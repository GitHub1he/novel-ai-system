import axios from 'axios'
import type { User, Project, Chapter } from '../types'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

// 请求拦截器
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

// 响应拦截器
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// 认证API
export const authApi = {
  register: (data: { username: string; email: string; password: string }) =>
    api.post<User>('/auth/register', data),

  login: (data: { username: string; password: string }) =>
    api.post<{ access_token: string; token_type: string }>('/auth/login', data),
}

// 项目API
export const projectApi = {
  list: (params?: { skip?: number; limit?: number }) =>
    api.get<{ projects: Project[]; total: number }>('/projects/', { params }),

  get: (id: number) =>
    api.get<Project>(`/projects/${id}`),

  create: (data: Partial<Project>) =>
    api.post<Project>('/projects/', data),

  update: (id: number, data: Partial<Project>) =>
    api.put<Project>(`/projects/${id}`, data),

  delete: (id: number) =>
    api.delete(`/projects/${id}`),
}

// 章节API
export const chapterApi = {
  create: (data: { project_id: number; title: string; chapter_number: number }) =>
    api.post<Chapter>('/chapters/', data),

  get: (id: number) =>
    api.get<Chapter>(`/chapters/${id}`),

  update: (id: number, data: Partial<Chapter>) =>
    api.put<Chapter>(`/chapters/${id}`, data),

  generate: (id: number, prompt: string) =>
    api.post<{ content: string; word_count: number }>(`/chapters/${id}/generate`, { prompt }),
}

export default api
