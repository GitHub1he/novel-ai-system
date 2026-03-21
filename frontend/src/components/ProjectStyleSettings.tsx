import { useState, useEffect } from 'react'
import { Modal, Form, Select, Input, Slider, Space, Button, message } from 'antd'

interface ProjectStyleSettingsProps {
  visible: boolean
  onClose: () => void
  project: any
  onSave: (data: any) => Promise<void>
}

const PRESET_STYLES = [
  { label: '冷峻', value: 'cold', description: '冷静客观，少用修饰，叙事简洁' },
  { label: '诗意', value: 'poetic', description: '语言优美，善用比喻，意境深远' },
  { label: '幽默', value: 'humorous', description: '轻松风趣，善于调侃，富有张力' },
  { label: '通俗', value: 'colloquial', description: '平实朴素，贴近生活，易于理解' },
  { label: '华丽', value: 'flowery', description: '辞藻丰富，色彩浓郁，富有文采' },
  { label: '简洁', value: 'concise', description: '言简意赅，不拖泥带水，节奏明快' },
]

const LANGUAGE_STYLES = [
  { label: '简洁', value: 'concise' },
  { label: '华丽', value: 'flowery' },
  { label: '口语化', value: 'colloquial' },
  { label: '书面语', value: 'formal' },
]

const SENSORY_FOCUS = [
  { label: '视觉', value: 'visual' },
  { label: '听觉', value: 'auditory' },
  { label: '嗅觉', value: 'olfactory' },
  { label: '触觉', value: 'tactile' },
  { label: '味觉', value: 'gustatory' },
  { label: '心理', value: 'psychological' },
]

const ProjectStyleSettings: React.FC<ProjectStyleSettingsProps> = ({
  visible,
  onClose,
  project,
  onSave,
}) => {
  const [form] = Form.useForm()
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (visible && project) {
      form.setFieldsValue({
        preset_style: project.style || '',
        custom_keywords: project.style_keywords || '',
        language_style: project.language_style || 'concise',
        sensory_focus: project.sensory_focus || ['visual', 'psychological'],
        style_intensity: project.style_intensity || 70,
      })
    }
  }, [visible, project, form])

  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      setSaving(true)

      await onSave({
        style: values.preset_style,
        style_keywords: values.custom_keywords,
        language_style: values.language_style,
        sensory_focus: values.sensory_focus,
        style_intensity: values.style_intensity,
      })

      message.success('文风设置已保存')
      onClose()
    } catch (error) {
      console.error('保存失败', error)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal
      title={<span style={{ fontSize: '18px', fontWeight: 600 }}>🎨 文风设置</span>}
      open={visible}
      onCancel={onClose}
      onOk={handleSave}
      confirmLoading={saving}
      okText="保存设置"
      cancelText="取消"
      width={700}
      okButtonProps={{ style: { borderRadius: 6 } }}
      cancelButtonProps={{ style: { borderRadius: 6 } }}
    >
      <Form
        form={form}
        layout="vertical"
        style={{ marginTop: '24px' }}
      >
        <Form.Item
          label="预设文风"
          name="preset_style"
          tooltip="选择主要文风倾向，AI生成时会参考此风格"
        >
          <Select
            placeholder="选择预设文风"
            options={PRESET_STYLES.map(style => ({
              label: (
                <div>
                  <div style={{ fontWeight: 500 }}>{style.label}</div>
                  <div style={{ fontSize: '12px', color: '#8c8c8c' }}>{style.description}</div>
                </div>
              ),
              value: style.value,
            }))}
            showSearch
          />
        </Form.Item>

        <Form.Item
          label="自定义关键词"
          name="custom_keywords"
          tooltip="输入文风相关的关键词，如：克制、隐忍、压抑、奔放等，用逗号分隔"
        >
          <Input.TextArea
            placeholder="例如：克制、隐忍、细腻、含蓄、留白..."
            autoSize={{ minRows: 2, maxRows: 4 }}
            style={{ fontSize: '14px' }}
          />
        </Form.Item>

        <Form.Item
          label="语言风格"
          name="language_style"
          tooltip="选择整体语言表达风格"
        >
          <Select placeholder="选择语言风格" options={LANGUAGE_STYLES} />
        </Form.Item>

        <Form.Item
          label="感官细节重点"
          name="sensory_focus"
          tooltip="选择描写的侧重点，可多选"
        >
          <Select
            mode="multiple"
            placeholder="选择感官重点"
            options={SENSORY_FOCUS}
            maxTagCount={3}
          />
        </Form.Item>

        <Form.Item
          label="风格匹配度"
          name="style_intensity"
          tooltip="AI生成时对文风设置的遵循程度（0%为完全不遵循，100%为严格遵循）"
        >
          <Slider
            min={0}
            max={100}
            marks={{
              0: '宽松',
              50: '适中',
              100: '严格'
            }}
          />
        </Form.Item>

        <div style={{
          padding: '12px',
          background: '#f0f5ff',
          borderRadius: '6px',
          fontSize: '13px',
          color: '#595959',
          lineHeight: '1.6'
        }}>
          💡 <strong>提示：</strong>
          <ul style={{ margin: '8px 0 0 0', paddingLeft: '20px' }}>
            <li>文风设置会应用到AI生成的内容中</li>
            <li>可随时调整文风设置，无需重新创作</li>
            <li>建议先写一段示例文本，测试文风效果</li>
          </ul>
        </div>
      </Form>
    </Modal>
  )
}

export default ProjectStyleSettings
