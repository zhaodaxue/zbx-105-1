<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <div class="logo">🌾</div>
        <h2>丰收节临时摊位用电申报系统</h2>
        <p class="subtitle">乡镇丰收节筹备组 · 在线管理平台</p>
      </div>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        size="large"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="账号" :prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-button
          type="primary"
          :loading="loading"
          class="login-btn"
          @click="handleLogin"
        >
          登 录
        </el-button>
      </el-form>
      <el-divider>演示账号</el-divider>
      <div class="demo-accounts">
        <div class="account-row">
          <span class="role">摊主</span>
          <span class="cred">vendor1 / vendor123</span>
        </div>
        <div class="account-row">
          <span class="role">电工</span>
          <span class="cred">electrician1 / elec123</span>
        </div>
        <div class="account-row">
          <span class="role">筹备员</span>
          <span class="cred">planner1 / plan123</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)
const form = reactive({
  username: '',
  password: '',
})
const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const handleLogin = async () => {
  await formRef.value?.validate()
  loading.value = true
  try {
    await userStore.login(form.username, form.password)
    ElMessage.success('登录成功')
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (e) {
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-box {
  width: 420px;
  padding: 40px 36px 32px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.18);
}
.login-header {
  text-align: center;
  margin-bottom: 32px;
}
.logo {
  font-size: 56px;
  line-height: 1;
  margin-bottom: 12px;
}
.login-header h2 {
  margin: 0 0 6px;
  font-size: 22px;
  color: #303133;
}
.subtitle {
  margin: 0;
  font-size: 13px;
  color: #909399;
}
.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  margin-top: 8px;
}
.demo-accounts {
  font-size: 13px;
  color: #606266;
}
.account-row {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
}
.role {
  font-weight: 600;
  color: #409eff;
}
.cred {
  font-family: Menlo, Monaco, Consolas, monospace;
  color: #67c23a;
}
</style>
