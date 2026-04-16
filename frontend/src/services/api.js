import axios from 'axios'

// Create axios instance with default config
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor - add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - unified error handling
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.error?.message || '请求失败'
    const code = error.response?.data?.error?.code || 'UNKNOWN_ERROR'
    
    console.error('API Error:', { message, code, error: error.response?.data })
    
    // Handle specific error codes
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to home
      localStorage.removeItem('token')
      window.location.href = '/'
    }
    
    return Promise.reject({ message, code })
  }
)

export default api
