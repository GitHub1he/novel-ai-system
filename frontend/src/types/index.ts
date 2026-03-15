export interface User {
  id: number
  email: string
  username: string
  phone?: string
  avatar?: string
  preferred_genre?: string
  is_admin: number
  is_active: number
  created_at: string
}

export interface Project {
  id: number
  user_id: number
  title: string
  author: string
  genre: string
  tags?: string
  summary?: string
  target_readers?: string
  status: 'draft' | 'writing' | 'completed' | 'archived'
  default_pov?: string
  style?: string
  target_words_per_chapter: number
  background_template?: string
  total_words: number
  total_chapters: number
  completion_rate: number
  created_at: string
  updated_at: string
}

export interface Character {
  id: number
  project_id: number
  name: string
  age?: number
  gender?: string
  appearance?: string
  identity?: string
  hometown?: string
  role: 'protagonist' | 'antagonist' | 'supporting' | 'minor'
  personality?: string
  core_motivation?: string
  fears?: string
  desires?: string
  initial_state?: string
  turning_point?: string
  final_state?: string
  speech_style?: string
  sample_dialogue?: string
  avatar?: string
  appearance_count: number
  created_at: string
  updated_at: string
}

export interface Chapter {
  id: number
  project_id: number
  chapter_number: number
  title: string
  volume?: string
  content?: string
  outline?: string
  summary?: string
  pov_character_id?: number
  featured_characters?: string
  locations?: string
  status: 'draft' | 'revising' | 'completed'
  word_count: number
  version: number
  created_at: string
  updated_at: string
}

export interface WorldSetting {
  id: number
  project_id: number
  name: string
  setting_type: 'era' | 'region' | 'rule' | 'culture' | 'power' | 'location' | 'faction' | 'item' | 'event'
  description?: string
  attributes?: Record<string, any>
  related_entities?: number[]
  is_core_rule: number
  image?: string
  created_at: string
  updated_at: string
}
