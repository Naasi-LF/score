<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="sidebar-brand">
        <span class="brand-icon">📊</span>
        <div>
          <div class="brand-name">成绩分析系统</div>
          <div class="brand-ver">v2.0</div>
        </div>
      </div>
      <nav class="sidebar-nav">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: route.path === item.path }"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label">{{ item.label }}</span>
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <div class="user-row">
          <div class="user-avatar">{{ (auth.user?.username ?? 'U')[0].toUpperCase() }}</div>
          <span class="user-name">{{ auth.user?.username ?? '用户' }}</span>
        </div>
        <button class="logout-btn" @click="handleLogout">退出</button>
      </div>
    </aside>
    <div class="main-area">
      <header class="topbar">
        <div class="topbar-title">{{ currentLabel }}</div>
      </header>
      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const navItems = [
  { path: '/dashboard',  icon: '📈', label: '数据概览' },
  { path: '/students',   icon: '👥', label: '学生管理' },
  { path: '/prediction', icon: '🔮', label: '成绩预测' },
  { path: '/history',    icon: '📋', label: '预测历史' },
  { path: '/models',     icon: '🧪', label: '模型对比' },
]

const currentLabel = computed(() => navItems.find(n => n.path === route.path)?.label ?? '')

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.app-shell { display: flex; height: 100vh; overflow: hidden; }

.sidebar {
  width: 220px;
  background: #fff;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 16px;
  border-bottom: 1px solid #f0f0f0;
}
.brand-icon { font-size: 24px; }
.brand-name { font-size: 14px; font-weight: 700; color: #303133; }
.brand-ver { font-size: 11px; color: #909399; }

.sidebar-nav {
  flex: 1;
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 6px;
  text-decoration: none;
  color: #606266;
  font-size: 14px;
  transition: background 0.15s, color 0.15s;
}
.nav-item:hover { background: #f5f7fa; color: #409eff; }
.nav-item.active { background: #ecf5ff; color: #409eff; font-weight: 600; }
.nav-icon { font-size: 16px; width: 20px; text-align: center; }

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.user-row { display: flex; align-items: center; gap: 8px; }
.user-avatar {
  width: 28px; height: 28px;
  background: #409eff;
  color: #fff;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700;
}
.user-name { font-size: 13px; color: #303133; }
.logout-btn {
  font-size: 12px;
  color: #909399;
  background: none;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 4px 10px;
  cursor: pointer;
  transition: color 0.15s, border-color 0.15s;
}
.logout-btn:hover { color: #f56c6c; border-color: #f56c6c; }

.main-area { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

.topbar {
  height: 52px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  padding: 0 24px;
  flex-shrink: 0;
}
.topbar-title { font-size: 15px; font-weight: 600; color: #303133; }

.content { flex: 1; padding: 24px; overflow-y: auto; }
</style>
