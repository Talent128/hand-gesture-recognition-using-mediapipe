import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.DEV ? '/api' : 'http://localhost:5000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    console.log('发送请求:', config.method.toUpperCase(), config.url)
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    console.log('收到响应:', response.status, response.config.url)
    return response
  },
  error => {
    if (error.code === 'ECONNABORTED') {
      console.error('请求超时:', error.config.url)
    } else if (error.response) {
      console.error('服务器错误:', error.response.status, error.response.data)
    } else if (error.request) {
      console.error('网络错误: 无法连接到服务器')
    } else {
      console.error('请求配置错误:', error.message)
    }
    return Promise.reject(error)
  }
)

export default api

