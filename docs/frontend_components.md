# 前端组件文档

## 组件架构

```
App.vue (根组件)
├── 侧边栏导航
└── 路由视图
    ├── Home.vue (首页)
    ├── PPTControl.vue (PPT控制)
    │   └── CameraFeed.vue (摄像头组件)
    ├── VideoControl.vue (视频控制)
    │   └── CameraFeed.vue (摄像头组件)
    └── Settings.vue (设置)
```

## 核心组件

### 1. CameraFeed.vue

摄像头采集和手势识别组件。

#### Props

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| module | String | null | 模块名称（'ppt' 或 'video'） |
| onGestureDetected | Function | null | 手势检测回调函数 |

#### 事件

**onGestureDetected(gestureInfo)**
- 触发时机：检测到手势并映射到操作时
- 参数：
  ```javascript
  {
    gesture: "Thumbs Up",        // 静态手势名称
    dynamicGesture: "Move Up",   // 动态手势名称
    action: "volume_up"          // 映射的操作
  }
  ```

#### 方法

**startCamera()**
- 启动摄像头
- 返回：Promise

**stopCamera()**
- 停止摄像头
- 无返回值

#### 使用示例

```vue
<template>
  <CameraFeed 
    module="video" 
    :onGestureDetected="handleGesture"
  />
</template>

<script setup>
import CameraFeed from '@/components/CameraFeed.vue'

const handleGesture = (gestureInfo) => {
  console.log('检测到手势:', gestureInfo)
  // 执行相应操作
}
</script>
```

#### 工作流程

1. 获取用户摄像头权限
2. 捕获视频帧到Canvas
3. 将Canvas内容编码为Base64
4. 发送到后端API进行识别
5. 接收识别结果
6. 查询配置获取操作
7. 触发回调函数
8. 在Canvas上绘制关键点

---

### 2. Home.vue

首页组件，展示系统功能和使用指南。

#### 功能

- 功能卡片展示（PPT控制、视频控制、设置）
- 支持手势列表
- 快速开始指南

#### 使用示例

```vue
<router-link to="/">首页</router-link>
```

---

### 3. PPTControl.vue

PPT控制视图组件。

#### 功能

- PPT文件选择和上传
- PPT内容显示（支持PDF）
- 手势控制响应
- 键盘快捷键支持
- 手势映射说明

#### 数据

```javascript
{
  selectedPPT: '',           // 选中的PPT路径
  pptFiles: [],              // PPT文件列表
  currentSlide: 0,           // 当前幻灯片索引
  totalSlides: 10,           // 总幻灯片数
  gestureMappings: []        // 手势映射表
}
```

#### 方法

**nextSlide()**
- 切换到下一页

**previousSlide()**
- 切换到上一页

**firstSlide()**
- 跳转到第一页

**lastSlide()**
- 跳转到最后一页

**scrollUp() / scrollDown()**
- 页面滚动

**loadPPTFiles()**
- 加载PPT文件列表

**handleGestureDetected(gestureInfo)**
- 处理手势识别结果

#### 手势映射

| 手势 | 操作 |
|------|------|
| Thumbs Down | 下一页 |
| Thumbs Up | 上一页 |
| Open | 第一页 |
| Close | 最后一页 |
| Move Up | 向上滚动 |
| Move Down | 向下滚动 |

#### 键盘快捷键

| 按键 | 操作 |
|------|------|
| → | 下一页 |
| ← | 上一页 |
| Home | 第一页 |
| End | 最后一页 |
| Page Up | 向上滚动 |
| Page Down | 向下滚动 |

---

### 4. VideoControl.vue

视频控制视图组件。

#### 功能

- 视频文件选择和上传
- 视频播放器
- 手势控制响应
- 键盘快捷键支持
- 播放信息显示
- 自定义控制面板

#### 数据

```javascript
{
  selectedVideo: '',         // 选中的视频路径
  videoFiles: [],            // 视频文件列表
  isPlaying: false,          // 播放状态
  currentTime: 0,            // 当前播放时间
  duration: 0,               // 视频总时长
  volume: 1.0,               // 音量 (0-1)
  playbackRate: 1.0,         // 播放速度
  gestureMappings: []        // 手势映射表
}
```

#### 方法

**togglePlay()**
- 切换播放/暂停

**play() / pause()**
- 播放 / 暂停

**restart()**
- 重新开始播放

**seekBackward() / seekForward()**
- 后退/前进10秒

**volumeUp() / volumeDown()**
- 音量增加/减少10%

**speedUp() / speedDown()**
- 播放速度增加/减少0.25x

**toggleFullscreen()**
- 切换全屏

**loadVideoFiles()**
- 加载视频文件列表

**handleGestureDetected(gestureInfo)**
- 处理手势识别结果（带防抖）

#### 手势映射

| 手势 | 操作 |
|------|------|
| Open | 播放 |
| Close | 暂停 |
| OK | 重新开始 |
| Peace | 全屏 |
| Thumbs Up | 音量+10% |
| Thumbs Down | 音量-10% |
| Move Left | 后退10秒 |
| Move Right | 前进10秒 |
| Clockwise | 加速 |
| Counter Clockwise | 减速 |

#### 键盘快捷键

| 按键 | 操作 |
|------|------|
| Space | 播放/暂停 |
| r | 重新开始 |
| f | 全屏 |
| ↑ | 音量+10% |
| ↓ | 音量-10% |
| ← | 后退10秒 |
| → | 前进10秒 |
| > | 加速 |
| < | 减速 |

---

### 5. Settings.vue

设置视图组件。

#### 功能

- PPT控制配置
- 视频控制配置
- 手势映射管理
- 键盘快捷键配置
- 系统信息显示
- 配置保存/重置

#### 标签页

1. **PPT控制配置**
   - 手势映射设置
   - 键盘快捷键设置

2. **视频控制配置**
   - 手势映射设置
   - 键盘快捷键设置

3. **系统信息**
   - 系统状态
   - 支持的手势列表
   - 使用说明

#### 方法

**loadConfigs()**
- 加载所有配置

**savePPTConfig()**
- 保存PPT配置

**saveVideoConfig()**
- 保存视频配置

**resetPPTConfig()**
- 重置PPT配置为默认值

**resetVideoConfig()**
- 重置视频配置为默认值

**checkBackendStatus()**
- 检查后端服务状态

---

## 状态管理

项目使用Pinia进行状态管理（虽然当前实现较为简单，但预留了扩展空间）。

### 可扩展的Store结构

```javascript
// stores/gesture.js
import { defineStore } from 'pinia'

export const useGestureStore = defineStore('gesture', {
  state: () => ({
    currentGesture: null,
    gestureHistory: [],
    config: {}
  }),
  
  actions: {
    updateGesture(gesture) {
      this.currentGesture = gesture
      this.gestureHistory.push(gesture)
    },
    
    loadConfig(config) {
      this.config = config
    }
  }
})
```

---

## 路由配置

```javascript
const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/ppt',
    name: 'PPTControl',
    component: PPTControl
  },
  {
    path: '/video',
    name: 'VideoControl',
    component: VideoControl
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings
  }
]
```

---

## 样式规范

### 颜色方案

```css
--primary-color: #3498db;      /* 主色 */
--secondary-color: #2c3e50;    /* 次要色 */
--success-color: #67c23a;      /* 成功 */
--warning-color: #e6a23c;      /* 警告 */
--danger-color: #f56c6c;       /* 危险 */
--info-color: #909399;         /* 信息 */
--background-color: #ecf0f1;   /* 背景 */
```

### 响应式断点

```css
xs: < 768px    /* 手机 */
sm: ≥ 768px    /* 平板 */
md: ≥ 992px    /* 小屏PC */
lg: ≥ 1200px   /* 大屏PC */
xl: ≥ 1920px   /* 超大屏 */
```

---

## 开发建议

### 1. 组件开发

- 使用组合式API（Composition API）
- 遵循单一职责原则
- 提供清晰的Props和Events
- 添加必要的注释

### 2. 性能优化

```vue
<script setup>
import { ref, computed, watch } from 'vue'

// 使用computed缓存计算结果
const filteredData = computed(() => {
  return data.value.filter(item => item.active)
})

// 使用watch监听变化
watch(() => props.value, (newVal) => {
  // 处理逻辑
})

// 使用防抖处理频繁操作
let debounceTimer = null
const debouncedFunction = () => {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    // 执行操作
  }, 300)
}
</script>
```

### 3. 错误处理

```javascript
try {
  const response = await axios.get('/api/config')
  // 处理响应
} catch (error) {
  console.error('请求失败:', error)
  ElMessage.error('加载配置失败')
}
```

### 4. 代码分割

```javascript
// 路由懒加载
const Settings = () => import('@/views/Settings.vue')
```

---

## 调试技巧

### 1. Vue DevTools

安装Vue DevTools浏览器扩展，可以：
- 查看组件树
- 检查Props和Data
- 追踪事件
- 性能分析

### 2. 网络调试

```javascript
// 在axios请求中添加拦截器
axios.interceptors.request.use(config => {
  console.log('请求:', config)
  return config
})

axios.interceptors.response.use(response => {
  console.log('响应:', response)
  return response
})
```

### 3. 控制台日志

```javascript
// 开发环境启用详细日志
if (import.meta.env.DEV) {
  console.log('手势识别结果:', result)
}
```

---

## 测试

### 单元测试示例

```javascript
import { mount } from '@vue/test-utils'
import CameraFeed from '@/components/CameraFeed.vue'

describe('CameraFeed.vue', () => {
  it('启动摄像头', async () => {
    const wrapper = mount(CameraFeed)
    await wrapper.vm.startCamera()
    expect(wrapper.vm.isStreaming).toBe(true)
  })
})
```

---

## 常见问题

### Q: 如何添加新的控制页面？

1. 在`views/`创建新组件
2. 在`router/index.js`添加路由
3. 在`App.vue`菜单中添加入口
4. 在后端`config_manager.py`添加配置

### Q: 如何自定义手势映射？

在Settings页面修改配置，或直接编辑`config/gesture_mapping.json`文件。

### Q: 如何优化手势识别性能？

1. 降低发送到后端的图像质量
2. 控制帧率（减少requestAnimationFrame频率）
3. 添加防抖处理

