import { defineStore } from 'pinia'
import request from '@/utils/request'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('access_token') || '',
    userInfo: JSON.parse(localStorage.getItem('user_info') || 'null'),
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
    role: (state) => state.userInfo?.role || '',
    isVendor: (state) => state.userInfo?.role === 'vendor',
    isElectrician: (state) => state.userInfo?.role === 'electrician',
    isPlanner: (state) => state.userInfo?.role === 'planner',
    fullName: (state) => state.userInfo?.full_name || '',
  },
  actions: {
    async login(username, password) {
      const res = await request.post('/auth/login', { username, password })
      this.token = res.access_token
      localStorage.setItem('access_token', res.access_token)
      await this.fetchProfile()
      return res
    },
    async fetchProfile() {
      const res = await request.get('/auth/me')
      this.userInfo = res
      localStorage.setItem('user_info', JSON.stringify(res))
      return res
    },
    logout() {
      this.token = ''
      this.userInfo = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_info')
    },
  },
})
