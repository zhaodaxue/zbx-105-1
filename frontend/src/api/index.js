import request from '@/utils/request'

export const loginApi = (data) => request.post('/auth/login', data)
export const getProfileApi = () => request.get('/auth/me')

export const listApplicationsApi = (params) => request.get('/applications', { params })
export const getApplicationApi = (id) => request.get(`/applications/${id}`)
export const createApplicationApi = (data) => request.post('/applications', data)
export const reviewApplicationApi = (id, data) => request.put(`/applications/${id}/review`, data)

export const getDailyStatsApi = (params) => request.get('/stats/daily', { params })
export const exportCsvApi = (params) => {
  const token = localStorage.getItem('access_token')
  const query = new URLSearchParams(params || {}).toString()
  const base = (import.meta.env.VITE_API_BASE || '/api')
  const url = `${base}/stats/export-csv${query ? '?' + query : ''}`
  const link = document.createElement('a')
  link.href = url
  link.target = '_blank'
  link.setAttribute('download', '')
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
