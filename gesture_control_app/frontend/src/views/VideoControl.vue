<template>
  <div class="video-control-view">
    <h1 class="page-title">视频播放控制</h1>
    
    <el-row :gutter="20">
      <!-- 左侧：摄像头和手势识别 -->
      <el-col :xs="24" :lg="8">
        <CameraFeed 
          module="video" 
          :onGestureDetected="handleGestureDetected"
        />
        
            <!-- 手势映射说明 -->
            <el-card class="gesture-mapping-card" shadow="hover">
              <template #header>
                <h3>手势控制说明</h3>
              </template>
              
              <!-- 静态手势组 -->
              <div v-if="groupedGestureMappings['静态'].length > 0" class="gesture-group">
                <div class="group-header">
                  <el-tag type="success" size="small">静态</el-tag>
                </div>
                <el-table :data="groupedGestureMappings['静态']" style="width: 100%" size="small" :show-header="false">
                  <el-table-column width="50">
                    <template #default="scope">
                      <span class="gesture-emoji">{{ scope.row.emoji }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="gesture" label="手势" width="120" />
                  <el-table-column prop="action" label="操作" />
                </el-table>
              </div>
              
              <!-- 动态手势组 -->
              <div v-if="groupedGestureMappings['动态'].length > 0" class="gesture-group" style="margin-top: 15px;">
                <div class="group-header">
                  <el-tag type="warning" size="small">动态</el-tag>
                </div>
                <el-table :data="groupedGestureMappings['动态']" style="width: 100%" size="small" :show-header="false">
                  <el-table-column width="50">
                    <template #default="scope">
                      <span class="gesture-emoji">{{ scope.row.emoji }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="gesture" label="手势" width="120" />
                  <el-table-column prop="action" label="操作" />
                </el-table>
              </div>
            </el-card>
      </el-col>
      
      <!-- 右侧：视频播放区域 -->
      <el-col :xs="24" :lg="16">
        <el-card class="video-player-card">
          <template #header>
            <div class="video-header">
              <span>视频播放区域</span>
              <div class="video-controls">
                <el-upload
                  action="/api/upload/video"
                  :show-file-list="false"
                  :on-success="handleUploadSuccess"
                  accept=".mp4,.avi,.mkv,.mov,.webm"
                >
                  <el-button type="primary" :icon="Upload">上传视频</el-button>
                </el-upload>
                
                <el-select 
                  v-model="selectedVideo" 
                  placeholder="选择视频"
                  @change="loadVideo"
                  style="width: 200px; margin-left: 10px;"
                >
                  <el-option
                    v-for="file in videoFiles"
                    :key="file.filename"
                    :label="file.filename"
                    :value="file.path"
                  />
                </el-select>
              </div>
            </div>
          </template>
          
          <div class="video-display">
            <!-- 视频显示区域 -->
            <div v-if="!selectedVideo" class="empty-state">
              <el-empty description="请上传或选择一个视频文件">
                <el-upload
                  action="/api/upload/video"
                  :show-file-list="false"
                  :on-success="handleUploadSuccess"
                  accept=".mp4,.avi,.mkv,.mov,.webm"
                >
                  <el-button type="primary">上传视频</el-button>
                </el-upload>
              </el-empty>
            </div>
            
            <div v-else class="video-container">
              <video 
                ref="videoPlayer"
                :src="selectedVideo.startsWith('/assets') ? selectedVideo : `/assets${selectedVideo}`"
                controls
                class="video-element"
                @loadedmetadata="handleVideoLoaded"
                @timeupdate="handleTimeUpdate"
                @play="isPlaying = true"
                @pause="isPlaying = false"
              ></video>
              
              <!-- 视频信息 -->
              <div class="video-info">
                <el-row :gutter="10">
                  <el-col :span="8">
                    <el-statistic title="当前时间" :value="currentTime" :formatter="(val) => formatTime(val)" />
                  </el-col>
                  <el-col :span="8">
                    <el-statistic title="总时长" :value="duration" :formatter="(val) => formatTime(val)" />
                  </el-col>
                  <el-col :span="8">
                    <el-statistic title="播放速度" :value="playbackRate" suffix="x" :precision="2" />
                  </el-col>
                </el-row>
              </div>
              
              <!-- 自定义控制面板 -->
              <div class="custom-controls">
                <el-button-group>
                  <el-button @click="togglePlay" :icon="isPlaying ? VideoPause : VideoPlay">
                    {{ isPlaying ? '暂停' : '播放' }}
                  </el-button>
                  <el-button @click="restart" :icon="RefreshLeft">重新开始</el-button>
                  <el-button @click="seekBackward" :icon="DArrowLeft">后退10秒</el-button>
                  <el-button @click="seekForward" :icon="DArrowRight">前进10秒</el-button>
                </el-button-group>
                
                <el-button-group style="margin-left: 10px;">
                  <el-button @click="volumeDown" :icon="Remove">音量-</el-button>
                  <el-button disabled>音量 {{ Math.round(volume * 100) }}%</el-button>
                  <el-button @click="volumeUp" :icon="Plus">音量+</el-button>
                </el-button-group>
                
                <el-button-group style="margin-left: 10px;">
                  <el-button @click="speedDown">慢速</el-button>
                  <el-button disabled>{{ playbackRate }}x</el-button>
                  <el-button @click="speedUp">快速</el-button>
                </el-button-group>
                
                <el-button @click="toggleFullscreen" :icon="FullScreen" style="margin-left: 10px;">
                  全屏
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Upload, VideoPlay, VideoPause, RefreshLeft, 
  DArrowLeft, DArrowRight, Plus, Remove, FullScreen 
} from '@element-plus/icons-vue'
import CameraFeed from '../components/CameraFeed.vue'
import axios from 'axios'

const selectedVideo = ref('')
const videoFiles = ref([])
const videoPlayer = ref(null)
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const volume = ref(1.0)
const playbackRate = ref(1.0)
const gestureMappings = ref([])

let gestureDebounce = null

// 加载视频文件列表
const loadVideoFiles = async () => {
  try {
    const response = await axios.get('/api/files/videos')
    videoFiles.value = response.data.files
    
    // 如果有默认文件，选择第一个
    if (videoFiles.value.length > 0 && !selectedVideo.value) {
      selectedVideo.value = videoFiles.value[0].path
    }
  } catch (error) {
    console.error('加载视频列表失败:', error)
  }
}

// 手势类型映射
const gestureTypes = {
  'Open': '静态',
  'Close': '静态',
  'Pointer': '静态',
  'OK': '静态',
  'Peace': '静态',
  'Thumbs Up': '静态',
  'Thumbs Down': '静态',
  'Quiet Coyote': '静态',
  'Move Up': '动态',
  'Move Down': '动态',
  'Move Left': '动态',
  'Move Right': '动态',
  'Clockwise': '动态',
  'Counter Clockwise': '动态'
}

// 手势emoji映射
const gestureEmojis = {
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
  'Clockwise': '🔃',  // 镜像后交换
  'Counter Clockwise': '🔄'  // 镜像后交换
}

// 加载手势映射配置
const loadGestureMappings = async () => {
  try {
    const response = await axios.get('/api/config?module=video')
    const config = response.data
    
    gestureMappings.value = Object.entries(config.gestures || {}).map(([gesture, action]) => ({
      type: gestureTypes[gesture] || '未知',
      gesture,
      emoji: gestureEmojis[gesture] || '🤚',
      action: getActionName(action)
    }))
  } catch (error) {
    console.error('加载手势映射失败:', error)
  }
}

const getActionName = (action) => {
  const actionNames = {
    'play': '播放',
    'pause': '暂停',
    'restart': '重新开始',
    'fullscreen': '全屏',
    'volume_up': '音量增加',
    'volume_down': '音量减少',
    'seek_backward': '后退10秒',
    'seek_forward': '前进10秒',
    'speed_up': '加速播放',
    'speed_down': '减速播放'
  }
  return actionNames[action] || action
}

// 按类型分组的手势映射
const groupedGestureMappings = computed(() => {
  const groups = {
    '静态': [],
    '动态': []
  }
  
  gestureMappings.value.forEach(mapping => {
    if (groups[mapping.type]) {
      groups[mapping.type].push(mapping)
    }
  })
  
  return groups
})

// 防抖和状态记录
let lastAction = null
let lastActionTime = 0
const actionCooldown = 800 // 冷却时间800ms

// 处理手势识别结果
const handleGestureDetected = (gestureInfo) => {
  const action = gestureInfo.action
  const now = Date.now()
  
  console.log('视频收到手势:', gestureInfo)
  
  // 冷却时间内不执行
  if (now - lastActionTime < actionCooldown) {
    return
  }
  
  // 相同操作需要间隔更长时间
  if (action === lastAction && now - lastActionTime < 1500) {
    return
  }
  
  lastAction = action
  lastActionTime = now
  
  executeAction(action)
  
  // 显示操作提示
  showActionMessage(action)
}

// 显示操作提示
const showActionMessage = (action) => {
  const messages = {
    'play': '播放',
    'pause': '暂停',
    'restart': '重新开始',
    'fullscreen': '进入全屏',
    'exit_fullscreen': '退出全屏',
    'volume_up': '音量+',
    'volume_down': '音量-',
    'seek_backward': '后退10秒',
    'seek_forward': '前进10秒',
    'speed_up': '加速',
    'speed_down': '减速'
  }
  
  const message = messages[action]
  if (message) {
    ElMessage.success(message)
  }
}

// 执行操作
const executeAction = (action) => {
  switch (action) {
    case 'play':
      play()
      break
    case 'pause':
      pause()
      break
    case 'restart':
      restart()
      break
    case 'fullscreen':
      enterFullscreen()
      break
    case 'exit_fullscreen':
      exitFullscreen()
      break
    case 'volume_up':
      volumeUp()
      break
    case 'volume_down':
      volumeDown()
      break
    case 'seek_backward':
      seekBackward()
      break
    case 'seek_forward':
      seekForward()
      break
    case 'speed_up':
      speedUp()
      break
    case 'speed_down':
      speedDown()
      break
  }
}

// 视频控制函数（移除提示消息）
const togglePlay = () => {
  if (isPlaying.value) {
    pause()
  } else {
    play()
  }
}

const play = () => {
  if (videoPlayer.value) {
    videoPlayer.value.play()
  }
}

const pause = () => {
  if (videoPlayer.value) {
    videoPlayer.value.pause()
  }
}

const restart = () => {
  if (videoPlayer.value) {
    videoPlayer.value.currentTime = 0
    videoPlayer.value.play()
  }
}

const seekBackward = () => {
  if (videoPlayer.value) {
    videoPlayer.value.currentTime = Math.max(0, videoPlayer.value.currentTime - 10)
  }
}

const seekForward = () => {
  if (videoPlayer.value) {
    videoPlayer.value.currentTime = Math.min(duration.value, videoPlayer.value.currentTime + 10)
  }
}

const volumeUp = () => {
  if (videoPlayer.value) {
    const newVolume = Math.min(1.0, volume.value + 0.1)
    videoPlayer.value.volume = newVolume
    volume.value = newVolume
  }
}

const volumeDown = () => {
  if (videoPlayer.value) {
    const newVolume = Math.max(0, volume.value - 0.1)
    videoPlayer.value.volume = newVolume
    volume.value = newVolume
  }
}

const speedUp = () => {
  if (videoPlayer.value) {
    const newRate = Math.min(2.0, playbackRate.value + 0.25)
    videoPlayer.value.playbackRate = newRate
    playbackRate.value = newRate
  }
}

const speedDown = () => {
  if (videoPlayer.value) {
    const newRate = Math.max(0.25, playbackRate.value - 0.25)
    videoPlayer.value.playbackRate = newRate
    playbackRate.value = newRate
  }
}

// 进入全屏（Peace手势）- 总是尝试进入全屏
const enterFullscreen = () => {
  if (videoPlayer.value) {
    if (!document.fullscreenElement) {
      videoPlayer.value.requestFullscreen().catch(err => {
        console.error('进入全屏失败:', err)
        ElMessage.error('无法进入全屏')
      })
    } else {
      console.log('已经在全屏模式，无需重复操作')
    }
  }
}

// 退出全屏（Quiet Coyote手势）
const exitFullscreen = () => {
  console.log('尝试退出全屏，当前fullscreenElement:', document.fullscreenElement)
  if (document.fullscreenElement) {
    document.exitFullscreen().catch(err => {
      console.error('退出全屏失败:', err)
      ElMessage.error('无法退出全屏')
    })
  } else {
    console.log('未在全屏模式，无需退出')
    ElMessage.info('当前不在全屏模式')
  }
}

// 保留toggleFullscreen用于按钮点击
const toggleFullscreen = () => {
  if (videoPlayer.value) {
    if (document.fullscreenElement) {
      exitFullscreen()
    } else {
      enterFullscreen()
    }
  }
}

// 视频事件处理
const handleVideoLoaded = () => {
  if (videoPlayer.value) {
    duration.value = videoPlayer.value.duration
    volume.value = videoPlayer.value.volume
    playbackRate.value = videoPlayer.value.playbackRate
  }
}

const handleTimeUpdate = () => {
  if (videoPlayer.value) {
    currentTime.value = videoPlayer.value.currentTime
  }
}

const loadVideo = () => {
  currentTime.value = 0
  ElMessage.success('视频加载成功')
}

const handleUploadSuccess = (response) => {
  ElMessage.success('视频上传成功')
  loadVideoFiles()
  selectedVideo.value = response.path
}

// 格式化时间
const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 加载键盘快捷键配置
let keyboardConfig = {}

const loadKeyboardConfig = async () => {
  try {
    const response = await axios.get('/api/config?module=video')
    keyboardConfig = response.data.keyboard_shortcuts || {}
    console.log('视频键盘快捷键配置:', keyboardConfig)
  } catch (error) {
    console.error('加载键盘配置失败:', error)
  }
}

// 键盘快捷键支持（使用配置的快捷键）
const handleKeyPress = (event) => {
  if (!videoPlayer.value) return
  
  // 获取按键名称
  let keyName = event.key
  if (event.key === ' ') keyName = 'Space'
  if (event.ctrlKey) keyName = 'Ctrl+' + keyName
  if (event.altKey) keyName = 'Alt+' + keyName
  if (event.shiftKey && event.key.length > 1) keyName = 'Shift+' + keyName
  
  console.log('按下的键:', keyName, event.key)
  
  // 检查是否匹配配置的快捷键
  for (const [action, configuredKey] of Object.entries(keyboardConfig)) {
    if (configuredKey === keyName || configuredKey === event.key) {
      event.preventDefault()
      executeAction(action)
      return
    }
  }
}

// 添加页面可见性监听，页面重新可见时重新加载配置
const handleVisibilityChange = () => {
  if (!document.hidden) {
    console.log('页面重新可见，重新加载配置')
    loadKeyboardConfig()
    loadGestureMappings()
  }
}

onMounted(() => {
  loadVideoFiles()
  loadGestureMappings()
  loadKeyboardConfig()
  window.addEventListener('keydown', handleKeyPress)
  document.addEventListener('visibilitychange', handleVisibilityChange)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyPress)
  document.removeEventListener('visibilitychange', handleVisibilityChange)
  if (gestureDebounce) {
    clearTimeout(gestureDebounce)
  }
})
</script>

<style scoped>
.video-control-view {
  max-width: 1600px;
  margin: 0 auto;
}

.page-title {
  font-size: 28px;
  color: #2c3e50;
  margin-bottom: 20px;
}

.gesture-mapping-card {
  margin-top: 20px;
}

.video-player-card {
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
}

.video-player-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 10px;
}

.video-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.video-controls {
  display: flex;
  gap: 10px;
}

.video-display {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 400px;
}

.video-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.video-element {
  width: 100%;
  max-height: 600px;
  min-height: 400px;
  background: #000;
  border-radius: 8px;
}

.video-info {
  padding: 10px 0;
}

.custom-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

/* 手势控制说明样式 */
.gesture-group {
  margin-bottom: 10px;
}

.group-header {
  margin-bottom: 8px;
}

.gesture-emoji {
  font-size: 24px;
  display: inline-block;
  text-align: center;
}
</style>

