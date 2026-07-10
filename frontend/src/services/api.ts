import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
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
