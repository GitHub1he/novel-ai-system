import axios from 'axios'
import type { User, Project, Chapter, PlotNode } from '../types'

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
    api.get<{ code: number; message: string; data: { projects: Project[]; total: number } }>('/projects/list', { params }),

  get: (id: number) =>
    api.get<{ code: number; message: string; data: Project }>(`/projects/detail/${id}`),

  create: (data: Partial<Project>) =>
    api.post<{ code: number; message: string; data: Project }>('/projects/create', data),

  update: (id: number, data: Partial<Project>) =>
    api.post<{ code: number; message: string; data: Project }>(`/projects/update/${id}`, data),

  delete: (id: number) =>
    api.post<{ code: number; message: string; data: null }>(`/projects/del/${id}`),
}

// 章节API
export const chapterApi = {
  list: (projectId: number) =>
    api.get<{ code: number; message: string; data: { chapters: Chapter[]; total: number } }>(`/chapters/list/${projectId}`),

  get: (id: number) =>
    api.get<{ code: number; message: string; data: Chapter }>(`/chapters/${id}`),

  create: (data: { project_id: number; title: string; chapter_number: number; outline?: string; summary?: string }) =>
    api.post<{ code: number; message: string; data: Chapter }>('/chapters/', data),

  update: (id: number, data: Partial<Chapter>) =>
    api.put<{ code: number; message: string; data: Chapter }>(`/chapters/${id}`, data),

  generate: (id: number, prompt: string) =>
    api.post<{ content: string; word_count: number }>(`/chapters/${id}/generate`, { prompt }),
}

// 人物API
export const characterApi = {
  list: (projectId: number) =>
    api.get<{ code: number; message: string; data: { characters: Character[]; total: number } }>(`/characters/list/${projectId}`),

  get: (id: number) =>
    api.get<{ code: number; message: string; data: Character }>(`/characters/detail/${id}`),

  create: (data: Partial<Character>) =>
    api.post<{ code: number; message: string; data: Character }>('/characters/create', data),

  update: (id: number, data: Partial<Character>) =>
    api.post<{ code: number; message: string; data: Character }>(`/characters/update/${id}`, data),

  delete: (id: number) =>
    api.post<{ code: number; message: string; data: null }>(`/characters/del/${id}`),
}

// 世界观设定API
export const worldSettingApi = {
  list: (projectId: number) =>
    api.get<{ code: number; message: string; data: { settings: WorldSetting[]; total: number } }>(`/world-settings/list/${projectId}`),

  get: (id: number) =>
    api.get<{ code: number; message: string; data: WorldSetting }>(`/world-settings/detail/${id}`),

  create: (data: Partial<WorldSetting>) =>
    api.post<{ code: number; message: string; data: WorldSetting }>('/world-settings/create', data),

  update: (id: number, data: Partial<WorldSetting>) =>
    api.post<{ code: number; message: string; data: WorldSetting }>(`/world-settings/update/${id}`, data),

  delete: (id: number) =>
    api.post<{ code: number; message: string; data: null }>(`/world-settings/del/${id}`),
}

// 情节节点API
export const plotNodeApi = {
  list: (projectId: number, params?: { plot_type?: string; importance?: string }) =>
    api.get<{ code: number; message: string; data: { plot_nodes: PlotNode[]; total: number } }>(`/plot-nodes/list/${projectId}`, { params }),

  create: (data: Partial<PlotNode>) =>
    api.post<{ code: number; message: string; data: PlotNode }>('/plot-nodes/', data),

  update: (id: number, data: Partial<PlotNode>) =>
    api.put<{ code: number; message: string; data: PlotNode }>(`/plot-nodes/${id}`, data),

  delete: (id: number) =>
    api.post<{ code: number; message: string; data: null }>(`/plot-nodes/${id}/delete`),
}

// 上下文分析API
export const contextAnalysisApi = {
  analyze: (data: { project_id: number; plot_direction?: string; previous_chapter_id?: number; chapter_number: number }) =>
    api.post<{ code: number; message: string; data: any }>('/chapters/analyze-context', data),
}

export default api
