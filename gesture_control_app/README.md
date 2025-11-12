# 手势控制系统

基于MediaPipe和深度学习的实时手势识别系统，支持通过手势控制PPT演示和视频播放。

## 功能特点

- 🎯 实时手势识别：支持8种静态手势和6种动态手势
- 📊 PPT控制：手势控制幻灯片翻页、跳转等操作
- 🎬 视频控制：手势控制视频播放、暂停、进度、音量等
- ⚙️ 灵活配置：自定义手势到操作的映射关系
- 🎨 美观界面：现代化Vue3界面，响应式设计
- 🔧 前后端分离：Flask后端API + Vue3前端

## 系统架构

```
gesture_control_app/
├── backend/              # 后端服务
│   ├── app.py           # Flask API主程序
│   ├── gesture_service.py  # 手势识别服务
│   └── config_manager.py   # 配置管理
├── frontend/             # 前端应用
│   └── src/
│       ├── components/   # Vue组件
│       ├── views/        # 页面视图
│       └── router/       # 路由配置
└── config/              # 配置文件
```

## 环境要求

- Python 3.8+
- Node.js 16+
- Conda（推荐）
- 摄像头设备

## 快速开始

### 方式一：使用启动脚本（推荐）

**Windows系统：**
```bash
.\run.bat
```

**Linux/Mac系统：**
```bash
chmod +x run.sh
./run.sh
```

启动脚本会自动：
1. 检测并创建conda环境（handGR）
2. 安装前后端依赖
3. 启动后端和前端服务

### 方式二：手动启动

#### 1. 创建并激活conda环境

```bash
# 创建环境
conda create -n handGR python=3.9

# 激活环境
conda activate handGR
```

#### 2. 安装后端依赖

```bash
# 安装项目原有依赖
pip install -r requirements.txt

# 安装后端额外依赖
pip install -r gesture_control_app/backend/requirements-backend.txt
```

#### 3. 安装前端依赖

```bash
cd gesture_control_app/frontend
npm install
```

#### 4. 启动服务

**启动后端（Terminal 1）：**
```bash
conda activate handGR
cd gesture_control_app/backend
python app.py
```

**启动前端（Terminal 2）：**
```bash
cd gesture_control_app/frontend
npm run dev
```

## 访问应用

- 前端界面：http://localhost:3000
- 后端API：http://localhost:5000

## 使用指南

### 1. PPT控制

1. 进入"PPT控制"页面
2. 上传或选择PPT文件（推荐PDF格式）
3. 点击"启动摄像头"
4. 对着摄像头做出手势即可控制PPT

**默认手势映射：**
- 👎 Thumbs Down → 下一页
- 👍 Thumbs Up → 上一页
- ✋ Open → 第一页
- ✊ Close → 最后一页
- ⬆️ Move Up → 向上滚动
- ⬇️ Move Down → 向下滚动

### 2. 视频控制

1. 进入"视频控制"页面
2. 上传或选择视频文件
3. 点击"启动摄像头"
4. 对着摄像头做出手势即可控制视频

**默认手势映射：**
- ✋ Open → 播放
- ✊ Close → 暂停
- 👌 OK → 重新开始
- ✌️ Peace → 全屏
- 👍 Thumbs Up → 音量+10%
- 👎 Thumbs Down → 音量-10%
- ⬅️ Move Left → 后退10秒
- ➡️ Move Right → 前进10秒
- 🔄 Clockwise → 加速播放
- 🔃 Counter Clockwise → 减速播放

### 3. 自定义配置

1. 进入"系统设置"页面
2. 选择"PPT控制配置"或"视频控制配置"
3. 修改手势映射或键盘快捷键
4. 点击"保存配置"

## 支持的手势

### 静态手势
- Open（张开手掌）
- Close（握拳）
- Pointer（食指指向）
- OK（OK手势）
- Peace（V字手势）
- Thumbs Up（大拇指向上）
- Thumbs Down（大拇指向下）

### 动态手势
- Move Up（向上移动）
- Move Down（向下移动）
- Move Left（向左移动）
- Move Right（向右移动）
- Clockwise（顺时针旋转）
- Counter Clockwise（逆时针旋转）

## 技术栈

### 后端
- Flask - Web框架
- MediaPipe - 手部关键点检测
- TensorFlow Lite - 手势分类模型
- OpenCV - 图像处理

### 前端
- Vue 3 - 渐进式框架
- Element Plus - UI组件库
- Axios - HTTP客户端
- Vite - 构建工具

## 常见问题

### Q: 摄像头无法启动？
A: 请检查浏览器是否授予摄像头权限，确保没有其他程序占用摄像头。

### Q: 手势识别不准确？
A: 确保光线充足，手部清晰可见，与摄像头保持适当距离（40-80cm）。

### Q: 无法上传PPT？
A: 建议将PPT转换为PDF格式上传，浏览器对PDF的兼容性更好。

### Q: 配置修改后不生效？
A: 确保点击了"保存配置"按钮，必要时刷新页面。

## 开发说明

详细的系统架构和开发文档请参阅 `docs/` 目录：
- [系统架构文档](docs/system_architecture.md)
- [后端API文档](docs/backend_api.md)
- [前端组件文档](docs/frontend_components.md)

## 许可证

本项目基于原有的手势识别项目扩展开发，保留原有项目的许可证。

## 贡献

欢迎提交Issue和Pull Request！

