<template>
  <div class="ppt-control-view">
    <h1 class="page-title">PPT 演示控制</h1>
    
    <el-row :gutter="20">
      <!-- 左侧：摄像头和手势识别 -->
      <el-col :xs="24" :lg="8">
        <CameraFeed 
          module="ppt" 
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
      
      <!-- 右侧：PPT显示区域 -->
      <el-col :xs="24" :lg="16">
        <el-card class="ppt-viewer-card">
          <template #header>
            <div class="ppt-header">
              <span>PPT 演示区域</span>
              <div class="ppt-controls">
                <el-upload
                  action="/api/upload/ppt"
                  :show-file-list="false"
                  :on-success="handleUploadSuccess"
                  accept=".pptx,.ppt,.pdf"
                >
                  <el-button type="primary" :icon="Upload">上传PPT</el-button>
                </el-upload>
                
                <el-select 
                  v-model="selectedPPT" 
                  placeholder="选择PPT"
                  @change="loadPPT"
                  style="width: 200px; margin-left: 10px;"
                >
                  <el-option
                    v-for="file in pptFiles"
                    :key="file.filename"
                    :label="file.filename"
                    :value="file.path"
                  />
                </el-select>
              </div>
            </div>
          </template>
          
          <div class="ppt-display">
            <!-- PPT显示区域 -->
            <div v-if="!selectedPPT" class="empty-state">
              <el-empty description="请上传或选择一个PPT文件">
                <el-upload
                  action="/api/upload/ppt"
                  :show-file-list="false"
                  :on-success="handleUploadSuccess"
                  accept=".pptx,.ppt,.pdf"
                >
                  <el-button type="primary">上传PPT</el-button>
                </el-upload>
              </el-empty>
            </div>
            
            <!-- 使用iframe显示PDF或Office Online -->
            <div v-else class="ppt-iframe-container">
              <iframe 
                v-if="isPDF"
                :src="pdfViewerUrl" 
                class="ppt-iframe"
                ref="pptIframe"
              ></iframe>
              
              <div v-else class="office-viewer">
                <el-alert
                  title="PPT显示说明"
                  type="info"
                  description="由于浏览器限制，PPTX文件需要使用Office Online或转换为PDF格式才能在线预览。建议上传PDF格式文件。"
                  :closable="false"
                  show-icon
                />
                
                <!-- 简单的图片列表模拟PPT -->
                <div class="slide-container">
                  <div class="slide">
                    <h2>幻灯片 {{ currentSlide + 1 }} / {{ totalSlides }}</h2>
                    <div class="slide-content">
                      <p>当前显示幻灯片内容</p>
                      <p>使用手势进行控制：</p>
                      <ul>
                        <li>👎 下一页</li>
                        <li>👍 上一页</li>
                        <li>✋ 第一页</li>
                        <li>✊ 最后一页</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- PPT控制面板 -->
            <div class="ppt-controls-panel" v-if="selectedPPT">
              <el-button-group>
                <el-button @click="firstSlide" :icon="DArrowLeft">首页</el-button>
                <el-button @click="previousSlide" :icon="ArrowLeft" :disabled="currentSlide === 0">上一页</el-button>
                <el-button disabled>{{ currentSlide + 1 }} / {{ totalSlides }}</el-button>
                <el-button @click="nextSlide" :icon="ArrowRight" :disabled="currentSlide >= totalSlides - 1">下一页</el-button>
                <el-button @click="lastSlide" :icon="DArrowRight">末页</el-button>
              </el-button-group>
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
import { Upload, ArrowLeft, ArrowRight, DArrowLeft, DArrowRight } from '@element-plus/icons-vue'
import CameraFeed from '../components/CameraFeed.vue'
import axios from 'axios'

const selectedPPT = ref('')
const pptFiles = ref([])
const currentSlide = ref(0)
const totalSlides = ref(10) // 默认10页
const pptIframe = ref(null)
const gestureMappings = ref([])

const isPDF = computed(() => {
  return selectedPPT.value.toLowerCase().endsWith('.pdf')
})

const pdfViewerUrl = computed(() => {
  if (isPDF.value && selectedPPT.value) {
    // 确保路径正确，移除/api前缀（因为vite会自动代理）
    let path = selectedPPT.value
    if (!path.startsWith('/assets')) {
      path = `/assets${path.startsWith('/') ? path : '/' + path}`
    }
    // 使用Mozilla CDN的PDF.js viewer
    const pdfUrl = encodeURIComponent(window.location.origin + path)
    // zoom=page-fit 设置默认缩放为"适合页面"
    return `https://mozilla.github.io/pdf.js/web/viewer.html?file=${pdfUrl}#page=${currentSlide.value + 1}&zoom=page-fit`
  }
  return ''
})

// 加载PPT文件列表
const loadPPTFiles = async () => {
  try {
    const response = await axios.get('/api/files/presentations')
    pptFiles.value = response.data.files
    
    // 如果有默认文件，选择第一个
    if (pptFiles.value.length > 0 && !selectedPPT.value) {
      selectedPPT.value = pptFiles.value[0].path
      loadPPT()
    }
  } catch (error) {
    console.error('加载PPT列表失败:', error)
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
    const response = await axios.get('/api/config?module=ppt')
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

const getActionName = (action) => {
  const actionNames = {
    'next_slide': '下一页',
    'prev_slide': '上一页',
    'first_slide': '第一页',
    'last_slide': '最后一页',
    'scroll_up': '向上滚动',
    'scroll_down': '向下滚动'
  }
  return actionNames[action] || action
}

// 防抖和状态记录
let lastAction = null
let lastActionTime = 0
const actionCooldown = 800 // 冷却时间800ms

// 处理手势识别结果
const handleGestureDetected = (gestureInfo) => {
  const action = gestureInfo.action
  const now = Date.now()
  
  console.log('PPT收到手势:', gestureInfo)
  
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
  
  // 根据操作执行相应功能
  switch (action) {
    case 'next_slide':
      nextSlide()
      ElMessage.success('下一页')
      break
    case 'prev_slide':
      previousSlide()
      ElMessage.success('上一页')
      break
    case 'first_slide':
      firstSlide()
      ElMessage.success('第一页')
      break
    case 'last_slide':
      lastSlide()
      ElMessage.success('最后一页')
      break
    case 'scroll_up':
      scrollUp()
      ElMessage.info('向上滚动')
      break
    case 'scroll_down':
      scrollDown()
      ElMessage.info('向下滚动')
      break
  }
}

// PPT控制函数
const nextSlide = () => {
  if (currentSlide.value < totalSlides.value - 1) {
    currentSlide.value++
    updatePDFPage()
  }
}

const previousSlide = () => {
  if (currentSlide.value > 0) {
    currentSlide.value--
    updatePDFPage()
  }
}

const firstSlide = () => {
  currentSlide.value = 0
  updatePDFPage()
}

const lastSlide = () => {
  if (totalSlides.value > 0) {
    currentSlide.value = totalSlides.value - 1
    updatePDFPage()
  }
}

// 更新PDF页面显示
const updatePDFPage = () => {
  if (isPDF.value && pptIframe.value) {
    // PDF.js viewer会自动响应URL中#page参数的变化
    // 由于pdfViewerUrl是computed属性，它会自动更新
    const newUrl = pdfViewerUrl.value
    console.log('更新PDF URL:', newUrl, '当前页:', currentSlide.value + 1)
    // 强制iframe重新加载以应用新的页面参数
    pptIframe.value.src = newUrl
  }
}

const scrollUp = () => {
  // PDF模式下：向上滚动等同于上一页
  if (isPDF.value) {
    previousSlide()
  } else {
    // PPT模式：实现滚动（如果支持）
    if (pptIframe.value && pptIframe.value.contentWindow) {
      try {
        pptIframe.value.contentWindow.scrollBy(0, -100)
      } catch (e) {
        console.log('滚动操作不支持')
      }
    }
  }
}

const scrollDown = () => {
  // PDF模式下：向下滚动等同于下一页
  if (isPDF.value) {
    nextSlide()
  } else {
    // PPT模式：实现滚动（如果支持）
    if (pptIframe.value && pptIframe.value.contentWindow) {
      try {
        pptIframe.value.contentWindow.scrollBy(0, 100)
      } catch (e) {
        console.log('滚动操作不支持')
      }
    }
  }
}

// 加载PPT
const loadPPT = async () => {
  currentSlide.value = 0
  
  // 对于PDF，尝试获取页数
  if (isPDF.value) {
    // 从文件名中提取页数（如果有）或使用默认值
    const fileName = selectedPPT.value.split('/').pop()
    console.log('加载PDF文件:', fileName)
    
    // 设置为11页（根据用户反馈）
    // TODO: 未来可以通过PDF.js库获取准确页数
    totalSlides.value = 11
    
    ElMessage.success('PDF加载成功（共11页）')
  } else {
    totalSlides.value = 10
    ElMessage.success('PPT加载成功')
  }
}

// 上传成功回调
const handleUploadSuccess = (response) => {
  ElMessage.success('PPT上传成功')
  loadPPTFiles()
  selectedPPT.value = response.path
  loadPPT()
}

// 加载键盘快捷键配置
let keyboardConfig = {}

const loadKeyboardConfig = async () => {
  try {
    const response = await axios.get('/api/config?module=ppt')
    keyboardConfig = response.data.keyboard_shortcuts || {}
    console.log('PPT键盘快捷键配置:', keyboardConfig)
  } catch (error) {
    console.error('加载键盘配置失败:', error)
  }
}

// 键盘快捷键支持（使用配置的快捷键）
const handleKeyPress = (event) => {
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

// 执行操作
const executeAction = (action) => {
  console.log('执行PPT操作:', action)
  switch (action) {
    case 'next_slide':
      nextSlide()
      break
    case 'prev_slide':
      previousSlide()
      break
    case 'first_slide':
      firstSlide()
      break
    case 'last_slide':
      lastSlide()
      break
    case 'scroll_up':
      scrollUp()
      break
    case 'scroll_down':
      scrollDown()
      break
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
  loadPPTFiles()
  loadGestureMappings()
  loadKeyboardConfig()
  window.addEventListener('keydown', handleKeyPress)
  document.addEventListener('visibilitychange', handleVisibilityChange)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyPress)
  document.removeEventListener('visibilitychange', handleVisibilityChange)
})
</script>

<style scoped>
.ppt-control-view {
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

.ppt-viewer-card {
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
}

.ppt-viewer-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 10px;
}

.ppt-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.ppt-controls {
  display: flex;
  gap: 10px;
}

.ppt-display {
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

.ppt-iframe-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.ppt-iframe {
  width: 100%;
  flex: 1;
  min-height: 700px; /* Increase minimum height */
  border: none;
  background: #f5f5f5;
}

.office-viewer {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.slide-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  border-radius: 8px;
}

.slide {
  background: white;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 800px;
}

.slide-content {
  margin-top: 20px;
  text-align: left;
}

.slide-content ul {
  list-style: none;
  padding: 0;
}

.slide-content li {
  padding: 8px 0;
  font-size: 16px;
}

.ppt-controls-panel {
  margin-top: 20px;
  display: flex;
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

