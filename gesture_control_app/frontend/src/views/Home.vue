<template>
  <div class="home-view">
    <h1 class="page-title">欢迎使用手势控制系统</h1>
    
    <el-row :gutter="20" class="feature-cards">
      <el-col :xs="24" :sm="12" :md="8">
        <el-card shadow="hover" class="feature-card">
          <template #header>
            <div class="card-title">
              <el-icon size="24"><Document /></el-icon>
              <span>PPT控制</span>
            </div>
          </template>
          <div class="card-content">
            <p>使用手势控制PPT演示文稿，支持翻页、跳转等操作。</p>
            <el-button type="primary" @click="navigateTo('/ppt')" class="action-btn">
              开始使用
            </el-button>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="8">
        <el-card shadow="hover" class="feature-card">
          <template #header>
            <div class="card-title">
              <el-icon size="24"><VideoPlay /></el-icon>
              <span>视频控制</span>
            </div>
          </template>
          <div class="card-content">
            <p>通过手势控制视频播放、暂停、音量、进度等。</p>
            <el-button type="primary" @click="navigateTo('/video')" class="action-btn">
              开始使用
            </el-button>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="8">
        <el-card shadow="hover" class="feature-card">
          <template #header>
            <div class="card-title">
              <el-icon size="24"><Setting /></el-icon>
              <span>系统设置</span>
            </div>
          </template>
          <div class="card-content">
            <p>自定义手势映射和键盘快捷键配置。</p>
            <el-button type="primary" @click="navigateTo('/settings')" class="action-btn">
              前往设置
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 系统介绍 -->
    <el-card class="intro-card">
      <template #header>
        <h2>系统功能介绍</h2>
      </template>
      
      <el-row :gutter="20">
        <el-col :xs="24" :md="12">
          <h3>🤚 支持的静态手势</h3>
          <ul class="gesture-list">
            <li><span class="gesture-emoji">✋</span> <el-tag>Open</el-tag> - 张开手掌</li>
            <li><span class="gesture-emoji">✊</span> <el-tag>Close</el-tag> - 握拳</li>
            <li><span class="gesture-emoji">☝️</span> <el-tag>Pointer</el-tag> - 食指指向</li>
            <li><span class="gesture-emoji">👌</span> <el-tag>OK</el-tag> - OK手势</li>
            <li><span class="gesture-emoji">✌️</span> <el-tag>Peace</el-tag> - V字手势</li>
            <li><span class="gesture-emoji">👍</span> <el-tag>Thumbs Up</el-tag> - 大拇指向上</li>
            <li><span class="gesture-emoji">👎</span> <el-tag>Thumbs Down</el-tag> - 大拇指向下</li>
            <li><span class="gesture-emoji">🤘</span> <el-tag>Quiet Coyote</el-tag> - 摇滚手势</li>
          </ul>
        </el-col>
        
        <el-col :xs="24" :md="12">
          <h3>✋ 支持的动态手势</h3>
          <ul class="gesture-list">
            <li><span class="gesture-emoji">⬆️</span> <el-tag type="success">Move Up</el-tag> - 向上移动</li>
            <li><span class="gesture-emoji">⬇️</span> <el-tag type="success">Move Down</el-tag> - 向下移动</li>
            <li><span class="gesture-emoji">⬅️</span> <el-tag type="success">Move Left</el-tag> - 向左移动</li>
            <li><span class="gesture-emoji">➡️</span> <el-tag type="success">Move Right</el-tag> - 向右移动</li>
            <li><span class="gesture-emoji">🔃</span> <el-tag type="success">Clockwise</el-tag> - 顺时针旋转</li>
            <li><span class="gesture-emoji">🔄</span> <el-tag type="success">Counter Clockwise</el-tag> - 逆时针旋转</li>
          </ul>
        </el-col>
      </el-row>
    </el-card>

    <!-- 快速开始指南 -->
    <el-card class="guide-card">
      <template #header>
        <h2>快速开始指南</h2>
      </template>
      
      <el-steps :active="0" align-center>
        <el-step title="选择功能" description="选择PPT控制或视频控制"></el-step>
        <el-step title="启动摄像头" description="点击按钮启动摄像头"></el-step>
        <el-step title="执行手势" description="对着摄像头做出相应手势"></el-step>
        <el-step title="查看效果" description="观察PPT或视频的控制效果"></el-step>
      </el-steps>
    </el-card>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { Document, VideoPlay, Setting } from '@element-plus/icons-vue'

const router = useRouter()

const navigateTo = (path) => {
  router.push(path)
}
</script>

<style scoped>
.home-view {
  max-width: 1400px;
  margin: 0 auto;
}

.page-title {
  font-size: 32px;
  color: #2c3e50;
  margin-bottom: 30px;
  text-align: center;
}

.feature-cards {
  margin-bottom: 30px;
}

.feature-card {
  height: 100%;
  transition: transform 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.card-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.card-content p {
  color: #606266;
  line-height: 1.6;
  min-height: 48px;
}

.action-btn {
  width: 100%;
}

.intro-card,
.guide-card {
  margin-bottom: 30px;
}

.intro-card h3,
.guide-card h2 {
  color: #2c3e50;
  margin-bottom: 15px;
}

.gesture-list {
  list-style: none;
  padding: 0;
}

.gesture-list li {
  padding: 8px 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.gesture-emoji {
  font-size: 20px;
  min-width: 30px;
  text-align: center;
}

.el-steps {
  margin-top: 20px;
}
</style>

