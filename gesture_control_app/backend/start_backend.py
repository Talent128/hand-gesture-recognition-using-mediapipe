#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
带详细错误处理的后端启动脚本
"""

import sys
import os
import traceback

# 添加项目根目录到系统路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)

print("=" * 60)
print("手势控制后端启动中...")
print("=" * 60)
print(f"项目根目录: {project_root}")
print(f"Python版本: {sys.version}")
print()

# 检查依赖
print("[1/6] 检查依赖...")
try:
    import flask
    print(f"  ✓ Flask {flask.__version__}")
except ImportError as e:
    print(f"  ✗ Flask未安装: {e}")
    sys.exit(1)

try:
    import cv2
    print(f"  ✓ OpenCV {cv2.__version__}")
except ImportError as e:
    print(f"  ✗ OpenCV未安装: {e}")
    sys.exit(1)

try:
    import mediapipe
    print(f"  ✓ MediaPipe {mediapipe.__version__}")
except ImportError as e:
    print(f"  ✗ MediaPipe未安装: {e}")
    sys.exit(1)

try:
    import tensorflow
    print(f"  ✓ TensorFlow {tensorflow.__version__}")
except ImportError as e:
    print(f"  ✗ TensorFlow未安装: {e}")
    sys.exit(1)

try:
    from flask_cors import CORS
    print(f"  ✓ Flask-CORS")
except ImportError as e:
    print(f"  ✗ Flask-CORS未安装: {e}")
    sys.exit(1)

print()

# 检查模型文件
print("[2/6] 检查模型文件...")
static_model = os.path.join(project_root, 'model/keypoint_classifier/static_gesture_model/avazahedi/keypoint_classifier.tflite')
dynamic_model = os.path.join(project_root, 'model/point_history_classifier/dynamic_gesture_model/NUM_CLASSES_7/point_history_classifier.tflite')

if os.path.exists(static_model):
    print(f"  ✓ 静态手势模型: {os.path.basename(static_model)}")
else:
    print(f"  ✗ 静态手势模型不存在: {static_model}")
    sys.exit(1)

if os.path.exists(dynamic_model):
    print(f"  ✓ 动态手势模型: {os.path.basename(dynamic_model)}")
else:
    print(f"  ✗ 动态手势模型不存在: {dynamic_model}")
    sys.exit(1)

print()

# 检查标签文件
print("[3/6] 检查标签文件...")
static_label = os.path.join(project_root, 'model/keypoint_classifier/static_gesture_model/avazahedi/keypoint_classifier_label.csv')
dynamic_label = os.path.join(project_root, 'model/point_history_classifier/dynamic_gesture_model/NUM_CLASSES_7/point_history_classifier_label.csv')

if os.path.exists(static_label):
    print(f"  ✓ 静态手势标签")
else:
    print(f"  ✗ 静态手势标签不存在")
    sys.exit(1)

if os.path.exists(dynamic_label):
    print(f"  ✓ 动态手势标签")
else:
    print(f"  ✗ 动态手势标签不存在")
    sys.exit(1)

print()

# 初始化手势识别服务
print("[4/6] 初始化手势识别服务...")
try:
    from gesture_control_app.backend.gesture_service import GestureRecognitionService
    gesture_service = GestureRecognitionService()
    print("  ✓ 手势识别服务初始化成功")
except Exception as e:
    print(f"  ✗ 手势识别服务初始化失败:")
    print(f"     错误: {e}")
    traceback.print_exc()
    sys.exit(1)

print()

# 初始化配置管理器
print("[5/6] 初始化配置管理器...")
try:
    from gesture_control_app.backend.config_manager import ConfigManager
    config_manager = ConfigManager()
    print("  ✓ 配置管理器初始化成功")
except Exception as e:
    print(f"  ✗ 配置管理器初始化失败:")
    print(f"     错误: {e}")
    traceback.print_exc()
    sys.exit(1)

print()

# 启动Flask应用
print("[6/6] 启动Flask应用...")
try:
    from flask import Flask, request, jsonify, send_from_directory
    from flask_cors import CORS
    import cv2 as cv
    import numpy as np
    import base64
    from werkzeug.utils import secure_filename
    
    app = Flask(__name__)
    CORS(app)
    
    # 配置上传文件
    UPLOAD_FOLDER = os.path.join(project_root, 'assets')
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov', 'webm'}
    ALLOWED_PPT_EXTENSIONS = {'pptx', 'ppt', 'pdf'}
    app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024
    
    def allowed_file(filename, allowed_extensions):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'ok', 'message': '服务运行正常'})
    
    @app.route('/api/gesture/recognize', methods=['POST'])
    def recognize_gesture():
        try:
            data = request.json
            image_data = data.get('image', '')
            
            image_bytes = base64.b64decode(image_data.split(',')[1] if ',' in image_data else image_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv.imdecode(nparr, cv.IMREAD_COLOR)
            
            if image is None:
                return jsonify({'error': '无效的图像数据'}), 400
            
            result = gesture_service.process_frame(image)
            
            if data.get('draw_landmarks', False) and result['hand_detected']:
                annotated_image = image.copy()
                annotated_image = gesture_service.draw_landmarks_on_image(
                    annotated_image, result['landmarks']
                )
                _, buffer = cv.imencode('.jpg', annotated_image)
                image_base64 = base64.b64encode(buffer).decode('utf-8')
                result['annotated_image'] = f"data:image/jpeg;base64,{image_base64}"
            
            return jsonify(result)
        
        except Exception as e:
            print(f"手势识别错误: {e}")
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/config', methods=['GET'])
    def get_config():
        module = request.args.get('module')
        config = config_manager.get_config(module)
        return jsonify(config)
    
    @app.route('/api/config', methods=['POST'])
    def update_config():
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
        try:
            data = request.json
            module = data.get('module')
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
        try:
            return send_from_directory(UPLOAD_FOLDER, filename)
        except Exception as e:
            return jsonify({'error': f'文件不存在: {str(e)}'}), 404
    
    # 确保必要的目录存在
    os.makedirs(os.path.join(UPLOAD_FOLDER, 'videos'), exist_ok=True)
    os.makedirs(os.path.join(UPLOAD_FOLDER, 'presentations'), exist_ok=True)
    
    print("  ✓ Flask应用初始化成功")
    print()
    print("=" * 60)
    print("✓ 所有检查通过！")
    print("=" * 60)
    print()
    print("后端服务启动地址:")
    print("  • http://localhost:5000")
    print("  • http://127.0.0.1:5000")
    print()
    print("健康检查: http://localhost:5000/api/health")
    print()
    print("按 Ctrl+C 停止服务")
    print("=" * 60)
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=False)

except Exception as e:
    print(f"  ✗ Flask应用启动失败:")
    print(f"     错误: {e}")
    traceback.print_exc()
    sys.exit(1)

