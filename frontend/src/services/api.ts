import axios from 'axios'
import type { User, Project, Chapter, PlotNode, WorldSetting, Character, ChapterGenerateRequest, AdminUser } from '../types'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000, // AI 生成需要更长时间，增加到 60 秒
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    // 调试日志
    console.log('=== 发送 API 请求 ===')
    console.log('URL:', config.url)
    console.log('Method:', config.method)
    console.log('Headers:', config.headers)
    console.log('Token 存在:', !!token)
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
      // 清除token
      localStorage.removeItem('token')
      // 显示友好提示
      // 注意：这里不能直接使用 message，因为会形成循环依赖
      // 改为使用 console 或 window.location 直接跳转
      console.warn('登录已过期，请重新登录')
      // 延迟跳转
      setTimeout(() => {
        window.location.href = '/login'
      }, 500)
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

  delete: (id: number) =>
    api.delete<{ code: number; message: string; data: null }>(`/chapters/${id}`),

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

// 管理员API
export const adminApi = {
  // 获取所有用户
  getUsers: (params?: { skip?: number; limit?: number }) =>
    api.get<{ code: number; message: string; data: { users: AdminUser[]; total: number } }>('/admin/users', { params }),

  // 切换用户管理员权限
  toggleAdmin: (userId: number) =>
    api.post<{ code: number; message: string; data: AdminUser }>(`/admin/users/${userId}/toggle-admin`),

  // 启用/禁用用户
  toggleActive: (userId: number) =>
    api.post<{ code: number; message: string; data: AdminUser }>(`/admin/users/${userId}/toggle-active`),

  // 获取所有项目
  getAllProjects: (params?: { skip?: number; limit?: number }) =>
    api.get<{ code: number; message: string; data: { projects: Project[]; total: number } }>('/admin/projects', { params }),

  // 获取系统统计
  getStats: () =>
    api.get<{ code: number; message: string; data: { user_count: number; admin_count: number; project_count: number; chapter_count: number } }>('/admin/stats'),
}

// 上下文分析API
export const contextAnalysisApi = {
  analyze: (params: { project_id: number; plot_direction: string; previous_chapter_id?: number; chapter_number: number }) =>
    api.post<{ code: number; message: string; data: any }>('/chapters/analyze-context', params),
}

// 统一生成API
export const generateChapterApi = {
  generate: async (params: ChapterGenerateRequest) => {
    const token = localStorage.getItem('token')
    const response = await axios.post(
      `${api.defaults.baseURL}/api/chapters/generate`,
      params,
      { headers: { Authorization: `Bearer ${token}` } }
    )
    return response.data
  }
}

// 版本选择API
export const versionApi = {
  selectVersion: async (chapterId: number, params: { version_id: string; edited_content?: string }) => {
    const token = localStorage.getItem('token')
    const response = await axios.post(
      `${api.defaults.baseURL}/api/chapters/${chapterId}/select-version`,
      params,
      { headers: { Authorization: `Bearer ${token}` } }
    )
    return response.data
  },

  getDrafts: async (chapterId: number) => {
    const token = localStorage.getItem('token')
    const response = await axios.get(
      `${api.defaults.baseURL}/api/chapters/${chapterId}/drafts`,
      { headers: { Authorization: `Bearer ${token}` } }
    )
    return response.data
  }
}

/**
 * 检测章节中的实体（不保存）
 * @param chapterId 章节 ID
 * @returns 检测到的实体列表
 */
export const detectEntitiesFromChapter = async (chapterId: number) => {
  const response = await api.get(`/chapters/${chapterId}/detect-entities`)
  return response.data
}

/**
 * 批量创建实体
 * @param chapterId 章节 ID
 * @param characters 要创建的人物列表
 * @param worldSettings 要创建的世界观设定列表
 * @returns 创建结果
 */
export const createEntities = async (
  chapterId: number,
  characters: any[],
  worldSettings: any[]
) => {
  const response = await api.post(`/chapters/${chapterId}/create-entities`, {
    characters,
    world_settings: worldSettings
  })
  return response.data
}

export default api
