<template>
  <div class="login-wrap">
    <div class="login-box">
      <div class="brand">
        <div class="brand-icon">📊</div>
        <div class="brand-title">学生成绩分析与预测系统</div>
        <div class="brand-sub">Student Score Analysis System</div>
      </div>
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="field">
          <label class="field-label">用户名</label>
          <input v-model="form.username" class="field-input" placeholder="请输入用户名" autocomplete="username" />
        </div>
        <div class="field">
          <label class="field-label">密码</label>
          <input v-model="form.password" class="field-input" type="password" placeholder="请输入密码" autocomplete="current-password" />
        </div>
        <button type="submit" class="login-btn" :disabled="loading">
          {{ loading ? '登录中...' : '登 录' }}
        </button>
        <div v-if="error" class="error-msg">{{ error }}</div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const auth = useAuthStore()
const router = useRouter()
const loading = ref(false)
const error = ref('')
const form = reactive({ username: '', password: '' })

async function handleLogin() {
  loading.value = true
  error.value = ''
  try {
    await auth.login(form.username, form.password)
    router.push('/dashboard')
  } catch {
    error.value = '用户名或密码错误，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrap {
  min-height: 100vh;
  background: linear-gradient(135deg, #e8f4fd 0%, #f0f2f5 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-box {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.1);
  padding: 48px 40px;
  width: 380px;
}

.brand {
  text-align: center;
  margin-bottom: 36px;
}
.brand-icon { font-size: 40px; margin-bottom: 12px; }
.brand-title { font-size: 18px; font-weight: 700; color: #303133; margin-bottom: 4px; }
.brand-sub { font-size: 12px; color: #909399; }

.login-form { display: flex; flex-direction: column; gap: 16px; }

.field { display: flex; flex-direction: column; gap: 6px; }
.field-label { font-size: 13px; font-weight: 500; color: #606266; }
.field-input {
  padding: 10px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
  color: #303133;
  outline: none;
  transition: border-color 0.2s;
}
.field-input:focus { border-color: #409eff; }

.login-btn {
  margin-top: 8px;
  padding: 12px;
  background: #409eff;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}
.login-btn:hover:not(:disabled) { background: #337ecc; }
.login-btn:disabled { opacity: 0.7; cursor: not-allowed; }

.error-msg {
  font-size: 13px;
  color: #f56c6c;
  text-align: center;
}
</style>
