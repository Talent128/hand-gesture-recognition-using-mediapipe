# 后端API文档

## API概述

后端提供RESTful API服务，默认运行在 `http://localhost:5000`

所有API响应格式为JSON，支持跨域请求（CORS）。

## 基础信息

- **Base URL**: `http://localhost:5000/api`
- **Content-Type**: `application/json`
- **编码**: UTF-8

## API端点

### 1. 健康检查

检查后端服务状态。

- **URL**: `/api/health`
- **方法**: `GET`
- **参数**: 无

**响应示例：**
```json
{
  "status": "ok",
  "message": "服务运行正常"
}
```

---

### 2. 手势识别

发送图像进行手势识别。

- **URL**: `/api/gesture/recognize`
- **方法**: `POST`
- **Content-Type**: `application/json`

**请求参数：**
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",  // Base64编码的图像
  "draw_landmarks": false  // 可选，是否返回绘制关键点的图像
}
```

**响应示例（检测到手部）：**
```json
{
  "hand_detected": true,
  "static_gesture": "Thumbs Up",
  "static_gesture_id": 5,
  "dynamic_gesture": "Stop",
  "dynamic_gesture_id": 0,
  "landmarks": [[x1, y1], [x2, y2], ...],  // 21个关键点坐标
  "bounding_rect": [x, y, x2, y2],
  "handedness": "Right"
}
```

**响应示例（未检测到手部）：**
```json
{
  "hand_detected": false,
  "static_gesture": null,
  "static_gesture_id": -1,
  "dynamic_gesture": null,
  "dynamic_gesture_id": -1,
  "landmarks": null,
  "bounding_rect": null
}
```

---

### 3. 获取配置

获取指定模块的配置。

- **URL**: `/api/config`
- **方法**: `GET`

**查询参数：**
- `module`: 模块名称（`ppt` 或 `video`），不传则返回全部配置

**请求示例：**
```
GET /api/config?module=ppt
```

**响应示例：**
```json
{
  "gestures": {
    "Thumbs Down": "next_slide",
    "Thumbs Up": "prev_slide",
    "Open": "first_slide",
    "Close": "last_slide",
    "Move Up": "scroll_up",
    "Move Down": "scroll_down"
  },
  "keyboard_shortcuts": {
    "next_slide": "ArrowRight",
    "prev_slide": "ArrowLeft",
    "first_slide": "Home",
    "last_slide": "End",
    "scroll_up": "PageUp",
    "scroll_down": "PageDown"
  }
}
```

---

### 4. 更新配置

更新指定模块的配置。

- **URL**: `/api/config`
- **方法**: `POST`
- **Content-Type**: `application/json`

**请求参数：**
```json
{
  "module": "ppt",  // 模块名称
  "config": {
    "gestures": {
      "Thumbs Down": "next_slide",
      ...
    },
    "keyboard_shortcuts": {
      "next_slide": "ArrowRight",
      ...
    }
  }
}
```

**响应示例：**
```json
{
  "message": "配置更新成功",
  "config": { ... }  // 更新后的配置
}
```

---

### 5. 重置配置

重置配置为默认值。

- **URL**: `/api/config/reset`
- **方法**: `POST`
- **Content-Type**: `application/json`

**请求参数：**
```json
{
  "module": "ppt"  // 模块名称，不传则重置全部
}
```

**响应示例：**
```json
{
  "message": "配置重置成功",
  "config": { ... }  // 重置后的配置
}
```

---

### 6. 获取手势对应操作

获取手势对应的操作和快捷键。

- **URL**: `/api/gesture/action`
- **方法**: `POST`
- **Content-Type**: `application/json`

**请求参数：**
```json
{
  "module": "video",  // 模块名称
  "gesture": "Open"   // 手势名称
}
```

**响应示例：**
```json
{
  "gesture": "Open",
  "action": "play",
  "keyboard_shortcut": "Space"
}
```

---

### 7. 上传视频

上传视频文件。

- **URL**: `/api/upload/video`
- **方法**: `POST`
- **Content-Type**: `multipart/form-data`

**请求参数：**
- `file`: 视频文件

**支持格式：** mp4, avi, mkv, mov, webm

**响应示例：**
```json
{
  "message": "视频上传成功",
  "filename": "movie.mp4",
  "path": "/assets/videos/movie.mp4"
}
```

---

### 8. 上传PPT

上传PPT文件。

- **URL**: `/api/upload/ppt`
- **方法**: `POST`
- **Content-Type**: `multipart/form-data`

**请求参数：**
- `file`: PPT文件

**支持格式：** pptx, ppt, pdf

**响应示例：**
```json
{
  "message": "PPT上传成功",
  "filename": "presentation.pdf",
  "path": "/assets/presentations/presentation.pdf"
}
```

---

### 9. 列出文件

列出指定类型的文件。

- **URL**: `/api/files/<file_type>`
- **方法**: `GET`

**路径参数：**
- `file_type`: 文件类型（`videos` 或 `presentations`）

**请求示例：**
```
GET /api/files/videos
```

**响应示例：**
```json
{
  "files": [
    {
      "filename": "movie.mp4",
      "path": "/assets/videos/movie.mp4"
    },
    {
      "filename": "demo.mp4",
      "path": "/assets/videos/demo.mp4"
    }
  ]
}
```

---

### 10. 访问资源文件

访问上传的资源文件。

- **URL**: `/assets/<path:filename>`
- **方法**: `GET`

**示例：**
```
GET /assets/videos/movie.mp4
GET /assets/presentations/11.pdf
```

---

## 错误响应

所有API在出错时返回以下格式：

```json
{
  "error": "错误信息描述"
}
```

**常见HTTP状态码：**
- `200`: 成功
- `400`: 请求参数错误
- `404`: 资源不存在
- `500`: 服务器内部错误

---

## 使用示例

### Python示例

```python
import requests
import base64

# 1. 健康检查
response = requests.get('http://localhost:5000/api/health')
print(response.json())

# 2. 手势识别
with open('hand_image.jpg', 'rb') as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')
    
response = requests.post(
    'http://localhost:5000/api/gesture/recognize',
    json={
        'image': f'data:image/jpeg;base64,{image_data}',
        'draw_landmarks': False
    }
)
print(response.json())

# 3. 获取配置
response = requests.get('http://localhost:5000/api/config?module=ppt')
print(response.json())

# 4. 上传文件
with open('video.mp4', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/api/upload/video',
        files={'file': f}
    )
print(response.json())
```

### JavaScript示例

```javascript
// 1. 健康检查
fetch('http://localhost:5000/api/health')
  .then(response => response.json())
  .then(data => console.log(data));

// 2. 手势识别
const canvas = document.getElementById('canvas');
const imageData = canvas.toDataURL('image/jpeg');

fetch('http://localhost:5000/api/gesture/recognize', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    image: imageData,
    draw_landmarks: false
  })
})
  .then(response => response.json())
  .then(data => console.log(data));

// 3. 获取配置
fetch('http://localhost:5000/api/config?module=video')
  .then(response => response.json())
  .then(data => console.log(data));

// 4. 上传文件
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:5000/api/upload/video', {
  method: 'POST',
  body: formData
})
  .then(response => response.json())
  .then(data => console.log(data));
```

---

## 性能建议

1. **图像质量**：建议使用JPEG格式，质量设置为0.8，平衡识别准确度和传输速度
2. **请求频率**：建议控制在10-15 FPS，避免过度请求
3. **文件大小**：单次上传文件不超过500MB
4. **并发请求**：后端使用Flask开发服务器，建议生产环境使用Gunicorn等WSGI服务器

---

## 安全性

1. **文件上传**：使用白名单验证文件类型，文件名使用`secure_filename`处理
2. **大小限制**：配置了最大上传大小限制（500MB）
3. **CORS**：默认允许所有来源，生产环境建议配置具体允许的域名

