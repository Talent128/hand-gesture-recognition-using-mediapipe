# 项目结构说明

## 完整目录结构

```
hand-gesture-recognition-using-mediapipe/
│
├── gesture_control_app/              # 【新增】手势控制应用主目录
│   ├── backend/                      # 后端服务
│   │   ├── app.py                   # Flask API主程序，提供RESTful接口
│   │   ├── gesture_service.py       # 手势识别服务，封装识别逻辑
│   │   ├── config_manager.py        # 配置管理器，管理手势映射配置
│   │   └── requirements-backend.txt # 后端额外依赖
│   │
│   ├── frontend/                     # 前端应用
│   │   ├── src/
│   │   │   ├── components/          # Vue组件
│   │   │   │   └── CameraFeed.vue  # 摄像头采集和手势识别显示组件
│   │   │   │
│   │   │   ├── views/               # 页面视图
│   │   │   │   ├── Home.vue        # 首页，功能介绍和导航
│   │   │   │   ├── PPTControl.vue  # PPT控制页面
│   │   │   │   ├── VideoControl.vue # 视频控制页面
│   │   │   │   └── Settings.vue    # 设置页面
│   │   │   │
│   │   │   ├── router/              # 路由配置
│   │   │   │   └── index.js        # Vue Router配置
│   │   │   │
│   │   │   ├── App.vue              # 根组件，布局和导航
│   │   │   └── main.js              # 入口文件
│   │   │
│   │   ├── index.html               # HTML模板
│   │   ├── package.json             # Node.js依赖配置
│   │   └── vite.config.js           # Vite构建配置
│   │
│   ├── config/                       # 配置文件目录
│   │   └── gesture_mapping.json    # 手势映射配置文件
│   │
│   ├── README.md                     # 应用使用说明
│   ├── .gitignore                    # Git忽略文件配置
│   ├── run.bat                       # Windows启动脚本
│   └── run.sh                        # Linux/Mac启动脚本
│
├── model/                             # 【原有】模型文件目录
│   ├── __init__.py                   # 模块初始化
│   │
│   ├── keypoint_classifier/          # 静态手势分类器
│   │   ├── keypoint_classifier.py   # 静态手势分类器类
│   │   ├── README.md                # 分类器说明
│   │   │
│   │   └── static_gesture_model/    # 静态手势模型集合
│   │       ├── avazahedi/           # 使用的模型（默认）
│   │       │   ├── keypoint_classifier.tflite      # TFLite模型文件
│   │       │   ├── keypoint_classifier.hdf5        # Keras模型文件
│   │       │   ├── keypoint_classifier_label.csv   # 手势标签
│   │       │   └── keypoint.csv                    # 训练数据
│   │       │
│   │       └── [其他贡献者模型]/     # 其他可选模型
│   │
│   └── point_history_classifier/     # 动态手势分类器
│       ├── point_history_classifier.py  # 动态手势分类器类
│       │
│       └── dynamic_gesture_model/    # 动态手势模型
│           └── NUM_CLASSES_7/       # 7类动态手势模型（使用中）
│               ├── point_history_classifier.tflite  # TFLite模型
│               ├── point_history_classifier.keras   # Keras模型
│               └── point_history_classifier_label.csv # 手势标签
│
├── utils/                             # 【原有】工具模块
│   ├── __init__.py
│   └── cvfpscalc.py                  # FPS计算工具
│
├── assets/                            # 【原有，已完善】资源文件
│   ├── presentations/                # PPT文件目录
│   │   ├── 11.pptx                  # 示例PPT
│   │   └── README.md                # 使用说明（已完善）
│   │
│   └── videos/                       # 视频文件目录
│       ├── movie.mp4                # 示例视频
│       └── README.md                # 使用说明（已完善）
│
├── docs/                              # 【新增】文档目录
│   ├── system_architecture.md       # 系统架构文档
│   ├── backend_api.md               # 后端API文档
│   ├── frontend_components.md       # 前端组件文档
│   ├── project_structure.md         # 项目结构说明（本文档）
│   └── quickstart.md                # 快速入门指南
│
├── app.py                             # 【原有】原始手势识别演示程序
├── collection_helper.py               # 【原有】数据采集辅助工具
├── keypoint_classification.ipynb     # 【原有】静态手势模型训练notebook
├── point_history_classification.ipynb # 【原有】动态手势模型训练notebook
├── requirements.txt                   # 【原有】Python依赖
├── CITATION.cff                       # 【原有】引用信息
└── 数据采集操作指南.md                # 【原有】数据采集说明

```

## 模块说明

### 1. gesture_control_app/ - 主应用目录

这是新增的手势控制应用，包含完整的前后端实现。

#### 1.1 backend/ - 后端服务

**作用：** 提供RESTful API服务，处理手势识别、配置管理、文件上传等功能。

**关键文件：**

- **app.py** (Flask主程序)
  - 定义API路由
  - 处理HTTP请求
  - 文件上传管理
  - CORS跨域配置
  
- **gesture_service.py** (手势识别服务)
  - 封装MediaPipe手部检测
  - 调用TFLite模型进行分类
  - 管理识别历史
  - 绘制关键点
  
- **config_manager.py** (配置管理)
  - 读写配置文件
  - 管理手势映射
  - 管理快捷键配置
  - 提供默认配置

#### 1.2 frontend/ - 前端应用

**作用：** Vue3单页应用，提供用户交互界面。

**目录结构：**

```
frontend/src/
├── components/        # 可复用组件
│   └── CameraFeed.vue    # 摄像头组件（核心）
│
├── views/            # 页面视图
│   ├── Home.vue          # 首页导航
│   ├── PPTControl.vue    # PPT控制
│   ├── VideoControl.vue  # 视频控制
│   └── Settings.vue      # 系统设置
│
├── router/           # 路由配置
└── App.vue           # 根组件
```

**关键组件：**

- **CameraFeed.vue**
  - 访问用户摄像头
  - 实时捕获并发送帧到后端
  - 显示识别结果
  - 绘制手部关键点
  
- **PPTControl.vue**
  - 显示PPT内容
  - 处理手势控制
  - 文件上传
  
- **VideoControl.vue**
  - 视频播放器
  - 手势控制实现
  - 播放状态管理
  
- **Settings.vue**
  - 配置界面
  - 手势映射设置
  - 快捷键配置

#### 1.3 config/ - 配置目录

**gesture_mapping.json**
- 存储手势到操作的映射
- 存储键盘快捷键配置
- 分为ppt和video两个模块

### 2. model/ - 模型目录（原有）

**作用：** 存放训练好的手势识别模型。

#### 2.1 keypoint_classifier/ - 静态手势识别

**工作原理：**
- 输入：21个手部关键点坐标
- 处理：相对坐标+归一化
- 输出：手势类别（Open, Close, OK等）

**使用的模型：** `static_gesture_model/avazahedi/`

#### 2.2 point_history_classifier/ - 动态手势识别

**工作原理：**
- 输入：16帧指尖轨迹
- 处理：时序分析
- 输出：运动手势（Move Up, Clockwise等）

**使用的模型：** `dynamic_gesture_model/NUM_CLASSES_7/`

### 3. assets/ - 资源文件（原有，已完善）

**presentations/** - PPT文件存储
- 支持PDF、PPTX、PPT格式
- 建议使用PDF格式

**videos/** - 视频文件存储
- 支持MP4、WebM、AVI等格式
- 建议使用MP4格式

### 4. docs/ - 文档目录（新增）

**文档列表：**
- `system_architecture.md` - 系统架构和技术选型
- `backend_api.md` - API接口文档
- `frontend_components.md` - 前端组件说明
- `project_structure.md` - 项目结构（本文档）
- `quickstart.md` - 快速入门指南

### 5. 原有文件

**app.py** - 原始演示程序
- 基于OpenCV的实时手势识别
- 用于测试和数据采集
- **不要修改，保留原有功能**

**Notebooks**
- `keypoint_classification.ipynb` - 训练静态手势模型
- `point_history_classification.ipynb` - 训练动态手势模型

## 数据流转

### 手势识别流程

```
用户 → 摄像头 → CameraFeed.vue → Base64编码 
     → HTTP POST /api/gesture/recognize 
     → gesture_service.py → MediaPipe检测 
     → 模型推理 → 返回结果 
     → 前端显示 → 查询配置 
     → 执行操作
```

### 配置管理流程

```
前端Settings.vue → HTTP POST /api/config 
     → config_manager.py → 保存JSON 
     → 返回成功 → 前端更新
```

### 文件上传流程

```
用户选择文件 → multipart/form-data 
     → HTTP POST /api/upload/* 
     → 验证文件类型 → 保存到assets/ 
     → 返回路径 → 前端更新列表
```

## 技术栈总结

### 后端
- **Flask** - Web框架
- **MediaPipe** - 手部检测
- **TensorFlow Lite** - 模型推理
- **OpenCV** - 图像处理
- **NumPy** - 数值计算

### 前端
- **Vue 3** - 前端框架
- **Element Plus** - UI组件库
- **Vite** - 构建工具
- **Axios** - HTTP客户端
- **Vue Router** - 路由管理

## 扩展指南

### 添加新手势

1. 使用`app.py`采集数据（按k进入采集模式）
2. 使用notebook训练模型
3. 替换`model/`中的模型文件
4. 更新标签文件
5. 在配置中添加映射

### 添加新功能页面

1. 在`frontend/src/views/`创建新组件
2. 在`router/index.js`添加路由
3. 在`App.vue`添加菜单项
4. 在`config_manager.py`添加配置模块
5. 实现控制逻辑

### 修改界面样式

1. 使用Element Plus主题定制
2. 修改组件的`<style>`部分
3. 遵循响应式设计原则

## 部署建议

### 开发环境
```bash
# 使用启动脚本
./gesture_control_app/run.bat    # Windows
./gesture_control_app/run.sh     # Linux/Mac
```

### 生产环境

**后端：**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 gesture_control_app.backend.app:app
```

**前端：**
```bash
cd gesture_control_app/frontend
npm run build
# 使用Nginx提供静态文件服务
```

## 依赖关系

```
gesture_control_app (新应用)
    ├── 依赖 model/ (原有模型)
    ├── 依赖 utils/ (原有工具)
    ├── 读写 assets/ (资源文件)
    └── 读写 config/ (配置文件)

原有 app.py
    └── 独立运行，不受新应用影响
```

## 文件大小说明

- 模型文件：约5-10MB
- 前端构建：约2-3MB（压缩后）
- 依赖包：约500MB（首次安装）

## 版本控制

建议`.gitignore`忽略：
- `node_modules/`
- `__pycache__/`
- `frontend/dist/`
- 上传的大文件（视频、PPT）
- 配置备份文件

## 性能考虑

- **后端**：单次识别约50-100ms
- **前端**：推荐帧率10-15 FPS
- **网络**：局域网延迟<20ms
- **资源**：CPU占用<30%，内存<500MB

## 维护建议

1. **定期备份**：配置文件和用户数据
2. **日志监控**：记录错误和异常
3. **性能优化**：监控响应时间
4. **安全更新**：及时更新依赖包
5. **文档同步**：代码修改后更新文档

## 贡献指南

如需为项目做贡献：
1. Fork项目
2. 创建特性分支
3. 提交代码
4. 发起Pull Request
5. 等待审核

## 许可证

遵循原项目许可证。

