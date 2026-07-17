import axios from 'axios'

// 在 Render 上前后端分离，通过环境变量指定 API 地址
// 本地开发时用相对路径（Vite proxy 会转发）
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1'

const api = axios.create({
  baseURL: apiBaseUrl,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

// Global error handler — dispatches custom event for toast notifications
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      '网络请求失败，请检查连接后重试'

    // Dispatch a custom event that the Toast component can listen to
    if (typeof window !== 'undefined') {
      window.dispatchEvent(
        new CustomEvent('api-error', {
          detail: {
            message,
            status: error.response?.status,
            url: error.config?.url,
          },
        })
      )
    }

    console.error(`[API Error] ${error.config?.url}: ${message}`)
    return Promise.reject(error)
  }
)

export default api
