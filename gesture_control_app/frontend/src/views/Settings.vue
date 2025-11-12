<template>
  <div class="settings-view">
    <h1 class="page-title">系统设置</h1>
    
    <el-tabs v-model="activeTab" type="card">
      <!-- PPT控制配置 -->
      <el-tab-pane label="PPT控制配置" name="ppt">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>PPT手势映射配置</span>
              <el-button type="primary" @click="savePPTConfig">保存配置</el-button>
            </div>
          </template>
          
          <el-form :model="pptConfig" label-width="150px">
            <h3>手势映射</h3>
            <el-form-item 
              v-for="(action, gesture) in pptConfig.gestures" 
              :key="gesture"
              :label="gesture"
            >
              <el-select v-model="pptConfig.gestures[gesture]" placeholder="选择操作">
                <el-option label="下一页" value="next_slide" />
                <el-option label="上一页" value="prev_slide" />
                <el-option label="第一页" value="first_slide" />
                <el-option label="最后一页" value="last_slide" />
                <el-option label="向上滚动" value="scroll_up" />
                <el-option label="向下滚动" value="scroll_down" />
              </el-select>
            </el-form-item>
            
            <el-divider />
            
            <h3>键盘快捷键映射</h3>
            <el-form-item 
              v-for="(key, action) in pptConfig.keyboard_shortcuts" 
              :key="action"
              :label="getActionName(action, 'ppt')"
            >
              <el-input 
                v-model="pptConfig.keyboard_shortcuts[action]" 
                placeholder="点击修改按钮后按下按键"
                readonly
              >
                <template #append>
                  <el-button 
                    @click="startKeyCapture('ppt', action)"
                    :type="capturingKey === `ppt-${action}` ? 'warning' : 'primary'"
                  >
                    {{ capturingKey === `ppt-${action}` ? '请按键...' : '修改' }}
                  </el-button>
                </template>
              </el-input>
            </el-form-item>
          </el-form>
          
          <div class="action-buttons">
            <el-button @click="resetPPTConfig" type="warning">恢复默认配置</el-button>
          </div>
        </el-card>
      </el-tab-pane>
      
      <!-- 视频控制配置 -->
      <el-tab-pane label="视频控制配置" name="video">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>视频手势映射配置</span>
              <el-button type="primary" @click="saveVideoConfig">保存配置</el-button>
            </div>
          </template>
          
          <el-form :model="videoConfig" label-width="150px">
            <h3>手势映射</h3>
            <el-form-item 
              v-for="(action, gesture) in videoConfig.gestures" 
              :key="gesture"
              :label="gesture"
            >
              <el-select v-model="videoConfig.gestures[gesture]" placeholder="选择操作">
                <el-option label="播放" value="play" />
                <el-option label="暂停" value="pause" />
                <el-option label="重新开始" value="restart" />
                <el-option label="进入全屏" value="fullscreen" />
                <el-option label="退出全屏" value="exit_fullscreen" />
                <el-option label="音量增加" value="volume_up" />
                <el-option label="音量减少" value="volume_down" />
                <el-option label="后退" value="seek_backward" />
                <el-option label="前进" value="seek_forward" />
                <el-option label="加速" value="speed_up" />
                <el-option label="减速" value="speed_down" />
              </el-select>
            </el-form-item>
            
            <el-divider />
            
            <h3>键盘快捷键映射</h3>
            <el-form-item 
              v-for="(key, action) in videoConfig.keyboard_shortcuts" 
              :key="action"
              :label="getActionName(action, 'video')"
            >
              <el-input 
                v-model="videoConfig.keyboard_shortcuts[action]" 
                placeholder="点击修改按钮后按下按键"
                readonly
              >
                <template #append>
                  <el-button 
                    @click="startKeyCapture('video', action)"
                    :type="capturingKey === `video-${action}` ? 'warning' : 'primary'"
                  >
                    {{ capturingKey === `video-${action}` ? '请按键...' : '修改' }}
                  </el-button>
                </template>
              </el-input>
            </el-form-item>
          </el-form>
          
          <div class="action-buttons">
            <el-button @click="resetVideoConfig" type="warning">恢复默认配置</el-button>
          </div>
        </el-card>
      </el-tab-pane>
      
      <!-- 系统信息 -->
      <el-tab-pane label="系统信息" name="info">
        <el-card>
          <template #header>
            <span>系统信息</span>
          </template>
          
          <el-descriptions :column="1" border>
            <el-descriptions-item label="系统名称">
              手势控制系统
            </el-descriptions-item>
            <el-descriptions-item label="版本">
              v1.0.0
            </el-descriptions-item>
            <el-descriptions-item label="后端服务">
              <el-tag :type="backendStatus === 'ok' ? 'success' : 'danger'">
                {{ backendStatus === 'ok' ? '运行正常' : '连接失败' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="摄像头状态">
              <el-tag type="info">准备就绪</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="支持的静态手势">
              Open, Close, Pointer, OK, Peace, Thumbs Up, Thumbs Down, Quiet Coyote
            </el-descriptions-item>
            <el-descriptions-item label="支持的动态手势">
              Move Up, Move Down, Move Left, Move Right, Clockwise, Counter Clockwise
            </el-descriptions-item>
          </el-descriptions>
          
          <el-divider />
          
          <h3>使用说明</h3>
          <el-alert
            title="配置说明"
            type="info"
            :closable="false"
          >
            <ul style="margin: 10px 0; padding-left: 20px;">
              <li>手势映射：将识别到的手势映射到具体的操作</li>
              <li>键盘快捷键：设置键盘快捷键，支持手势和键盘混合操作</li>
              <li>配置修改后需要点击"保存配置"按钮才能生效</li>
              <li>如需恢复出厂设置，点击"恢复默认配置"按钮</li>
            </ul>
          </el-alert>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const activeTab = ref('ppt')
const backendStatus = ref('checking')
const capturingKey = ref(null) // 当前正在捕获的按键
const pptConfig = ref({
  gestures: {},
  keyboard_shortcuts: {}
})
const videoConfig = ref({
  gestures: {},
  keyboard_shortcuts: {}
})

// 检查后端服务状态
const checkBackendStatus = async () => {
  try {
    const response = await axios.get('/api/health')
    backendStatus.value = response.data.status
  } catch (error) {
    backendStatus.value = 'error'
  }
}

// 加载配置
const loadConfigs = async () => {
  try {
    // 加载PPT配置
    const pptResponse = await axios.get('/api/config?module=ppt')
    pptConfig.value = pptResponse.data
    
    // 加载视频配置
    const videoResponse = await axios.get('/api/config?module=video')
    videoConfig.value = videoResponse.data
  } catch (error) {
    console.error('加载配置失败:', error)
    ElMessage.error('加载配置失败')
  }
}

// 保存PPT配置
const savePPTConfig = async () => {
  try {
    await axios.post('/api/config', {
      module: 'ppt',
      config: pptConfig.value
    })
    ElMessage.success('PPT配置保存成功！请刷新PPT控制页面以应用新配置')
  } catch (error) {
    console.error('保存配置失败:', error)
    ElMessage.error('保存配置失败')
  }
}

// 保存视频配置
const saveVideoConfig = async () => {
  try {
    await axios.post('/api/config', {
      module: 'video',
      config: videoConfig.value
    })
    ElMessage.success('视频配置保存成功！请刷新视频控制页面以应用新配置')
  } catch (error) {
    console.error('保存配置失败:', error)
    ElMessage.error('保存配置失败')
  }
}

// 重置PPT配置
const resetPPTConfig = async () => {
  try {
    const response = await axios.post('/api/config/reset', {
      module: 'ppt'
    })
    pptConfig.value = response.data.config
    ElMessage.success('PPT配置已恢复默认')
  } catch (error) {
    console.error('重置配置失败:', error)
    ElMessage.error('重置配置失败')
  }
}

// 重置视频配置
const resetVideoConfig = async () => {
  try {
    const response = await axios.post('/api/config/reset', {
      module: 'video'
    })
    videoConfig.value = response.data.config
    ElMessage.success('视频配置已恢复默认')
  } catch (error) {
    console.error('重置配置失败:', error)
    ElMessage.error('重置配置失败')
  }
}

// 获取操作名称
const getActionName = (action, module) => {
  const pptActions = {
    'next_slide': '下一页',
    'prev_slide': '上一页',
    'first_slide': '第一页',
    'last_slide': '最后一页',
    'scroll_up': '向上滚动',
    'scroll_down': '向下滚动'
  }
  
  const videoActions = {
    'play': '播放',
    'pause': '暂停',
    'restart': '重新开始',
    'fullscreen': '进入全屏',
    'exit_fullscreen': '退出全屏',
    'volume_up': '音量增加',
    'volume_down': '音量减少',
    'seek_backward': '后退',
    'seek_forward': '前进',
    'speed_up': '加速',
    'speed_down': '减速'
  }
  
  return module === 'ppt' ? pptActions[action] : videoActions[action]
}

// 开始捕获按键
const startKeyCapture = (module, action) => {
  capturingKey.value = `${module}-${action}`
  ElMessage.info('请按下要设置的按键')
}

// 处理按键事件
const handleKeyDown = (event) => {
  if (capturingKey.value) {
    event.preventDefault()
    
    const [module, action] = capturingKey.value.split('-')
    
    // 获取按键名称
    let keyName = event.key
    
    // 特殊按键处理
    if (event.key === ' ') keyName = 'Space'
    if (event.key === 'ArrowUp') keyName = 'ArrowUp'
    if (event.key === 'ArrowDown') keyName = 'ArrowDown'
    if (event.key === 'ArrowLeft') keyName = 'ArrowLeft'
    if (event.key === 'ArrowRight') keyName = 'ArrowRight'
    if (event.key === 'PageUp') keyName = 'PageUp'
    if (event.key === 'PageDown') keyName = 'PageDown'
    if (event.key === 'Home') keyName = 'Home'
    if (event.key === 'End') keyName = 'End'
    
    // 组合键处理
    if (event.ctrlKey) keyName = 'Ctrl+' + keyName
    if (event.altKey) keyName = 'Alt+' + keyName
    if (event.shiftKey && event.key.length > 1) keyName = 'Shift+' + keyName
    
    // 更新配置
    if (module === 'ppt') {
      pptConfig.value.keyboard_shortcuts[action] = keyName
    } else if (module === 'video') {
      videoConfig.value.keyboard_shortcuts[action] = keyName
    }
    
    capturingKey.value = null
    ElMessage.success(`按键已设置为: ${keyName}`)
  }
}

onMounted(() => {
  checkBackendStatus()
  loadConfigs()
  
  // 添加键盘事件监听
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  // 移除键盘事件监听
  window.removeEventListener('keydown', handleKeyDown)
})
</script>

<style scoped>
.settings-view {
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 28px;
  color: #2c3e50;
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-form h3 {
  color: #2c3e50;
  margin: 20px 0 15px 0;
  font-size: 16px;
}

.action-buttons {
  margin-top: 20px;
  text-align: right;
}

.el-descriptions {
  margin-bottom: 20px;
}
</style>

