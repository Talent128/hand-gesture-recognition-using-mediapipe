#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
==========================================
手势识别服务模块
==========================================
功能：封装手势识别逻辑，提供统一的识别接口
"""

import cv2 as cv
import numpy as np
import mediapipe as mp
from collections import deque, Counter
import copy
import itertools
import sys
import os

# 添加项目根目录到系统路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from model import KeyPointClassifier, PointHistoryClassifier


class GestureRecognitionService:
    """手势识别服务类"""
    
    def __init__(self, static_model_path=None, dynamic_model_path=None):
        """
        初始化手势识别服务
        
        Args:
            static_model_path: 静态手势模型路径
            dynamic_model_path: 动态手势模型路径
        """
        # 获取项目根目录（向上两级）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, '../..'))
        
        # 初始化MediaPipe Hands（优化参数以提高稳定性）
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,  # 视频流模式，启用tracking
            max_num_hands=1,
            min_detection_confidence=0.7,  # 检测置信度
            min_tracking_confidence=0.5,   
            model_complexity=1,             # 模型复杂度：1为默认，平衡速度和准确度
        )
        
        # 加载分类器模型（使用绝对路径）
        if static_model_path is None:
            static_model_path = os.path.join(project_root, 'model/keypoint_classifier/static_gesture_model/avazahedi/keypoint_classifier.tflite')
        if dynamic_model_path is None:
            dynamic_model_path = os.path.join(project_root, 'model/point_history_classifier/dynamic_gesture_model/NUM_CLASSES_7/point_history_classifier.tflite')
        
        self.keypoint_classifier = KeyPointClassifier(model_path=static_model_path)
        self.point_history_classifier = PointHistoryClassifier(model_path=dynamic_model_path)
        
        # 加载标签（使用绝对路径）
        static_label_path = os.path.join(project_root, 'model/keypoint_classifier/static_gesture_model/avazahedi/keypoint_classifier_label.csv')
        dynamic_label_path = os.path.join(project_root, 'model/point_history_classifier/dynamic_gesture_model/NUM_CLASSES_7/point_history_classifier_label.csv')
        
        self.static_labels = self._load_labels(static_label_path)
        self.dynamic_labels = self._load_labels(dynamic_label_path)
        
        # 初始化历史记录
        self.history_length = 16
        self.point_history = deque(maxlen=self.history_length)  # 轨迹点历史
        self.static_gesture_history = deque(maxlen=self.history_length)  # 静态手势ID历史
        self.dynamic_gesture_history = deque(maxlen=self.history_length)  # 动态手势ID历史
        
        # 关键点平滑：使用指数移动平均（EMA）- 更低延迟，更快响应
        self.prev_landmarks = None  # 前一帧的关键点
        self.ema_alpha = 0.5  # EMA平滑系数：0.5平衡平滑度和响应速度
    
    def _load_labels(self, label_path):
        """加载标签文件"""
        with open(label_path, encoding='utf-8-sig') as f:
            labels = [line.strip() for line in f if line.strip()]
        return labels
    
    def process_frame(self, image):
        """
        处理单帧图像，返回手势识别结果
        
        Args:
            image: BGR格式的图像（前端已经翻转，无需再flip）
        
        Returns:
            dict: 包含识别结果的字典
        """
        # 转换图像格式（前端已经做了flip，这里直接处理）
        image_rgb = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False
        results = self.hands.process(image_rgb)
        image_rgb.flags.writeable = True
        
        response = {
            'hand_detected': False,
            'static_gesture': None,
            'static_gesture_id': -1,
            'dynamic_gesture': None,
            'dynamic_gesture_id': -1,
            'landmarks': None,
            'bounding_rect': None
        }
        
        if results.multi_hand_landmarks is not None:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                                  results.multi_handedness):
                # 计算边界框
                brect = self._calc_bounding_rect(image, hand_landmarks)
                
                # 计算关键点
                landmark_list = self._calc_landmark_list(image, hand_landmarks)
                
                # 平滑关键点坐标（减少抖动）
                landmark_list = self._smooth_landmarks(landmark_list)
                
                # 预处理
                pre_processed_landmark = self._pre_process_landmark(landmark_list)
                pre_processed_point_history = self._pre_process_point_history(
                    image, self.point_history)
                
                # 静态手势识别
                static_id = self.keypoint_classifier(pre_processed_landmark)
                # 将当前帧的静态手势ID加入历史缓冲区
                self.static_gesture_history.append(static_id)
                # 使用历史缓冲区中出现最多的ID作为平滑后的结果
                if len(self.static_gesture_history) > 0:
                    most_common_static_id = Counter(self.static_gesture_history).most_common()[0][0]
                    static_gesture = self.static_labels[most_common_static_id] if most_common_static_id < len(self.static_labels) else "Unknown"
                else:
                    static_gesture = self.static_labels[static_id] if static_id < len(self.static_labels) else "Unknown"
                
                # 更新轨迹历史（仅在Pointer手势时记录）- 使用原始static_id而不是平滑后的
                if static_id == 2:  # Pointer
                    self.point_history.append(landmark_list[8])  # 食指指尖
                else:
                    self.point_history.append([0, 0])
                
                # 动态手势识别
                dynamic_id = 0
                if len(pre_processed_point_history) == (self.history_length * 2):
                    dynamic_id = self.point_history_classifier(pre_processed_point_history)
                
                # 将当前帧的动态手势ID加入历史缓冲区
                self.dynamic_gesture_history.append(dynamic_id)
                # 使用历史缓冲区中出现最多的ID作为平滑后的结果（参照app.py line 158-159）
                most_common_dynamic_id = Counter(self.dynamic_gesture_history).most_common()[0][0]
                dynamic_gesture = self.dynamic_labels[most_common_dynamic_id] if most_common_dynamic_id < len(self.dynamic_labels) else "Unknown"
                
                response = {
                    'hand_detected': True,
                    'static_gesture': static_gesture,
                    'static_gesture_id': int(static_id),
                    'dynamic_gesture': dynamic_gesture,
                    'dynamic_gesture_id': int(most_common_dynamic_id),
                    'landmarks': landmark_list,
                    'bounding_rect': brect,
                    'handedness': handedness.classification[0].label
                }
                break  # 只处理第一只检测到的手
        else:
            self.point_history.append([0, 0])
        
        return response
    
    def draw_landmarks_on_image(self, image, landmarks):
        """在图像上绘制手部关键点"""
        if landmarks is None or len(landmarks) == 0:
            return image
        
        landmark_point = landmarks
        
        # 绘制连接线
        connections = [
            # 拇指
            (2, 3), (3, 4),
            # 食指
            (5, 6), (6, 7), (7, 8),
            # 中指
            (9, 10), (10, 11), (11, 12),
            # 无名指
            (13, 14), (14, 15), (15, 16),
            # 小指
            (17, 18), (18, 19), (19, 20),
            # 手掌
            (0, 1), (1, 2), (2, 5), (5, 9), (9, 13), (13, 17), (17, 0)
        ]
        
        for connection in connections:
            start_idx, end_idx = connection
            if start_idx < len(landmark_point) and end_idx < len(landmark_point):
                cv.line(image, tuple(landmark_point[start_idx]), 
                       tuple(landmark_point[end_idx]), (0, 0, 0), 6)
                cv.line(image, tuple(landmark_point[start_idx]), 
                       tuple(landmark_point[end_idx]), (255, 255, 255), 2)
        
        # 绘制关键点
        for index, landmark in enumerate(landmark_point):
            if index in [4, 8, 12, 16, 20]:  # 指尖
                cv.circle(image, tuple(landmark), 8, (255, 255, 255), -1)
                cv.circle(image, tuple(landmark), 8, (0, 0, 0), 1)
            else:
                cv.circle(image, tuple(landmark), 5, (255, 255, 255), -1)
                cv.circle(image, tuple(landmark), 5, (0, 0, 0), 1)
        
        return image
    
    def _calc_bounding_rect(self, image, landmarks):
        """计算手部边界框"""
        image_width, image_height = image.shape[1], image.shape[0]
        landmark_array = np.empty((0, 2), int)
        
        for landmark in landmarks.landmark:
            landmark_x = min(int(landmark.x * image_width), image_width - 1)
            landmark_y = min(int(landmark.y * image_height), image_height - 1)
            landmark_point = [np.array((landmark_x, landmark_y))]
            landmark_array = np.append(landmark_array, landmark_point, axis=0)
        
        x, y, w, h = cv.boundingRect(landmark_array)
        return [x, y, x + w, y + h]
    
    def _calc_landmark_list(self, image, landmarks):
        """计算关键点坐标列表"""
        image_width, image_height = image.shape[1], image.shape[0]
        landmark_point = []
        
        for landmark in landmarks.landmark:
            landmark_x = min(int(landmark.x * image_width), image_width - 1)
            landmark_y = min(int(landmark.y * image_height), image_height - 1)
            landmark_point.append([landmark_x, landmark_y])
        
        return landmark_point
    
    def _smooth_landmarks(self, landmark_list):
        """
        使用指数移动平均（EMA）平滑关键点坐标，减少抖动且延迟更低
        
        公式：smoothed = alpha * current + (1 - alpha) * previous
        - alpha=1: 无平滑，完全跟随当前值
        - alpha=0: 完全平滑，不响应当前值
        - alpha=0.5: 平衡点
        
        Args:
            landmark_list: 当前帧的关键点列表 [[x1,y1], [x2,y2], ...]
        
        Returns:
            平滑后的关键点列表
        """
        # 第一帧：直接使用当前值
        if self.prev_landmarks is None:
            self.prev_landmarks = landmark_list
            return landmark_list
        
        # EMA平滑
        smoothed_landmarks = []
        for point_idx in range(len(landmark_list)):
            curr_x, curr_y = landmark_list[point_idx]
            prev_x, prev_y = self.prev_landmarks[point_idx]
            
            # 指数移动平均
            smooth_x = int(self.ema_alpha * curr_x + (1 - self.ema_alpha) * prev_x)
            smooth_y = int(self.ema_alpha * curr_y + (1 - self.ema_alpha) * prev_y)
            
            smoothed_landmarks.append([smooth_x, smooth_y])
        
        # 更新前一帧
        self.prev_landmarks = smoothed_landmarks
        
        return smoothed_landmarks
    
    def _pre_process_landmark(self, landmark_list):
        """预处理关键点坐标"""
        temp_landmark_list = copy.deepcopy(landmark_list)
        
        # 转换为相对坐标
        base_x, base_y = 0, 0
        for index, landmark_point in enumerate(temp_landmark_list):
            if index == 0:
                base_x, base_y = landmark_point[0], landmark_point[1]
            
            temp_landmark_list[index][0] = temp_landmark_list[index][0] - base_x
            temp_landmark_list[index][1] = temp_landmark_list[index][1] - base_y
        
        # 展平为一维列表
        temp_landmark_list = list(itertools.chain.from_iterable(temp_landmark_list))
        
        # 归一化
        max_value = max(list(map(abs, temp_landmark_list)))
        
        def normalize_(n):
            return n / max_value if max_value != 0 else 0
        
        temp_landmark_list = list(map(normalize_, temp_landmark_list))
        
        return temp_landmark_list
    
    def _pre_process_point_history(self, image, point_history):
        """预处理轨迹历史"""
        image_width, image_height = image.shape[1], image.shape[0]
        temp_point_history = copy.deepcopy(point_history)
        
        # 转换为相对坐标
        base_x, base_y = 0, 0
        for index, point in enumerate(temp_point_history):
            if index == 0:
                base_x, base_y = point[0], point[1]
            
            temp_point_history[index][0] = (temp_point_history[index][0] - base_x) / image_width if image_width != 0 else 0
            temp_point_history[index][1] = (temp_point_history[index][1] - base_y) / image_height if image_height != 0 else 0
        
        # 展平为一维列表
        temp_point_history = list(itertools.chain.from_iterable(temp_point_history))
        
        return temp_point_history
    
    def reset_history(self):
        """重置历史记录"""
        self.point_history.clear()
        self.static_gesture_history.clear()
        self.dynamic_gesture_history.clear()
        self.prev_landmarks = None  # 重置EMA平滑状态

