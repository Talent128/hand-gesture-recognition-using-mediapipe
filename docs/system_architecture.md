# 手势控制系统架构文档

## 1. 系统概述

手势控制系统是一个基于深度学习和计算机视觉的实时手势识别应用，支持通过手势控制PPT演示和视频播放。系统采用前后端分离架构，前端使用Vue3实现交互界面，后端使用Flask提供RESTful API服务。

## 2. 系统架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                     用户浏览器                           │
│  ┌────────────────────────────────────────────────┐   │
│  │          Vue3 前端应用                          │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐    │   │
│  │  │ 摄像头组件│  │PPT控制器 │  │视频播放器│    │   │
│  │  └──────────┘  └──────────┘  └──────────┘    │   │
│  └────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                        ↕ HTTP/WebSocket
┌─────────────────────────────────────────────────────────┐
│                  Flask 后端服务                          │
│  ┌────────────────────────────────────────────────┐   │
│  │          API路由层                              │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐    │   │
│  │  │手势识别API│  │配置管理API│  │文件上传API│    │   │
│  │  └──────────┘  └──────────┘  └──────────┘    │   │
│  └────────────────────────────────────────────────┘   │
│  ┌────────────────────────────────────────────────┐   │
│  │          业务逻辑层                             │   │
│  │  ┌──────────┐  ┌──────────┐                  │   │
│  │  │手势识别服务│  │配置管理器│                  │   │
│  │  └──────────┘  └──────────┘                  │   │
│  └────────────────────────────────────────────────┘   │
│  ┌────────────────────────────────────────────────┐   │
│  │          核心引擎层                             │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐    │   │
│  │  │ MediaPipe │  │静态手势模型│  │动态手势模型│    │   │
│  │  └──────────┘  └──────────┘  └──────────┘    │   │
│  └────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 2.2 目录结构

```
hand-gesture-recognition-using-mediapipe/
├── gesture_control_app/          # 新增应用目录
│   ├── backend/                  # 后端服务
│   │   ├── app.py               # Flask主程序
│   │   ├── gesture_service.py   # 手势识别服务
│   │   ├── config_manager.py    # 配置管理
│   │   └── requirements-backend.txt
│   ├── frontend/                 # 前端应用
│   │   ├── src/
│   │   │   ├── components/      # Vue组件
│   │   │   │   └── CameraFeed.vue
│   │   │   ├── views/           # 页面视图
│   │   │   │   ├── Home.vue
│   │   │   │   ├── PPTControl.vue
│   │   │   │   ├── VideoControl.vue
│   │   │   │   └── Settings.vue
│   │   │   ├── router/          # 路由配置
│   │   │   ├── App.vue
│   │   │   └── main.js
│   │   ├── package.json
│   │   └── vite.config.js
│   ├── config/                   # 配置文件
│   │   └── gesture_mapping.json
│   ├── README.md
│   ├── run.bat                   # Windows启动脚本
│   └── run.sh                    # Linux/Mac启动脚本
├── model/                         # 原有模型目录
│   ├── keypoint_classifier/      # 静态手势分类器
│   └── point_history_classifier/ # 动态手势分类器
├── assets/                        # 资源文件
│   ├── presentations/            # PPT文件
│   └── videos/                   # 视频文件
├── docs/                          # 文档目录
├── app.py                         # 原有主程序（保留）
└── requirements.txt               # 原有依赖
```

## 3. 核心模块

### 3.1 后端模块

#### 3.1.1 手势识别服务 (gesture_service.py)

**功能：**
- 封装MediaPipe手部关键点检测
- 调用TensorFlow Lite模型进行手势分类
- 管理手势历史和轨迹

**核心类：**
```python
class GestureRecognitionService:
    - process_frame(image): 处理单帧图像，返回识别结果
    - draw_landmarks_on_image(image, landmarks): 绘制手部关键点
    - reset_history(): 重置历史记录
```

**识别流程：**
1. 接收BGR格式图像
2. MediaPipe检测手部21个关键点
3. 预处理关键点坐标（相对坐标+归一化）
4. 静态手势分类（基于关键点位置）
5. 动态手势分类（基于指尖轨迹）
6. 返回识别结果

#### 3.1.2 配置管理 (config_manager.py)

**功能：**
- 管理手势到操作的映射关系
- 管理键盘快捷键配置
- 支持配置的保存、读取和重置

**核心类：**
```python
class ConfigManager:
    - get_config(module): 获取配置
    - update_config(module, config_data): 更新配置
    - reset_config(module): 重置为默认配置
    - get_action_for_gesture(module, gesture_name): 获取手势对应操作
```

**配置结构：**
```json
{
  "ppt": {
    "gestures": {
      "Thumbs Down": "next_slide",
      "Thumbs Up": "prev_slide",
      ...
    },
    "keyboard_shortcuts": {
      "next_slide": "ArrowRight",
      "prev_slide": "ArrowLeft",
      ...
    }
  },
  "video": { ... }
}
```

#### 3.1.3 API路由 (app.py)

**主要接口：**

| 路由 | 方法 | 功能 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/gesture/recognize` | POST | 手势识别 |
| `/api/config` | GET/POST | 配置管理 |
| `/api/config/reset` | POST | 重置配置 |
| `/api/upload/video` | POST | 上传视频 |
| `/api/upload/ppt` | POST | 上传PPT |
| `/api/files/<type>` | GET | 列出文件 |

### 3.2 前端模块

#### 3.2.1 摄像头组件 (CameraFeed.vue)

**功能：**
- 访问用户摄像头
- 实时捕获视频帧
- 发送帧到后端进行手势识别
- 在画面上绘制手部关键点
- 显示识别结果

**关键方法：**
- `startCamera()`: 启动摄像头
- `stopCamera()`: 停止摄像头
- `processFrame()`: 处理视频帧
- `drawLandmarks()`: 绘制关键点

#### 3.2.2 PPT控制视图 (PPTControl.vue)

**功能：**
- 显示PPT内容（支持PDF格式）
- 响应手势进行翻页、跳转等操作
- 支持文件上传和选择
- 显示手势映射说明

**控制操作：**
- 下一页 / 上一页
- 第一页 / 最后一页
- 向上/向下滚动

#### 3.2.3 视频控制视图 (VideoControl.vue)

**功能：**
- 播放视频文件
- 响应手势进行播放控制
- 支持文件上传和选择
- 显示播放状态和信息

**控制操作：**
- 播放 / 暂停
- 重新开始
- 音量调节
- 进度调节
- 速度调节
- 全屏切换

#### 3.2.4 设置视图 (Settings.vue)

**功能：**
- 配置手势映射
- 配置键盘快捷键
- 查看系统信息
- 重置配置

## 4. 数据流

### 4.1 手势识别流程

```
用户手势 → 摄像头 → 视频帧 → Canvas
                              ↓
                          Base64编码
                              ↓
                     HTTP POST请求
                              ↓
                      后端API接收
                              ↓
                      图像解码
                              ↓
                   MediaPipe关键点检测
                              ↓
              ┌───────────────┴───────────────┐
              ↓                               ↓
        静态手势分类                      动态手势分类
      (KeyPointClassifier)          (PointHistoryClassifier)
              ↓                               ↓
              └───────────────┬───────────────┘
                              ↓
                        识别结果返回
                              ↓
                      前端接收并显示
                              ↓
                      查询手势映射
                              ↓
                      执行对应操作
```

### 4.2 配置管理流程

```
用户修改配置 → 前端表单 → HTTP POST → 后端接收
                                           ↓
                                      验证配置
                                           ↓
                                    保存到JSON文件
                                           ↓
                                      返回成功
                                           ↓
                                  前端更新显示
```

## 5. 技术选型

### 5.1 后端技术栈

- **Flask**: 轻量级Web框架，易于快速开发RESTful API
- **MediaPipe**: Google开源的机器学习框架，用于手部关键点检测
- **TensorFlow Lite**: 轻量级推理引擎，用于运行手势分类模型
- **OpenCV**: 计算机视觉库，用于图像处理
- **Flask-CORS**: 处理跨域请求

### 5.2 前端技术栈

- **Vue 3**: 渐进式JavaScript框架，组合式API
- **Element Plus**: 基于Vue 3的组件库，提供丰富的UI组件
- **Vite**: 新一代前端构建工具，快速开发体验
- **Axios**: HTTP客户端，用于API请求
- **Vue Router**: 官方路由管理器

## 6. 手势识别原理

### 6.1 静态手势识别

**输入：** 手部21个关键点的坐标

**处理步骤：**
1. 坐标归一化（相对于手腕位置）
2. 输入到神经网络模型
3. 输出各手势的概率分布
4. 选择概率最高的手势

**支持的手势：**
- Open（张开手掌）
- Close（握拳）
- Pointer（食指指向）
- OK（OK手势）
- Peace（V字手势）
- Thumbs Up（大拇指向上）
- Thumbs Down（大拇指向下）

### 6.2 动态手势识别

**输入：** 食指指尖16帧的轨迹坐标

**处理步骤：**
1. 记录食指指尖移动轨迹
2. 轨迹归一化
3. 输入到时序神经网络
4. 输出各动作的概率分布
5. 选择概率最高的动作

**支持的手势：**
- Move Up（向上移动）
- Move Down（向下移动）
- Move Left（向左移动）
- Move Right（向右移动）
- Clockwise（顺时针旋转）
- Counter Clockwise（逆时针旋转）

## 7. 扩展性设计

### 7.1 新增手势

1. 采集手势数据（使用原有的`app.py`）
2. 训练新模型（使用原有的notebook）
3. 替换模型文件
4. 更新标签文件
5. 在配置中添加新手势映射

### 7.2 新增控制对象

1. 在`config_manager.py`中添加新模块配置
2. 创建新的前端视图组件
3. 实现控制逻辑
4. 添加路由配置

### 7.3 新增操作

1. 在配置文件中定义新操作
2. 在视图组件中实现操作函数
3. 更新手势映射配置

## 8. 性能优化

### 8.1 前端优化

- 使用`requestAnimationFrame`控制帧率
- 适当降低发送到后端的图像质量
- 组件懒加载
- 防抖处理手势触发

### 8.2 后端优化

- TensorFlow Lite轻量级模型
- 单线程推理（可配置多线程）
- 图像预处理优化
- 缓存配置文件

## 9. 安全性考虑

- 文件上传大小限制（500MB）
- 文件类型白名单验证
- 文件名安全处理（secure_filename）
- CORS配置（可根据需要限制来源）

## 10. 部署建议

### 10.1 开发环境

- 使用提供的启动脚本
- 前后端分别运行在3000和5000端口
- 支持热重载

### 10.2 生产环境

**后端：**
- 使用Gunicorn或uWSGI作为WSGI服务器
- 配置Nginx反向代理
- 启用日志记录

**前端：**
- 执行`npm run build`构建生产版本
- 使用Nginx提供静态文件服务
- 配置代理到后端API

**示例Nginx配置：**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 前端静态文件
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # 后端API代理
    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # 资源文件
    location /assets {
        proxy_pass http://localhost:5000;
    }
}
```

## 11. 故障排查

### 11.1 常见问题

**问题：摄像头无法启动**
- 检查浏览器权限
- 确认没有其他程序占用摄像头
- 使用HTTPS协议（某些浏览器要求）

**问题：手势识别不准确**
- 确保光线充足
- 保持适当距离（40-80cm）
- 检查模型文件是否完整

**问题：配置修改不生效**
- 确认已点击保存按钮
- 检查配置文件权限
- 刷新页面

### 11.2 日志查看

**后端日志：**
```bash
# 查看Flask控制台输出
# 可在app.py中配置logging模块
```

**前端日志：**
```bash
# 浏览器控制台 (F12)
# 查看Network标签查看API请求
```

## 12. 未来改进方向

1. **WebSocket实时通信**：减少延迟，提高响应速度
2. **手势录制功能**：支持用户自定义手势
3. **多手势识别**：同时识别多只手
4. **移动端支持**：适配手机和平板
5. **性能监控**：添加FPS显示和性能统计
6. **离线支持**：PWA技术，支持离线使用

