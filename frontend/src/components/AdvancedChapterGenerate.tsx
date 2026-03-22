import { useState, useEffect } from 'react'
import { Modal, Form, Input, InputNumber, Select, Slider, Button, Space, Divider, Typography, Tag, Switch, Radio, message } from 'antd'
import { PlusOutlined } from '@ant-design/icons'
import type { ChapterGenerateRequest, Character, WorldSetting } from '../types'

const { TextArea } = Input
const { Text, Title } = Typography

interface AdvancedChapterGenerateProps {
  visible: boolean
  onClose: () => void
  onGenerate: (config: ChapterGenerateRequest) => void
  project: any
  chapters: any[]
  characters: Character[]
  worldSettings: WorldSetting[]
  loading?: boolean
  initialContext?: {  // 新增：上下文分析的选择
    characters: number[]
    world_settings: number[]
    plot_nodes: number[]
    previousChapterSummary?: string
  }
}

const AdvancedChapterGenerate: React.FC<AdvancedChapterGenerateProps> = ({
  visible,
  onClose,
  onGenerate,
  project,
  chapters,
  characters,
  worldSettings,
  loading = false,
  initialContext
}) => {
  const [form] = Form.useForm()

  const [generationMode, setGenerationMode] = useState<'standard' | 'first_chapter' | 'continue'>('standard')

  // 当接收到 initialContext 时，预填充表单
  useEffect(() => {
    if (initialContext && visible) {
      form.setFieldsValue({
        featured_characters: initialContext.characters,
        related_world_settings: initialContext.world_settings,
        related_plot_nodes: initialContext.plot_nodes,
        // 如果有前文摘要，可以设置到 prompt 中
        prompt: initialContext.previousChapterSummary
          ? `前文总结：\n${initialContext.previousChapterSummary}\n\n请根据以上前文内容续写：`
          : undefined
      })
      message.info('✅ 已应用上下文分析的设定')
    }
  }, [initialContext, visible, form])

  const handleGenerate = async () => {
    try {
      const values = await form.validateFields()
      // 确保 project_id 被包含
      const requestData = {
        ...values,
        project_id: project?.id
      }
      onGenerate(requestData)
    } catch (error) {
      console.error('表单验证失败:', error)
    }
  }

  return (
    <Modal
      title={
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span>🎨</span>
          <span>高级章节生成</span>
        </div>
      }
      open={visible}
      onCancel={onClose}
      onOk={handleGenerate}
      okText="开始生成"
      cancelText="取消"
      width={700}
      okButtonProps={{ loading, icon: <PlusOutlined /> }}
      styles={{
        body: { padding: '24px' }
      }}
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          mode: 'standard',
          project_id: project?.id,
          chapter_number: (chapters?.length || 0) + 1,
          versions: 3,
          word_count: project?.target_words_per_chapter || 2000,
          temperature: 0.8,
          style_intensity: 70,
          featured_characters: [],
          related_world_settings: []
        }}
      >
        {/* 基础配置 */}
        <Title level={5}>📝 基础配置</Title>

        <Form.Item label="章节号" name="chapter_number" rules={[{ required: true, message: '请输入章节号' }]}>
          <InputNumber style={{ width: '100%' }} min={1} placeholder="第几章" />
        </Form.Item>

        <Form.Item label="生成模式" name="mode" rules={[{ required: true }]}>
          <Radio.Group onChange={(e) => setGenerationMode(e.target.value)}>
            <Radio.Button value="standard">标准模式</Radio.Button>
            <Radio.Button value="first_chapter">首章模式</Radio.Button>
            <Radio.Button value="continue">续写模式</Radio.Button>
          </Radio.Group>
        </Form.Item>

        {/* 首章模式配置 */}
        {generationMode === 'first_chapter' && (
          <>
            <Divider />
            <Title level={5}>🌟 首章配置</Title>
            <Form.Item
              label="开篇场景"
              name={['first_chapter_mode', 'opening_scene']}
              rules={[{ required: true, message: '请描述开篇场景' }]}
            >
              <TextArea
                rows={3}
                placeholder="例如：风雨交加的夜晚，主角独自走在荒凉的小路上..."
              />
            </Form.Item>

            <Form.Item
              label="核心要素"
              name={['first_chapter_mode', 'key_elements']}
              tooltip="用逗号分隔，例如：悬念,冲突,氛围"
            >
              <Select
                mode="tags"
                placeholder="选择或输入核心要素"
                options={[
                  { label: '悬念', value: '悬念' },
                  { label: '冲突', value: '冲突' },
                  { label: '氛围', value: '氛围' },
                  { label: '人物介绍', value: '人物介绍' },
                  { label: '世界观展示', value: '世界观展示' },
                  { label: '伏笔', value: '伏笔' }
                ]}
              />
            </Form.Item>

            <Form.Item
              label="开篇基调"
              name={['first_chapter_mode', 'tone']}
            >
              <Select
                placeholder="选择开篇基调"
                options={[
                  { label: '悬疑', value: '悬疑' },
                  { label: '轻松', value: '轻松' },
                  { label: '史诗', value: '史诗' },
                  { label: '黑暗', value: '黑暗' },
                  { label: '温馨', value: '温馨' },
                  { label: '紧张', value: '紧张' }
                ]}
              />
            </Form.Item>
          </>
        )}

        {/* 续写模式配置 */}
        {generationMode === 'continue' && (
          <>
            <Divider />
            <Title level={5}>📖 续写配置</Title>
            <Form.Item
              label="上一章"
              name={['continue_mode', 'previous_chapter_id']}
              rules={[{ required: true, message: '请选择上一章' }]}
            >
              <Select
                placeholder="选择上一章"
                options={chapters?.map(ch => ({
                  label: `第${ch.chapter_number}章：${ch.title}`,
                  value: ch.id
                })) || []}
              />
            </Form.Item>

            <Form.Item
              label="衔接方式"
              name={['continue_mode', 'transition']}
            >
              <Select
                placeholder="选择衔接方式"
                options={[
                  { label: '直接衔接', value: 'immediate' },
                  { label: '时间跳跃', value: 'time_skip' },
                  { label: '场景切换', value: 'location_change' },
                  { label: '摘要过渡', value: 'summary' }
                ]}
              />
            </Form.Item>

            <Form.Item
              label="本章情节方向"
              name={['continue_mode', 'plot_direction']}
              rules={[{ required: true, message: '请描述情节方向' }]}
            >
              <TextArea
                rows={3}
                placeholder="例如：主角根据线索找到神秘地点，遭遇埋伏，发现隐藏的真相..."
              />
            </Form.Item>

            <Form.Item
              label="核心冲突点"
              name={['continue_mode', 'conflict_point']}
            >
              <TextArea
                rows={2}
                placeholder="例如：与反派的正面冲突，内心的道德挣扎..."
              />
            </Form.Item>
          </>
        )}

        {/* 高级控制 */}
        <Divider />
        <Title level={5}>⚙️ 高级控制</Title>

        <Form.Item label={<Space><span>生成版本数量</span><Tag color="blue">1-5个版本</Tag></Space>}>
          <Form.Item name="versions" noStyle>
            <Slider min={1} max={5} marks={{ 1: '1', 3: '3', 5: '5' }} />
          </Form.Item>
        </Form.Item>

        <Form.Item
          label={<Space><span>目标字数</span><Tag color="green">{project?.target_words_per_chapter || 2000}字</Tag></Space>}
          name="word_count"
        >
          <Slider min={1000} max={10000} step={500} marks={{ 1000: '1千', 2000: '2千', 5000: '5千', 10000: '1万' }} />
        </Form.Item>

        <Form.Item
          label={<Space><span>创造性参数</span><Tag color="purple">0.8</Tag></Space>}
          name="temperature"
          tooltip="越高越有创造性，但可能偏离设定"
        >
          <Slider min={0.1} max={1.5} step={0.1} marks={{ 0.1: '保守', 0.8: '标准', 1.5: '大胆' }} />
        </Form.Item>

        <Form.Item
          label={<Space><span>风格强度</span><Tag color="orange">70%</Tag></Space>}
          name="style_intensity"
          tooltip="遵循设定的程度"
        >
          <Slider min={0} max={100} marks={{ 0: '自由', 70: '标准', 100: '严格' }} />
        </Form.Item>

        {/* 人物和世界观 */}
        <Divider />
        <Title level={5}>👥 相关设定</Title>

        <Form.Item label="登场人物" name="featured_characters" tooltip="选择会在本章登场的人物">
          <Select
            mode="multiple"
            placeholder="选择登场人物"
            options={characters?.map(c => {
              const roleMap: Record<string, string> = {
                'protagonist': '主角',
                'antagonist': '反派',
                'supporting': '配角',
                'minor': '次要角色'
              }
              return {
                label: `${c.name} (${roleMap[c.role] || '未知'})`,
                value: c.id
              }
            }) || []}
            maxTagCount="responsive"
            optionFilterProp="label"
          />
        </Form.Item>

        <Form.Item label="相关世界观设定" name="related_world_settings" tooltip="选择本章相关的世界观设定">
          <Select
            mode="multiple"
            placeholder="选择世界观设定"
            options={worldSettings?.map(s => {
              const typeMap: Record<string, string> = {
                'era': '时代背景',
                'region': '地域设定',
                'rule': '核心规则',
                'culture': '文化习俗',
                'power': '权力结构',
                'location': '重要地点',
                'faction': '势力组织',
                'item': '重要物品',
                'event': '历史事件'
              }
              return {
                label: `${s.name} (${typeMap[s.setting_type] || s.setting_type})`,
                value: s.id
              }
            }) || []}
            maxTagCount="responsive"
            optionFilterProp="label"
          />
        </Form.Item>

        <Form.Item label="叙事视角人物" name="pov_character_id" tooltip="选择本章的叙事视角">
          <Select
            allowClear
            placeholder="选择叙事视角人物"
            showSearch
            options={characters
              ?.filter(c => c.role === 'protagonist' || c.role === 'supporting')
              .map(c => ({
                label: c.name,
                value: c.id
              })) || []}
            optionFilterProp="label"
          />
        </Form.Item>

        {/* 提示词 */}
        <Divider />
        <Form.Item
          label="💡 用户提示词"
          name="prompt"
          tooltip="额外的要求或提示"
        >
          <TextArea
            rows={4}
            placeholder="例如：重点描写主角的内心活动，营造紧张的氛围..."
          />
        </Form.Item>

        <div style={{ background: '#f0f5ff', padding: '12px', borderRadius: '6px', marginTop: '16px' }}>
          <Text type="secondary" style={{ fontSize: '12px' }}>
            💡 <strong>提示：</strong> 生成多个版本可以让你选择最满意的内容。每个版本会使用不同的创造性参数，会有不同的风格和细节。
          </Text>
        </div>
      </Form>
    </Modal>
  )
}

export default AdvancedChapterGenerate
