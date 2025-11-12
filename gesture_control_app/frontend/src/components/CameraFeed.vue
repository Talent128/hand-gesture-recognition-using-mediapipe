<template>
  <div class="camera-feed">
    <div class="camera-container">
      <video ref="videoElement" autoplay playsinline class="video-feed" style="display: none;"></video>
      <canvas ref="canvasElement" class="canvas-display"></canvas>
      
      <div class="camera-controls">
        <el-button 
          :type="isStreaming ? 'danger' : 'primary'" 
          @click="toggleCamera"
          :icon="isStreaming ? VideoPause : VideoPlay"
        >
          {{ isStreaming ? '停止摄像头' : '启动摄像头' }}
        </el-button>
      </div>
    </div>

    <!-- 手势信息显示 -->
    <el-card shadow="hover" class="gesture-result-card">
      <div class="gesture-result-fixed">
        <div class="result-row single-gesture">
          <span class="gesture-emoji">{{ getGestureEmoji(currentGesture) }}</span>
          <span class="gesture-name">{{ currentGesture || '无手势' }}</span>
        </div>
        <div class="result-row action-row">
          <span class="result-label">当前操作:</span>
          <span class="result-value action-value">{{ currentAction || '--' }}</span>
        </div>
        <div class="result-row fps-row">
          <span class="fps-label">FPS:</span>
          <span class="fps-value">{{ actualFps }}</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { VideoPlay, VideoPause } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const props = defineProps({
  module: {
    type: String,
    default: null // 'ppt' 或 'video'
  },
  onGestureDetected: {
    type: Function,
    default: null
  }
})

const videoElement = ref(null)
const canvasElement = ref(null)
const isStreaming = ref(false)
const gestureData = ref(null)
const currentAction = ref(null)
const currentGesture = ref(null) // 当前有效手势
const stream = ref(null)
const animationFrameId = ref(null)
const isProcessing = ref(false)
const lastProcessTime = ref(0)
const fps = ref(30) // 目标帧率：30帧/秒
const actualFps = ref(0) // 实际FPS
const fpsTimeBuffer = ref([]) // FPS时间差缓冲区
const fpsBufferLen = 10 // 缓冲区长度
const fpsLastTick = ref(Date.now())
const pointHistory = ref([]) // 指尖历史轨迹

let config = null

// 加载配置
const loadConfig = async () => {
  if (props.module) {
    try {
      console.log('正在加载配置:', props.module)
      const response = await axios.get(`/api/config?module=${props.module}`, {
        timeout: 5000
      })
      config = response.data
      console.log('配置加载成功:', config)
    } catch (error) {
      console.error('加载配置失败:', error.message)
      if (error.response) {
        console.error('错误响应:', error.response.status, error.response.data)
      }
    }
  }
}

// 启动摄像头
const startCamera = async () => {
  try {
    stream.value = await navigator.mediaDevices.getUserMedia({
      video: { 
        width: 640, 
        height: 480,
        frameRate: { ideal: 30, max: 60 }  // 优化帧率
      }
    })
    
    videoElement.value.srcObject = stream.value
    isStreaming.value = true
    
    // 等待视频加载
    videoElement.value.onloadedmetadata = () => {
      const canvas = canvasElement.value
      // 固定Canvas大小为640x480
      canvas.width = 640
      canvas.height = 480
      processFrame()
    }
  } catch (error) {
    console.error('启动摄像头失败:', error)
    alert('无法访问摄像头，请检查权限设置')
  }
}

// 停止摄像头
const stopCamera = () => {
  if (stream.value) {
    stream.value.getTracks().forEach(track => track.stop())
    stream.value = null
  }
  
  if (animationFrameId.value) {
    cancelAnimationFrame(animationFrameId.value)
    animationFrameId.value = null
  }
  
  isStreaming.value = false
  
  // 清空canvas
  const canvas = canvasElement.value
  if (canvas) {
    const context = canvas.getContext('2d')
    context.clearRect(0, 0, canvas.width, canvas.height)
  }
  
  // 重置手势数据
  gestureData.value = null
  currentAction.value = null
  currentGesture.value = null
  fpsTimeBuffer.value = []
  pointHistory.value = []
}

// 切换摄像头
const toggleCamera = () => {
  if (isStreaming.value) {
    stopCamera()
  } else {
    startCamera()
  }
}

// 处理视频帧
const processFrame = async () => {
  if (!isStreaming.value) return
  
  const canvas = canvasElement.value
  const context = canvas.getContext('2d')
  const video = videoElement.value
  
  // 每一帧都绘制视频（保持流畅显示）
  context.clearRect(0, 0, canvas.width, canvas.height)
  
  // 镜像翻转canvas内容（与app.py的flip保持一致）
  context.save()
  context.scale(-1, 1)  // 水平翻转
  context.drawImage(video, -canvas.width, 0, canvas.width, canvas.height)
  context.restore()
  
  // 先绘制指尖历史轨迹（在关键点之前）
  if (pointHistory.value.length > 0) {
    drawPointHistory(context, pointHistory.value)
  }
  
  // 再绘制手部关键点（覆盖在轨迹上方）
  if (gestureData.value?.hand_detected && gestureData.value?.landmarks) {
    drawLandmarks(context, gestureData.value.landmarks)
  }
  
  // 计算FPS
  updateFPS()
  
  const now = Date.now()
  const elapsed = now - lastProcessTime.value
  const interval = 1000 / fps.value // 计算帧间隔
  
  // 控制识别频率：只有当时间间隔足够且没有正在处理的请求时才识别
  if (elapsed >= interval && !isProcessing.value) {
    lastProcessTime.value = now
    isProcessing.value = true
    
    // 获取当前帧的图像数据（降低质量以减少传输延迟，0.8是平衡点）
    const imageData = canvas.toDataURL('image/jpeg', 0.8)
    
    // 异步处理识别请求
    axios.post('/api/gesture/recognize', {
      image: imageData,
      draw_landmarks: false
    }, {
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then(response => {
      gestureData.value = response.data
      
      // 更新指尖历史轨迹（与app.py逻辑一致：line 144-147）
      if (response.data.hand_detected && response.data.landmarks) {
        if (response.data.static_gesture === 'Pointer') {
          // 食指指尖是第8个关键点
          const indexFingerTip = response.data.landmarks[8]
          pointHistory.value.push(indexFingerTip)
        } else {
          // 非Pointer手势时添加[0,0]而不是清空（与app.py保持一致）
          pointHistory.value.push([0, 0])
        }
        // 保持历史记录在16个点以内
        while (pointHistory.value.length > 16) {
          pointHistory.value.shift()
        }
      } else {
        // 未检测到手时也添加[0,0]（与app.py line 172保持一致）
        pointHistory.value.push([0, 0])
        while (pointHistory.value.length > 16) {
          pointHistory.value.shift()
        }
      }
      
      // 如果检测到手势并且有模块配置，获取对应操作
      if (response.data.hand_detected && props.module && config) {
        const gesture = response.data.static_gesture
        const dynamicGesture = response.data.dynamic_gesture
        
        // 确定有效手势（优先静态，然后动态）
        let effectiveGesture = gesture
        let action = config.gestures?.[gesture]
        
        if (!action && dynamicGesture !== 'Stop') {
          effectiveGesture = dynamicGesture
          action = config.gestures?.[dynamicGesture]
        }
        
        // 直接使用后端平滑后的结果，不再做前端阈值判断
        currentGesture.value = effectiveGesture !== 'Pointer' ? effectiveGesture : null
        
        if (action) {
          currentAction.value = action
          
          // 触发回调
          if (props.onGestureDetected) {
            props.onGestureDetected({
              gesture: gesture,
              dynamicGesture: dynamicGesture,
              effectiveGesture: effectiveGesture,
              action: action
            })
          }
        } else {
          currentAction.value = null
        }
      } else {
        currentAction.value = null
        currentGesture.value = null
      }
    })
    .catch(error => {
      console.error('手势识别失败:', error)
    })
    .finally(() => {
      isProcessing.value = false
    })
  }
  
  // 继续处理下一帧（使用requestAnimationFrame保持流畅）
  animationFrameId.value = requestAnimationFrame(processFrame)
}

// 绘制手部关键点（参考app.py的绘制方式）
const drawLandmarks = (context, landmarks) => {
  if (!landmarks || landmarks.length === 0) return
  
  // 绘制连接线（黑色边框 + 白色线条）
  const connections = [
    // 拇指
    [2, 3], [3, 4],
    // 食指
    [5, 6], [6, 7], [7, 8],
    // 中指
    [9, 10], [10, 11], [11, 12],
    // 无名指
    [13, 14], [14, 15], [15, 16],
    // 小指
    [17, 18], [18, 19], [19, 20],
    // 手掌
    [0, 1], [1, 2], [2, 5], [5, 9], [9, 13], [13, 17], [17, 0]
  ]
  
  // 先绘制黑色粗线（边框效果）
  context.strokeStyle = '#000000'
  context.lineWidth = 6
  connections.forEach(([start, end]) => {
    if (start < landmarks.length && end < landmarks.length) {
      context.beginPath()
      context.moveTo(landmarks[start][0], landmarks[start][1])
      context.lineTo(landmarks[end][0], landmarks[end][1])
      context.stroke()
    }
  })
  
  // 再绘制白色细线（主线条）
  context.strokeStyle = '#FFFFFF'
  context.lineWidth = 2
  connections.forEach(([start, end]) => {
    if (start < landmarks.length && end < landmarks.length) {
      context.beginPath()
      context.moveTo(landmarks[start][0], landmarks[start][1])
      context.lineTo(landmarks[end][0], landmarks[end][1])
      context.stroke()
    }
  })
  
  // 绘制关键点
  landmarks.forEach((point, index) => {
    // 指尖使用较大的圆
    const isFingerTip = [4, 8, 12, 16, 20].includes(index)
    const radius = isFingerTip ? 8 : 5
    
    // 先绘制白色圆
    context.fillStyle = '#FFFFFF'
    context.beginPath()
    context.arc(point[0], point[1], radius, 0, 2 * Math.PI)
    context.fill()
    
    // 再绘制黑色边框
    context.strokeStyle = '#000000'
    context.lineWidth = 1
    context.beginPath()
    context.arc(point[0], point[1], radius, 0, 2 * Math.PI)
    context.stroke()
  })
}

// 绘制指尖历史轨迹（参考app.py的draw_point_history）
const drawPointHistory = (context, history) => {
  for (let i = 0; i < history.length; i++) {
    const point = history[i]
    if (point && point[0] !== 0 && point[1] !== 0) {
      // 半径随索引增大而增大，模拟轨迹效果
      const radius = 1 + Math.floor(i / 2)
      context.fillStyle = 'rgba(152, 251, 152, 0.9)' // 浅绿色，略微透明
      context.beginPath()
      context.arc(point[0], point[1], radius, 0, 2 * Math.PI)
      context.fill()
    }
  }
}

// 更新FPS（参考cvfpscalc.py的实现）
const updateFPS = () => {
  const currentTick = Date.now()
  const diffTime = currentTick - fpsLastTick.value
  fpsLastTick.value = currentTick
  
  // 添加到缓冲区
  fpsTimeBuffer.value.push(diffTime)
  if (fpsTimeBuffer.value.length > fpsBufferLen) {
    fpsTimeBuffer.value.shift()
  }
  
  // 计算平均FPS
  if (fpsTimeBuffer.value.length > 0) {
    const avgTime = fpsTimeBuffer.value.reduce((a, b) => a + b, 0) / fpsTimeBuffer.value.length
    actualFps.value = Math.round(1000.0 / avgTime)
  }
}

// 获取手势对应的emoji
const getGestureEmoji = (gesture) => {
  const emojiMap = {
    'Open': '✋',
    'Close': '✊',
    'Pointer': '☝️',
    'OK': '👌',
    'Peace': '✌️',
    'Thumbs Up': '👍',
    'Thumbs Down': '👎',
    'Quiet Coyote': '🤘',
    'Move Up': '⬆️',
    'Move Down': '⬇️',
    'Move Left': '⬅️',
    'Move Right': '➡️',
    'Clockwise': '🔃',  // 镜像后交换：实际顺时针显示为逆时针图标
    'Counter Clockwise': '🔄'  // 镜像后交换：实际逆时针显示为顺时针图标
  }
  return emojiMap[gesture] || '❓'
}

// 监听模块变化，重新加载配置
watch(() => props.module, () => {
  loadConfig()
})

onMounted(async () => {
  // 检查后端连接
  try {
    console.log('检查后端连接...')
    const response = await axios.get('/api/health', { timeout: 3000 })
    console.log('后端连接正常:', response.data)
    ElMessage.success('后端服务连接成功')
  } catch (error) {
    console.error('后端连接失败:', error.message)
    ElMessage.error('无法连接到后端服务，请确认后端已启动')
  }
  
  await loadConfig()
})

onUnmounted(() => {
  stopCamera()
})

// 暴露方法供父组件调用
defineExpose({
  startCamera,
  stopCamera,
  reloadConfig: loadConfig
})
</script>

<style scoped>
.camera-feed {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.camera-container {
  position: relative;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
  width: 100%;
  max-width: 640px;
}

.video-feed {
  display: none;
}

.canvas-display {
  width: 100%;
  height: auto;
  display: block;
  background: #1a1a1a;
  /* canvas内容已在绘制时翻转，无需CSS镜像 */
}

.camera-controls {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
}

.gesture-info {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.gesture-details {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.gesture-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.gesture-item .label {
  font-weight: 600;
  min-width: 80px;
}

.gesture-result-card {
  margin-top: 20px;
}

.gesture-result-fixed {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.result-row {
  display: flex;
  align-items: center;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 8px;
}

.single-gesture {
  justify-content: center;
  gap: 15px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.gesture-emoji {
  font-size: 32px;
}

.gesture-name {
  font-size: 20px;
  font-weight: 700;
  color: #ffffff;
}

.action-row {
  justify-content: space-between;
}

.fps-row {
  justify-content: center;
  gap: 10px;
  background: #e8f4f8;
}

.result-label {
  font-weight: 600;
  color: #606266;
  font-size: 14px;
}

.result-value {
  font-size: 16px;
  font-weight: 700;
  color: #409eff;
}

.action-value {
  color: #67c23a;
}

.fps-label {
  font-weight: 600;
  color: #409eff;
  font-size: 14px;
}

.fps-value {
  font-size: 18px;
  font-weight: 700;
  color: #409eff;
}
</style>

