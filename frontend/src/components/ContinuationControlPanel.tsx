import React, { useState } from 'react'
import {
  Card,
  Radio,
  Input,
  Button,
  Slider,
  InputNumber,
  Space,
  Typography,
  Divider,
  Form
} from 'antd'
import { RobotOutlined, BulbOutlined } from '@ant-design/icons'

const { TextArea } = Input
const { Text } = Typography

interface ContinuationControlPanelProps {
  chapterNumber: number
  onGenerate: (params: any) => Promise<void>
  generating: boolean
}

// Mode descriptions for user guidance
const MODE_DESCRIPTIONS = {
  simple: '简单模式：仅提供基本续写指令，AI自动处理细节',
  standard: '标准模式：提供明确的情节方向和字数要求',
  advanced: '高级模式：全面控制续写要素，包括冲突点等细节'
}

// First chapter mode options
const FIRST_CHAPTER_MODES = [
  { value: 'opening_scene', label: '开场场景' },
  { value: 'key_elements', label: '关键要素' },
  { value: 'tone', label: '整体基调' }
]

// Continue mode options
const CONTINUE_MODES = [
  { value: 'plot_direction', label: '情节方向' },
  { value: 'conflict_point', label: '冲突点' }
]

const ContinuationControlPanel: React.FC<ContinuationControlPanelProps> = ({
  chapterNumber,
  onGenerate,
  generating
}) => {
  const [mode, setMode] = useState<'simple' | 'standard' | 'advanced'>('standard')
  const [wordCount, setWordCount] = useState(2000)
  const [versionCount, setVersionCount] = useState(3)
  const [firstChapterMode, setFirstChapterMode] = useState('opening_scene')
  const [continueMode, setContinueMode] = useState('plot_direction')
  const [formData, setFormData] = useState({
    opening_scene: '',
    key_elements: '',
    tone: '',
    plot_direction: '',
    conflict_point: ''
  })

  // Handle form field changes
  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  // Validate form before generating
  const validateForm = (): boolean => {
    // Simple mode doesn't require specific inputs
    if (mode === 'simple') {
      return true
    }

    // For first chapters
    if (chapterNumber === 1) {
      const selectedMode = firstChapterMode
      if (!formData[selectedMode as keyof typeof formData]?.trim()) {
        return false
      }
    }

    // For continuing chapters
    if (chapterNumber > 1) {
      const selectedMode = continueMode
      if (!formData[selectedMode as keyof typeof formData]?.trim()) {
        return false
      }
    }

    return true
  }

  // Handle generate button click
  const handleGenerate = async () => {
    if (!validateForm()) {
      // Show validation error in a user-friendly way
      if (mode === 'simple') {
        await onGenerate({
          chapterNumber,
          mode,
          wordCount,
          versionCount
        })
      } else {
        const params: any = {
          chapterNumber,
          mode,
          wordCount,
          versionCount
        }

        if (chapterNumber === 1) {
          params[firstChapterMode as keyof typeof formData] = formData[firstChapterMode as keyof typeof formData]
        } else {
          params[continueMode as keyof typeof formData] = formData[continueMode as keyof typeof formData]
        }

        await onGenerate(params)
      }
    } else {
      await onGenerate({
        chapterNumber,
        mode,
        wordCount,
        versionCount
      })
    }
  }

  // Render first chapter specific inputs
  const renderFirstChapterInputs = () => {
    if (chapterNumber !== 1) return null

    return (
      <div style={{ marginTop: 16 }}>
        <Text strong style={{ marginBottom: 12, display: 'block' }}>
          请选择第一章的续写方式：
        </Text>
        <Radio.Group
          value={firstChapterMode}
          onChange={(e) => setFirstChapterMode(e.target.value)}
          disabled={generating}
        >
          <Space direction="vertical" style={{ width: '100%' }}>
            {FIRST_CHAPTER_MODES.map((option) => (
              <Radio key={option.value} value={option.value}>
                <div>
                  <Text strong>{option.label}</Text>
                  <div style={{ fontSize: '12px', color: '#8c8c8c', marginTop: 4 }}>
                    {option.value === 'opening_scene' && '描述开场场景和初始环境'}
                    {option.value === 'key_elements' && '设定故事关键要素和人物关系'}
                    {option.value === 'tone' && '确定整体基调和风格'}
                  </div>
                </div>
              </Radio>
            ))}
          </Space>
        </Radio.Group>

        <div style={{ marginTop: 16 }}>
          <Form.Item label={FIRST_CHAPTER_MODES.find(m => m.value === firstChapterMode)?.label || '内容'}>
            <TextArea
              value={formData[firstChapterMode as keyof typeof formData] || ''}
              onChange={(e) => handleInputChange(firstChapterMode, e.target.value)}
              placeholder={
                firstChapterMode === 'opening_scene' ?
                  '描述开场场景、环境氛围、人物出场等...' :
                firstChapterMode === 'key_elements' ?
                  '设定故事关键要素、重要人物关系、核心冲突等...' :
                  '确定整体基调、叙事风格、语言特点等...'
              }
              autoSize={{ minRows: 4, maxRows: 8 }}
              disabled={generating}
            />
          </Form.Item>
        </div>
      </div>
    )
  }

  // Render continuation specific inputs
  const renderContinuationInputs = () => {
    if (chapterNumber === 1) return null

    return (
      <div style={{ marginTop: 16 }}>
        <Text strong style={{ marginBottom: 12, display: 'block' }}>
          请选择续写方向：
        </Text>
        <Radio.Group
          value={continueMode}
          onChange={(e) => setContinueMode(e.target.value)}
          disabled={generating}
        >
          <Space direction="vertical" style={{ width: '100%' }}>
            {CONTINUE_MODES.map((option) => (
              <Radio key={option.value} value={option.value}>
                <div>
                  <Text strong>{option.label}</Text>
                  <div style={{ fontSize: '12px', color: '#8c8c8c', marginTop: 4 }}>
                    {option.value === 'plot_direction' && '描述接下来要发展的情节方向'}
                    {option.value === 'conflict_point' && '设定具体的冲突点和矛盾'}
                  </div>
                </div>
              </Radio>
            ))}
          </Space>
        </Radio.Group>

        <div style={{ marginTop: 16 }}>
          <Form.Item label={CONTINUE_MODES.find(m => m.value === continueMode)?.label || '内容'}>
            <TextArea
              value={formData[continueMode as keyof typeof formData] || ''}
              onChange={(e) => handleInputChange(continueMode, e.target.value)}
              placeholder={
                continueMode === 'plot_direction' ?
                  '描述接下来要发展的情节方向，包含主要事件和转折点...' :
                  '设定具体的冲突点和矛盾，描述角色间的关系变化...'
              }
              autoSize={{ minRows: 4, maxRows: 8 }}
              disabled={generating}
            />
          </Form.Item>
        </div>
      </div>
    )
  }

  return (
    <Card
      bordered={false}
      style={{
        borderRadius: 8,
        backgroundColor: '#f8f9fa',
        border: '1px solid #e9ecef',
      }}
      bodyStyle={{ padding: '24px' }}
    >
      <div style={{ marginBottom: 20 }}>
        <Space>
          <RobotOutlined style={{ fontSize: 24, color: '#1890ff' }} />
          <Text strong style={{ fontSize: 18, color: '#262626' }}>
            AI 续写控制面板
          </Text>
        </Space>
        <Text type="secondary" style={{ display: 'block', marginTop: 8 }}>
          第 {chapterNumber} 章 - 设置续写参数
        </Text>
      </div>

      {/* Mode Selection */}
      <div style={{ marginBottom: 24 }}>
        <Text strong style={{ marginBottom: 12, display: 'block' }}>
          选择模式：
        </Text>
        <Radio.Group
          value={mode}
          onChange={(e) => setMode(e.target.value as any)}
          disabled={generating}
        >
          <Space direction="vertical" style={{ width: '100%' }}>
            {(['simple', 'standard', 'advanced'] as const).map((m) => (
              <Radio key={m} value={m}>
                <div>
                  <Text strong>
                    {m === 'simple' && '简单模式'}
                    {m === 'standard' && '标准模式'}
                    {m === 'advanced' && '高级模式'}
                  </Text>
                  <div style={{ fontSize: '12px', color: '#8c8c8c', marginTop: 4 }}>
                    {MODE_DESCRIPTIONS[m]}
                  </div>
                </div>
              </Radio>
            ))}
          </Space>
        </Radio.Group>
      </div>

      <Divider />

      {/* Chapter Specific Inputs */}
      {chapterNumber === 1 ? renderFirstChapterInputs() : renderContinuationInputs()}

      <Divider />

      {/* Word Count Slider */}
      <div style={{ marginBottom: 24 }}>
        <Text strong style={{ marginBottom: 8, display: 'block' }}>
          字数要求：{wordCount} 字
        </Text>
        <Slider
          min={500}
          max={10000}
          step={100}
          value={wordCount}
          onChange={setWordCount}
          disabled={generating}
          marks={{
            500: '500',
            2000: '2000',
            5000: '5000',
            10000: '10000'
          }}
          tooltip={{ formatter: (value) => `${value}字` }}
        />
        <div style={{ display: 'flex', alignItems: 'center', marginTop: 8 }}>
          <Text type="secondary" style={{ fontSize: 12, marginRight: 8 }}>
            建议：
          </Text>
          <Text type="secondary" style={{ fontSize: 12 }}>
            {chapterNumber === 1 ? '第一章建议设置在1000-3000字之间' : '续写章节建议设置在2000-5000字之间'}
          </Text>
        </div>
      </div>

      {/* Version Count */}
      <div style={{ marginBottom: 24 }}>
        <Text strong style={{ marginBottom: 8, display: 'block' }}>
          生成版本数：
        </Text>
        <Space>
          <InputNumber
            min={1}
            max={5}
            value={versionCount}
            onChange={(value) => setVersionCount(value || 1)}
            disabled={generating}
            style={{ width: 80 }}
          />
          <Text type="secondary">个版本（AI将生成多个不同风格的续写供选择）</Text>
        </Space>
      </div>

      {/* Advanced Mode Additional Controls */}
      {mode === 'advanced' && (
        <div style={{ marginBottom: 24, padding: '16px', backgroundColor: '#fff3cd', borderRadius: 8 }}>
          <Text strong style={{ marginBottom: 8, color: '#856404' }}>
            高级模式设置
          </Text>
          <Text type="secondary" style={{ fontSize: 12 }}>
            高级模式下，您可以更精确地控制续写细节，包括角色对话、场景描写节奏等
          </Text>
        </div>
      )}

      {/* Generate Button */}
      <Button
        type="primary"
        size="large"
        block
        icon={<RobotOutlined />}
        onClick={handleGenerate}
        loading={generating}
        disabled={generating}
        style={{
          height: 48,
          fontSize: 16,
          fontWeight: 500,
          borderRadius: 8
        }}
      >
        {generating ? 'AI 正在生成中...' : '开始 AI 续写'}
      </Button>

      {/* Tips */}
      <div style={{ marginTop: 16, padding: '12px', backgroundColor: '#e6f7ff', borderRadius: 8 }}>
        <Text style={{ fontSize: 12, color: '#1890ff' }}>
          <BulbOutlined style={{ marginRight: 4 }} />
          提示：生成的内容会自动融合当前项目的人物设定和世界观背景，确保故事连贯性。
        </Text>
      </div>
    </Card>
  )
}

export default ContinuationControlPanel