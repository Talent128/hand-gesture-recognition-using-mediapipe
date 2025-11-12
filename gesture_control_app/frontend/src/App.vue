<template>
  <div id="app" class="app-container">
    <el-container>
      <!-- 侧边栏导航 -->
      <el-aside width="200px" class="sidebar">
        <div class="logo">
          <h2>手势控制</h2>
        </div>
        <el-menu
          :default-active="$route.path"
          router
          class="sidebar-menu"
          background-color="#2c3e50"
          text-color="#ecf0f1"
          active-text-color="#3498db"
        >
          <el-menu-item index="/">
            <el-icon><House /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/ppt">
            <el-icon><Document /></el-icon>
            <span>PPT控制</span>
          </el-menu-item>
          <el-menu-item index="/video">
            <el-icon><VideoPlay /></el-icon>
            <span>视频控制</span>
          </el-menu-item>
          <el-menu-item index="/settings">
            <el-icon><Setting /></el-icon>
            <span>设置</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区 -->
      <el-container>
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { House, Document, VideoPlay, Setting } from '@element-plus/icons-vue'
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
  width: 100%;
}

.app-container {
  height: 100%;
  width: 100%;
}

.el-container {
  height: 100%;
}

.sidebar {
  background-color: #2c3e50;
  height: 100vh;
}

.logo {
  padding: 20px;
  text-align: center;
  color: #ecf0f1;
  border-bottom: 1px solid #34495e;
}

.logo h2 {
  font-size: 20px;
  font-weight: 600;
}

.sidebar-menu {
  border-right: none;
}

.main-content {
  background-color: #ecf0f1;
  padding: 20px;
  overflow-y: auto;
}
</style>

