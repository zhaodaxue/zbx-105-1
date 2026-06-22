<template>
  <el-container class="layout-container">
    <el-aside width="230px" class="aside">
      <div class="logo-area">
        <span class="logo-icon">🌾</span>
        <span class="logo-text">丰收节申报系统</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        class="side-menu"
        background-color="transparent"
        text-color="#dcdfe6"
        active-text-color="#fff"
      >
        <el-menu-item index="/dashboard">
          <el-icon><House /></el-icon>
          <span>工作台</span>
        </el-menu-item>
        <el-menu-item index="/applications">
          <el-icon><Document /></el-icon>
          <span>用电申报</span>
        </el-menu-item>
        <el-menu-item v-if="userStore.isVendor" index="/applications/create">
          <el-icon><Edit /></el-icon>
          <span>提交申报</span>
        </el-menu-item>
        <el-menu-item v-if="userStore.isElectrician" index="/review">
          <el-icon><Check /></el-icon>
          <span>审核管理</span>
        </el-menu-item>
        <el-menu-item v-if="userStore.isPlanner || userStore.isElectrician" index="/stats">
          <el-icon><DataAnalysis /></el-icon>
          <span>统计摘要</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <span class="page-title">{{ pageTitle }}</span>
        </div>
        <div class="header-right">
          <el-tag size="large" :type="roleTagType" effect="dark" class="role-tag">
            {{ roleLabel }}
          </el-tag>
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-icon class="user-icon"><UserFilled /></el-icon>
              <span>{{ userStore.fullName }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)
const pageTitle = computed(() => route.meta.title || '')

const roleLabel = computed(() => {
  const map = { vendor: '摊主', electrician: '电工', planner: '筹备员' }
  return map[userStore.role] || '未知'
})
const roleTagType = computed(() => {
  const map = { vendor: 'success', electrician: 'warning', planner: 'primary' }
  return map[userStore.role] || 'info'
})

const handleCommand = (cmd) => {
  if (cmd === 'logout') {
    userStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}
.aside {
  background: #1f2937;
  color: #fff;
  overflow: hidden;
}
.logo-area {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-bottom: 1px solid #374151;
}
.logo-icon {
  font-size: 24px;
}
.logo-text {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}
.side-menu {
  border-right: none !important;
}
.side-menu :deep(.el-menu-item) {
  height: 50px;
  line-height: 50px;
}
.side-menu :deep(.el-menu-item.is-active) {
  background: #409eff !important;
}
.header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 60px !important;
}
.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.role-tag {
  font-size: 13px;
}
.user-info {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  color: #606266;
  font-size: 14px;
  padding: 4px 8px;
  border-radius: 4px;
}
.user-info:hover {
  background: #f5f7fa;
}
.user-icon {
  color: #409eff;
}
.main {
  background: #f5f7fa;
  overflow-y: auto;
  padding: 20px 24px;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
