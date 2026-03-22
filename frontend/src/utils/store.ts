import { create } from 'zustand'
import type { User, Project } from '../types'

interface AuthState {
  user: User | null
  token: string | null
  setAuth: (user: User, token: string) => void
  logout: () => void
}

interface ProjectState {
  currentProject: Project | null
  projects: Project[]
  setCurrentProject: (project: Project | null) => void
  setProjects: (projects: Project[]) => void
}

export const useAuthStore = create<AuthState>((set) => {
  // 从 localStorage 恢复用户信息
  const token = localStorage.getItem('token')
  let user = null

  if (token) {
    try {
      // 解码 JWT token 获取用户信息
      const base64Url = token.split('.')[1]
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
      const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
      }).join(''))
      const payload = JSON.parse(jsonPayload)

      user = {
        id: payload.sub || 0,
        username: payload.sub,
        email: payload.sub + "@example.com",
        is_admin: payload.is_admin || 0,
        is_active: 1,
        created_at: new Date().toISOString()
      }
    } catch (error) {
      console.error('Failed to decode token:', error)
      localStorage.removeItem('token')
    }
  }

  return {
    user,
    token,
    setAuth: (user, token) => {
      localStorage.setItem('token', token)
      set({ user, token })
    },
    logout: () => {
      localStorage.removeItem('token')
      set({ user: null, token: null })
    },
  }
})

export const useProjectStore = create<ProjectState>((set) => ({
  currentProject: null,
  projects: [],
  setCurrentProject: (project) => set({ currentProject: project }),
  setProjects: (projects) => set({ projects }),
}))
