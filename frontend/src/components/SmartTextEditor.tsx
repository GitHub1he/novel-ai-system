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
  }

  // 快捷指令
  const quickCommands = [
    {
      name: '续写一段',
      icon: <EditOutlined />,
      prompt: '请根据当前内容续写一段，保持文风和人物性格一致',
      action: () => {
        if (!onAIGenerate) return
        const textarea = textAreaRef.current?.resizableTextArea?.textArea
        // 如果有选中文本，从选中文本的末尾位置续写；否则从光标位置续写
        const position = selection ? selection.end : (textarea?.selectionEnd || value.length)
        // 传递选中的文本（如果有），否则传递空字符串
        const selectedTextContent = selection ? selection.text : ''
        onAIGenerate(selectedTextContent, 'insert_before', position)
      }
    },
    {
      name: '扩展描写',
      icon: <PlusCircleOutlined />,
      prompt: '请扩展选中的内容，增加更多细节和描写',
      action: () => {
        if (!selection) {
          message.warning('请先选择要扩展的文本')
          return
        }
        if (!onAIGenerate) return
        onAIGenerate(selection.text, 'replace', selection.start)
      }
    },
    {
      name: '精简内容',
      icon: <SwapOutlined />,
      prompt: '请精简选中的内容，保留核心信息',
      action: () => {
        if (!selection) {
          message.warning('请先选择要精简的文本')
          return
        }
        if (!onAIGenerate) return
        onAIGenerate(selection.text, 'replace', selection.start)
      }
    },
    {
      name: '改写润色',
      icon: <HighlightOutlined />,
      prompt: '请改写选中的内容，使其更加生动流畅',
      action: () => {
        if (!selection) {
          message.warning('请先选择要改写的文本')
          return
        }
        if (!onAIGenerate) return
        onAIGenerate(selection.text, 'replace', selection.start)
      }
    }
  ]

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

        {/* 快捷指令 */}
        <Space size="small" wrap>
          {quickCommands.map((cmd, index) => (
            <Tooltip key={index} title={cmd.prompt}>
              <Button
                size="small"
                icon={cmd.icon}
                onClick={cmd.action}
                disabled={selection === null && cmd.name !== '续写一段'}
              >
                {cmd.name}
              </Button>
            </Tooltip>
          ))}
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
        width={500}
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
