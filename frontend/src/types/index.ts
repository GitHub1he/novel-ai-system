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

export interface AdminUser extends User {
  project_count: number
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
  character_arcs?: Array<{
    period: string
    event: string
    before: string
    after: string
  }>
  voice_styles?: Array<{
    target: string
    scenario: string
    style: string
    sample: string
  }>
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
  display_summary?: string  // 展示摘要（用于页面显示）
  pov_character_id?: number
  featured_characters?: string
  locations?: string
  status: 'draft' | 'revising' | 'completed'
  word_count: number
  version: number
  created_at: string
  updated_at: string
  // 列表接口专用字段
  has_outline?: boolean
  has_content?: boolean
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

export interface PlotNode {
  id: number
  project_id: number
  title: string
  description?: string
  plot_type: 'meeting' | 'betrayal' | 'reconciliation' | 'conflict' | 'revelation' | 'transformation' | 'climax' | 'resolution' | 'other'
  importance: 'main' | 'branch' | 'background'
  chapter_id?: number
  related_characters?: string
  related_locations?: string
  related_world_settings?: string
  conflict_points?: string
  theme_tags?: string
  sequence_number: number
  parent_plot_id?: number
  is_completed: number
  created_at: string
  updated_at?: string
}

// Generation modes
export type GenerationMode = 'simple' | 'standard' | 'advanced';

// Request types
export interface FirstChapterMode {
  opening_scene: string
  key_elements: string[]
  tone?: string
}

export interface ContinueMode {
  previous_chapter_id: number
  transition: string
  plot_direction: string
  conflict_point?: string
}

export interface ChapterGenerateRequest {
  mode: GenerationMode
  project_id: number
  chapter_number: number
  first_chapter_mode?: FirstChapterMode
  continue_mode?: ContinueMode
  suggested_context?: {
    characters?: number[]
    world_settings?: number[]
    plot_nodes?: number[]
  }
  featured_characters?: number[]
  related_world_settings?: number[]
  related_plot_nodes?: number[]
  word_count?: number
  versions?: number
  style_intensity?: number
  pov_character_id?: number
  temperature?: number
}

export interface ChapterGenerateResponse {
  code: number
  message: string
  data: {
    chapter_id: number
    task_id?: string
    versions: GeneratedVersion[]
    context_used: any
  }
}

export interface GeneratedVersion {
  version_id: string
  content: string
  summary: string
  word_count: number
}
