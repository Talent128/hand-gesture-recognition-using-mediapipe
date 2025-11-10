#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
==========================================
关键点手势分类器模块
==========================================
功能：基于手部21个关键点坐标进行静态手势识别
使用TensorFlow Lite模型进行推理
"""

import numpy as np
import tensorflow as tf


class KeyPointClassifier(object):
    """
    关键点手势分类器
    
    该类封装了TensorFlow Lite模型的加载和推理过程
    用于识别静态手势（如：张开手掌、握拳、指向等）
    
    属性:
        interpreter: TFLite解释器对象
        input_details: 输入张量的元信息
        output_details: 输出张量的元信息
    """
    
    def __init__(
        self,
        model_path='model/keypoint_classifier/keypoint_classifier.tflite',      # 默认读取的 TFLite 静态手势模型路径
        num_threads=1,      # 默认使用的推理线程数量（单线程推理）
    ):
        """
        初始化关键点手势分类器
        
        参数:
            model_path (str): TFLite模型文件路径
            num_threads (int): 推理使用的线程数量，默认为1
        """
        # 构建 TFLite 解释器实例
        # TFLite是轻量级推理引擎，适合移动端和嵌入式设备
        self.interpreter = tf.lite.Interpreter(
            model_path=model_path,
            num_threads=num_threads,
        )

        # 为解释器分配输入与输出张量缓冲区
        # 必须在推理前调用此方法
        self.interpreter.allocate_tensors()
        
        # 缓存输入张量的元信息以便后续写入
        # 包含：索引、形状、数据类型等信息
        self.input_details = self.interpreter.get_input_details()
        
        # 缓存输出张量的元信息以便后续读取
        self.output_details = self.interpreter.get_output_details()
    

    def __call__(       
        self,
        landmark_list,          # 接收预处理后的关键点坐标列表（42维向量）
    ):
        """
        执行手势分类推理
        
        参数:
            landmark_list (list): 预处理后的关键点坐标列表
                               包含42个元素（21个关键点 × 2个坐标）
                               已经过相对坐标转换和归一化处理
        
        返回:
            int: 预测的手势类别编号（0, 1, 2, ...）
        """
        # 取出单个输入张量在解释器中的索引
        input_details_tensor_index = self.input_details[0]['index']
        
        # 将预处理数据写入模型输入
        # 需要转换为float32类型的numpy数组，并添加batch维度
        self.interpreter.set_tensor(
            input_details_tensor_index,
            np.array([landmark_list], dtype=np.float32),
        )

        # 执行一次前向推理
        # 这是模型计算的核心步骤
        self.interpreter.invoke()

        # 取得输出张量对应的索引
        output_details_tensor_index = self.output_details[0]['index']

        # 从解释器中读取推理结果向量
        # 结果是各类别的概率分布（softmax输出）
        result = self.interpreter.get_tensor(output_details_tensor_index)

        # 找到概率最大的类别索引作为最终手势结果
        # np.argmax返回最大值的索引
        result_index = np.argmax(np.squeeze(result))

        return result_index  # 返回预测到的手势类别编号
