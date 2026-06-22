import axios from 'axios'
import { ElMessage } from 'element-plus'

const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '/api',
  timeout: 30000,
})

service.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

service.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      if (status === 401) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('user_info')
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
        ElMessage.error('登录已过期，请重新登录')
      } else if (status === 403) {
        ElMessage.error('权限不足，禁止访问')
      } else if (status === 404) {
        ElMessage.error(`请求的资源不存在 (404)：${error.config?.url || ''}`)
      } else if (status === 422) {
        const details = data?.detail
        let msg = '请求参数校验失败'
        if (Array.isArray(details) && details.length) {
          const first = details[0]
          const loc = (first.loc || []).filter(p => p !== 'body').join('.')
          msg = `${loc ? loc + '：' : ''}${first.msg || '参数错误'}`
        } else if (typeof details === 'string') {
          msg = details
        }
        ElMessage.error(msg)
      } else if (status >= 500) {
        ElMessage.error(`服务器内部错误 (${status})，请联系管理员或稍后重试`)
      } else {
        const msg = data?.detail || data?.message || `请求失败 (${status})`
        ElMessage.error(typeof msg === 'string' ? msg : JSON.stringify(msg))
      }
    } else if (error.request) {
      const isTimeout = error.code === 'ECONNABORTED' || /timeout/i.test(error.message)
      const url = error.config?.url || ''
      if (isTimeout) {
        ElMessage.error(`请求超时（30秒未响应），请稍后重试\n${url}`)
      } else if (error.message && /Network Error/i.test(error.message)) {
        ElMessage.error(`无法连接到后端服务\n请确认 API 服务已启动或检查网络配置\nURL: ${url || error.config?.baseURL || ''}`)
      } else if (error.code === 'ERR_CANCELED') {
        ElMessage.warning('请求已取消')
      } else {
        ElMessage.error(`请求失败：${error.message || '未知网络错误'}\n${url}`)
      }
    } else {
      ElMessage.error(`请求异常：${error.message || '未知错误'}`)
    }
    return Promise.reject(error)
  }
)

export default service
