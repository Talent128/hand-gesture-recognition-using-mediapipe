#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
==========================================
手势控制后端API服务
==========================================
功能：提供RESTful API接口，处理手势识别、文件上传、配置管理等
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import cv2 as cv
import numpy as np
import base64
import os
import sys
from werkzeug.utils import secure_filename

# 添加项目根目录到系统路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)

from gesture_control_app.backend.gesture_service import GestureRecognitionService
from gesture_control_app.backend.config_manager import ConfigManager

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置上传文件
UPLOAD_FOLDER = os.path.join(project_root, 'assets')
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov', 'webm'}
ALLOWED_PPT_EXTENSIONS = {'pptx', 'ppt', 'pdf'}
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB

# 初始化服务
gesture_service = GestureRecognitionService()
config_manager = ConfigManager()


def allowed_file(filename, allowed_extensions):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({'status': 'ok', 'message': '服务运行正常'})


@app.route('/api/gesture/recognize', methods=['POST'])
def recognize_gesture():
    """
    手势识别接口
    接收base64编码的图像，返回识别结果
    """
    try:
        data = request.json
        image_data = data.get('image', '')
        
        # 解码base64图像
        image_bytes = base64.b64decode(image_data.split(',')[1] if ',' in image_data else image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv.imdecode(nparr, cv.IMREAD_COLOR)
        
        if image is None:
            return jsonify({'error': '无效的图像数据'}), 400
        
        # 处理图像并识别手势
        result = gesture_service.process_frame(image)
        
        # 如果需要返回带关键点的图像
        if data.get('draw_landmarks', False) and result['hand_detected']:
            annotated_image = image.copy()
            annotated_image = gesture_service.draw_landmarks_on_image(
                annotated_image, result['landmarks']
            )
            
            # 编码为base64
            _, buffer = cv.imencode('.jpg', annotated_image)
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            result['annotated_image'] = f"data:image/jpeg;base64,{image_base64}"
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/config', methods=['GET'])
def get_config():
    """获取配置"""
    module = request.args.get('module')
    config = config_manager.get_config(module)
    return jsonify(config)


@app.route('/api/config', methods=['POST'])
def update_config():
    """更新配置"""
    try:
        data = request.json
        module = data.get('module')
        config_data = data.get('config')
        
        if not module or not config_data:
            return jsonify({'error': '缺少必要参数'}), 400
        
        success = config_manager.update_config(module, config_data)
        
        if success:
            return jsonify({'message': '配置更新成功', 'config': config_manager.get_config(module)})
        else:
            return jsonify({'error': '配置更新失败'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/config/reset', methods=['POST'])
def reset_config():
    """重置配置为默认值"""
    try:
        data = request.json
        module = data.get('module')
        
        success = config_manager.reset_config(module)
        
        if success:
            return jsonify({'message': '配置重置成功', 'config': config_manager.get_config(module)})
        else:
            return jsonify({'error': '配置重置失败'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/gesture/action', methods=['POST'])
def get_gesture_action():
    """
    获取手势对应的操作
    """
    try:
        data = request.json
        module = data.get('module')  # 'ppt' 或 'video'
        gesture_name = data.get('gesture')
        
        if not module or not gesture_name:
            return jsonify({'error': '缺少必要参数'}), 400
        
        action = config_manager.get_action_for_gesture(module, gesture_name)
        
        if action:
            keyboard_shortcut = config_manager.get_keyboard_shortcut(module, action)
            return jsonify({
                'gesture': gesture_name,
                'action': action,
                'keyboard_shortcut': keyboard_shortcut
            })
        else:
            return jsonify({'gesture': gesture_name, 'action': None, 'keyboard_shortcut': None})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload/video', methods=['POST'])
def upload_video():
    """上传视频文件"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400
        
        if file and allowed_file(file.filename, ALLOWED_VIDEO_EXTENSIONS):
            filename = secure_filename(file.filename)
            video_folder = os.path.join(UPLOAD_FOLDER, 'videos')
            os.makedirs(video_folder, exist_ok=True)
            
            file_path = os.path.join(video_folder, filename)
            file.save(file_path)
            
            return jsonify({
                'message': '视频上传成功',
                'filename': filename,
                'path': f'/assets/videos/{filename}'
            })
        else:
            return jsonify({'error': '不支持的文件类型'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload/ppt', methods=['POST'])
def upload_ppt():
    """上传PPT文件"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400
        
        if file and allowed_file(file.filename, ALLOWED_PPT_EXTENSIONS):
            filename = secure_filename(file.filename)
            ppt_folder = os.path.join(UPLOAD_FOLDER, 'presentations')
            os.makedirs(ppt_folder, exist_ok=True)
            
            file_path = os.path.join(ppt_folder, filename)
            file.save(file_path)
            
            return jsonify({
                'message': 'PPT上传成功',
                'filename': filename,
                'path': f'/assets/presentations/{filename}'
            })
        else:
            return jsonify({'error': '不支持的文件类型'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/files/<file_type>', methods=['GET'])
def list_files(file_type):
    """列出文件"""
    try:
        if file_type == 'videos':
            folder = os.path.join(UPLOAD_FOLDER, 'videos')
            extensions = ALLOWED_VIDEO_EXTENSIONS
        elif file_type == 'presentations':
            folder = os.path.join(UPLOAD_FOLDER, 'presentations')
            extensions = ALLOWED_PPT_EXTENSIONS
        else:
            return jsonify({'error': '无效的文件类型'}), 400
        
        if not os.path.exists(folder):
            return jsonify({'files': []})
        
        files = []
        for filename in os.listdir(folder):
            if allowed_file(filename, extensions):
                files.append({
                    'filename': filename,
                    'path': f'/assets/{file_type}/{filename}'
                })
        
        return jsonify({'files': files})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """提供静态资源"""
    try:
        return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        return jsonify({'error': f'文件不存在: {str(e)}'}), 404


if __name__ == '__main__':
    # 确保必要的目录存在
    os.makedirs(os.path.join(UPLOAD_FOLDER, 'videos'), exist_ok=True)
    os.makedirs(os.path.join(UPLOAD_FOLDER, 'presentations'), exist_ok=True)
    
    print("=" * 50)
    print("手势控制后端API服务启动中...")
    print(f"项目根目录: {project_root}")
    print(f"上传文件夹: {UPLOAD_FOLDER}")
    print("API服务地址: http://localhost:5000")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)

