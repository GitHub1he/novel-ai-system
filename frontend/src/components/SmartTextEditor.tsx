import { useState, useRef, useEffect } from 'react'
import { Input, Button, Space, Modal, Radio, message, Popover, Tooltip } from 'antd'
import {
  BulbOutlined,
  HighlightOutlined,
  SwapOutlined,
  PlusCircleOutlined,
  EditOutlined
} from '@ant-design/icons'

const { TextArea } = Input

interface SmartTextEditorProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  autoSize?: { minRows?: number; maxRows?: number }
  style?: React.CSSProperties
  onAIGenerate?: (selectedText: string, mode: 'replace' | 'insert_before' | 'insert_after', position?: number, prompt?: string) => void
  projectId?: number
  chapterId?: number
}

const SmartTextEditor: React.FC<SmartTextEditorProps> = ({
  value,
  onChange,
  placeholder,
  autoSize,
  style,
  onAIGenerate,
  projectId,
  chapterId
}) => {
  const textAreaRef = useRef<any>(null)
  const [selection, setSelection] = useState<{ start: number; end: number; text: string } | null>(null)
  const [aiModalVisible, setAiModalVisible] = useState(false)
  const [insertMode, setInsertMode] = useState<'cursor' | 'start' | 'end'>('cursor')
  const [customPrompt, setCustomPrompt] = useState('') // 自定义生成要求
  const [selectedQuickMode, setSelectedQuickMode] = useState<string | null>(null) // 选中的快捷模式

  // 监听文本选择
  const handleMouseUp = () => {
    const textarea = textAreaRef.current?.resizableTextArea?.textArea
    if (!textarea) return

    const start = textarea.selectionStart
    const end = textarea.selectionEnd

    if (start !== end) {
      const selectedText = value.substring(start, end)
      setSelection({ start, end, text: selectedText })
    } else {
      setSelection(null)
    }
  }

  // 打开AI修改弹窗
  const handleOpenAIModal = () => {
    if (selection) {
      // 有选中文本，直接进入修改模式
      setAiModalVisible(true)
    } else {
      // 没有选中文本，让用户选择插入方式
      Modal.confirm({
        title: '🤖 AI 智能生成',
        content: (
          <div>
            <p>请选择AI生成内容的插入方式：</p>
            <Radio.Group
              onChange={(e) => setInsertMode(e.target.value)}
              defaultValue="cursor"
              style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '8px' }}
            >
              <Radio value="cursor">
                <strong>插入到光标位置</strong><br />
                <span style={{ fontSize: '12px', color: '#666' }}>
                  在当前光标位置插入生成的内容
                </span>
              </Radio>
              <Radio value="start">
                <strong>插入到开头</strong><br />
                <span style={{ fontSize: '12px', color: '#666' }}>
                  在文本开头插入生成的内容
                </span>
              </Radio>
              <Radio value="end">
                <strong>插入到结尾</strong><br />
                <span style={{ fontSize: '12px', color: '#666' }}>
                  在文本结尾追加生成的内容
                </span>
              </Radio>
            </Radio.Group>
          </div>
        ),
        onOk: () => {
          setAiModalVisible(true)
        }
      })
    }
  }

  // 执行AI生成
  const handleAIGenerate = (mode: 'replace' | 'insert') => {
    if (!onAIGenerate) {
      message.warning('AI生成功能未配置')
      return
    }

    if (selection && mode === 'replace') {
      // 替换选中的文本
      onAIGenerate(selection.text, 'replace', selection.start, customPrompt)
    } else if (mode === 'insert') {
      // 插入到指定位置
      let position = 0
      const textarea = textAreaRef.current?.resizableTextArea?.textArea
      if (textarea) {
        position = textarea.selectionStart
      }

      if (insertMode === 'start') {
        position = 0
      } else if (insertMode === 'end') {
        position = value.length
      } else {
        // cursor mode，使用当前光标位置
        position = textarea?.selectionStart || 0
      }

      // 如果有选中文本，从选中文本的末尾位置插入；否则从指定位置插入
      const insertPosition = selection ? selection.end : position
      const selectedTextContent = selection ? selection.text : ''
      onAIGenerate(selectedTextContent, 'insert_before', insertPosition, customPrompt)
    }

    setAiModalVisible(false)
    setSelection(null)
    setCustomPrompt('') // 清空输入框
    setSelectedQuickMode(null) // 清空快捷模式选择
  }

  // 快捷模式定义
  const quickModes = [
    {
      key: 'continue_writing',
      name: '续写一段',
      icon: <EditOutlined />,
      prompt: '请根据当前内容续写一段，保持文风和人物性格一致，确保情节自然连贯。',
      description: '在现有内容基础上续写'
    },
    {
      key: 'expand_description',
      name: '扩展描写',
      icon: <PlusCircleOutlined />,
      prompt: '请扩展内容，增加更多细节描写、环境渲染、人物心理活动等，使内容更加丰富生动。',
      description: '增加细节和描写'
    },
    {
      key: 'simplify_content',
      name: '精简内容',
      icon: <SwapOutlined />,
      prompt: '请精简内容，保留核心情节和关键信息，去除冗余描述，使表达更加简洁明了。',
      description: '保留核心，去除冗余'
    },
    {
      key: 'polish_rewrite',
      name: '改写润色',
      icon: <HighlightOutlined />,
      prompt: '请改写润色内容，优化语言表达，增强文字感染力，使行文更加流畅生动。',
      description: '优化文字表达'
    }
  ]

  // 处理快捷模式选择
  const handleQuickModeSelect = (modeKey: string) => {
    const mode = quickModes.find(m => m.key === modeKey)
    if (mode) {
      // 如果再次点击已选中的模式，则取消选择
      if (selectedQuickMode === modeKey) {
        setSelectedQuickMode(null)
        setCustomPrompt('')
      } else {
        setSelectedQuickMode(modeKey)
        setCustomPrompt(mode.prompt)
      }
    }
  }

  // 当弹窗关闭时，重置快捷模式选择
  useEffect(() => {
    if (!aiModalVisible) {
      setSelectedQuickMode(null)
      setCustomPrompt('')
    }
  }, [aiModalVisible])

  return (
    <div>
      {/* 工具栏 */}
      <div style={{
        marginBottom: '8px',
        padding: '8px 12px',
        background: '#fafafa',
        borderRadius: '6px',
        border: '1px solid #f0f0f0',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <Space size="small">
          <Tooltip title="AI智能生成">
            <Button
              type="primary"
              size="small"
              icon={<BulbOutlined />}
              onClick={handleOpenAIModal}
            >
              {selection ? `修改选中文字 (${selection.text.length}字)` : 'AI生成'}
            </Button>
          </Tooltip>

          {selection && (
            <Tooltip title="取消选择">
              <Button
                size="small"
                onClick={() => {
                  setSelection(null)
                  const textarea = textAreaRef.current?.resizableTextArea?.textArea
                  if (textarea) {
                    textarea.focus()
                    textarea.setSelectionRange(0, 0)
                  }
                }}
              >
                取消选择
              </Button>
            </Tooltip>
          )}
        </Space>
      </div>

      {/* 文本编辑器 */}
      <TextArea
        ref={textAreaRef}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onMouseUp={handleMouseUp}
        onKeyUp={handleMouseUp}
        placeholder={placeholder}
        autoSize={autoSize}
        style={style}
      />

      {/* AI修改确认弹窗 */}
      <Modal
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <BulbOutlined style={{ color: '#1890ff' }} />
            <span>AI 智能修改</span>
          </div>
        }
        open={aiModalVisible}
        onCancel={() => setAiModalVisible(false)}
        footer={null}
        width={600}
      >
        {selection ? (
          // 有选中文本：显示替换选项
          <div>
            <div style={{ marginBottom: '16px', padding: '12px', background: '#f0f5ff', borderRadius: '6px' }}>
              <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>选中的文本：</div>
              <div style={{
                padding: '8px',
                background: 'white',
                borderRadius: '4px',
                maxHeight: '100px',
                overflow: 'auto',
                fontSize: '14px',
                whiteSpace: 'pre-wrap'
              }}>
                {selection.text}
              </div>
              <div style={{ fontSize: '12px', color: '#999', marginTop: '4px' }}>
                字数：{selection.text.length}
              </div>
            </div>

            {/* 快捷模式选择 */}
            <div style={{ marginBottom: '16px' }}>
              <div style={{ fontSize: '13px', color: '#666', marginBottom: '8px' }}>
                快捷模式（可选）
              </div>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(2, 1fr)',
                gap: '10px'
              }}>
                {quickModes.map(mode => {
                  const isSelected = selectedQuickMode === mode.key
                  return (
                    <div
                      key={mode.key}
                      onClick={() => handleQuickModeSelect(mode.key)}
                      style={{
                        padding: '10px 12px',
                        border: `2px solid ${isSelected ? '#1890ff' : '#d9d9d9'}`,
                        borderRadius: '6px',
                        cursor: 'pointer',
                        background: isSelected ? '#e6f7ff' : '#fff',
                        transition: 'all 0.3s',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px'
                      }}
                      onMouseEnter={(e) => {
                        if (!isSelected) {
                          e.currentTarget.style.borderColor = '#1890ff'
                          e.currentTarget.style.boxShadow = '0 2px 6px rgba(24, 144, 255, 0.2)'
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (!isSelected) {
                          e.currentTarget.style.borderColor = '#d9d9d9'
                          e.currentTarget.style.boxShadow = 'none'
                        }
                      }}
                    >
                      <div style={{
                        fontSize: '18px',
                        color: isSelected ? '#1890ff' : '#8c8c8c'
                      }}>
                        {mode.icon}
                      </div>
                      <div style={{ flex: 1 }}>
                        <div style={{
                          fontWeight: isSelected ? '600' : '400',
                          color: isSelected ? '#1890ff' : '#262626',
                          marginBottom: '2px',
                          fontSize: '13px'
                        }}>
                          {mode.name}
                        </div>
                        <div style={{
                          fontSize: '11px',
                          color: '#8c8c8c'
                        }}>
                          {mode.description}
                        </div>
                      </div>
                      {isSelected && (
                        <div style={{
                          color: '#1890ff',
                          fontSize: '14px',
                          fontWeight: 'bold'
                        }}>
                          ✓
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
              {selectedQuickMode && (
                <div style={{
                  marginTop: '8px',
                  padding: '6px 10px',
                  background: '#fff7e6',
                  border: '1px solid #ffd591',
                  borderRadius: '4px',
                  fontSize: '12px',
                  color: '#d46b08',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}>
                  <span style={{ fontSize: '14px' }}>💡</span>
                  <span>
                    已选择 <strong>{quickModes.find(m => m.key === selectedQuickMode)?.name}</strong> 模式，
                    点击卡片可取消选择
                  </span>
                </div>
              )}
            </div>

            <div style={{ fontSize: '14px', marginBottom: '12px' }}>
              生成要求
              <span style={{ fontSize: '12px', color: '#999', fontWeight: 'normal', marginLeft: '8px' }}>
                （可选，不填则使用默认指令）
              </span>
            </div>
            <Input.TextArea
              placeholder="例如：让对话更加紧张激烈&#10;例如：增加环境描写，营造恐怖氛围"
              value={customPrompt}
              onChange={(e) => setCustomPrompt(e.target.value)}
              autoSize={{ minRows: 2, maxRows: 4 }}
              style={{ marginBottom: '16px' }}
            />

            <div style={{ fontSize: '14px', marginBottom: '16px' }}>请选择操作：</div>

            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              <Button
                type="primary"
                size="large"
                block
                icon={<SwapOutlined />}
                onClick={() => handleAIGenerate('replace')}
              >
                替换选中文本
              </Button>

              <Button
                size="large"
                block
                icon={<PlusCircleOutlined />}
                onClick={() => {
                  if (!onAIGenerate) return
                  onAIGenerate(selection.text, 'insert_before', selection.end, customPrompt)
                  setAiModalVisible(false)
                  setCustomPrompt('')
                  setSelectedQuickMode(null)
                }}
              >
                在选中内容后插入
              </Button>

              <Button
                size="large"
                block
                icon={<EditOutlined />}
                onClick={() => {
                  if (!onAIGenerate) return
                  onAIGenerate(selection.text, 'insert_before', selection.start, customPrompt)
                  setAiModalVisible(false)
                  setCustomPrompt('')
                  setSelectedQuickMode(null)
                }}
              >
                在选中内容前插入
              </Button>
            </Space>
          </div>
        ) : (
          // 没有选中文本：提示用户选择文本或选择插入位置
          <div>
            <p style={{ marginBottom: '16px', color: '#666' }}>
              💡 <strong>提示：</strong>请先在文本框中选择要修改的内容，或者直接输入生成要求
            </p>

            {/* 快捷模式选择 */}
            <div style={{ marginBottom: '16px' }}>
              <div style={{ fontSize: '13px', color: '#666', marginBottom: '8px' }}>
                快捷模式（可选）
              </div>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(2, 1fr)',
                gap: '10px'
              }}>
                {quickModes.map(mode => {
                  const isSelected = selectedQuickMode === mode.key
                  return (
                    <div
                      key={mode.key}
                      onClick={() => handleQuickModeSelect(mode.key)}
                      style={{
                        padding: '10px 12px',
                        border: `2px solid ${isSelected ? '#1890ff' : '#d9d9d9'}`,
                        borderRadius: '6px',
                        cursor: 'pointer',
                        background: isSelected ? '#e6f7ff' : '#fff',
                        transition: 'all 0.3s',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px'
                      }}
                      onMouseEnter={(e) => {
                        if (!isSelected) {
                          e.currentTarget.style.borderColor = '#1890ff'
                          e.currentTarget.style.boxShadow = '0 2px 6px rgba(24, 144, 255, 0.2)'
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (!isSelected) {
                          e.currentTarget.style.borderColor = '#d9d9d9'
                          e.currentTarget.style.boxShadow = 'none'
                        }
                      }}
                    >
                      <div style={{
                        fontSize: '18px',
                        color: isSelected ? '#1890ff' : '#8c8c8c'
                      }}>
                        {mode.icon}
                      </div>
                      <div style={{ flex: 1 }}>
                        <div style={{
                          fontWeight: isSelected ? '600' : '400',
                          color: isSelected ? '#1890ff' : '#262626',
                          marginBottom: '2px',
                          fontSize: '13px'
                        }}>
                          {mode.name}
                        </div>
                        <div style={{
                          fontSize: '11px',
                          color: '#8c8c8c'
                        }}>
                          {mode.description}
                        </div>
                      </div>
                      {isSelected && (
                        <div style={{
                          color: '#1890ff',
                          fontSize: '14px',
                          fontWeight: 'bold'
                        }}>
                          ✓
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
              {selectedQuickMode && (
                <div style={{
                  marginTop: '8px',
                  padding: '6px 10px',
                  background: '#fff7e6',
                  border: '1px solid #ffd591',
                  borderRadius: '4px',
                  fontSize: '12px',
                  color: '#d46b08',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}>
                  <span style={{ fontSize: '14px' }}>💡</span>
                  <span>
                    已选择 <strong>{quickModes.find(m => m.key === selectedQuickMode)?.name}</strong> 模式，
                    点击卡片可取消选择
                  </span>
                </div>
              )}
            </div>

            <div style={{ fontSize: '14px', marginBottom: '12px' }}>
              生成要求
              <span style={{ fontSize: '12px', color: '#999', fontWeight: 'normal', marginLeft: '8px' }}>
                （可选）
              </span>
            </div>
            <Input.TextArea
              placeholder="例如：写一段主角内心的独白，表达他的纠结&#10;例如：添加一段紧张的追逐戏描写"
              value={customPrompt}
              onChange={(e) => setCustomPrompt(e.target.value)}
              autoSize={{ minRows: 3, maxRows: 5 }}
              style={{ marginBottom: '16px' }}
            />

            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              <Button
                type="primary"
                size="large"
                block
                onClick={() => {
                  if (!onAIGenerate) return
                  const textarea = textAreaRef.current?.resizableTextArea?.textArea
                  const position = textarea?.selectionStart || value.length
                  onAIGenerate('', 'insert_before', position, customPrompt)
                  setAiModalVisible(false)
                  setCustomPrompt('')
                  setSelectedQuickMode(null)
                }}
              >
                在光标位置生成
              </Button>
              <Button
                size="large"
                block
                onClick={() => {
                  if (!onAIGenerate) return
                  onAIGenerate('', 'insert_before', value.length, customPrompt)
                  setAiModalVisible(false)
                  setCustomPrompt('')
                  setSelectedQuickMode(null)
                }}
              >
                追加到末尾
              </Button>
            </Space>
          </div>
        )}
      </Modal>
    </div>
  )
}

export default SmartTextEditor
