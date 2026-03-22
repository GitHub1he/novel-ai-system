import { useState } from 'react'
import { Modal, Row, Col, Card, Button, Space, Typography, Tag, Statistic, Radio, Divider, message } from 'antd'
import { CheckCircleOutlined, EyeOutlined, CopyOutlined } from '@ant-design/icons'
import ReactMarkdown from 'react-markdown'

const { Text, Title, Paragraph } = Typography

interface GeneratedVersion {
  version_id: string
  content: string
  word_count: number
  summary: string
}

interface ContextUsed {
  previous_chapter?: any
  characters: string[]
  world_settings: string[]
  plot_nodes: string[]
}

interface VersionPreviewProps {
  visible: boolean
  versions: GeneratedVersion[]
  context?: ContextUsed
  onSelect: (versionId: string) => void
  onClose: () => void
  loading?: boolean
}

const VersionPreview: React.FC<VersionPreviewProps> = ({
  visible,
  versions,
  context,
  onSelect,
  onClose,
  loading = false
}) => {
  const [selectedVersion, setSelectedVersion] = useState<string>(versions[0]?.version_id || '')
  const [compareMode, setCompareMode] = useState(false)

  const currentVersion = versions.find(v => v.version_id === selectedVersion)

  const handleSelect = () => {
    if (!selectedVersion) {
      message.warning('请先选择一个版本')
      return
    }
    onSelect(selectedVersion)
  }

  const copyContent = (content: string) => {
    navigator.clipboard.writeText(content)
    message.success('已复制到剪贴板')
  }

  const renderVersionCard = (version: GeneratedVersion, index: number) => {
    const isSelected = version.version_id === selectedVersion
    const tempMap: Record<string, string> = {
      '0': '0.8 (标准)',
      '1': '0.85 (较高)',
      '2': '0.9 (高)'
    }
    const temp = tempMap[index.toString()] || '未知'

    return (
      <Card
        key={version.version_id}
        hoverable
        style={{
          height: '100%',
          border: isSelected ? '2px solid #1890ff' : '1px solid #d9d9d9',
          position: 'relative',
          overflow: 'hidden'
        }}
        onClick={() => setSelectedVersion(version.version_id)}
      >
        {isSelected && (
          <div style={{
            position: 'absolute',
            top: '12px',
            right: '12px',
            color: '#52c41a',
            fontSize: '20px'
          }}>
            <CheckCircleOutlined />
          </div>
        )}

        <Space direction="vertical" size="small" style={{ width: '100%' }}>
          <div>
            <Tag color="blue">版本 {index + 1}</Tag>
            <Tag color="purple">温度 {temp}</Tag>
          </div>

          <Statistic
            title="字数"
            value={version.word_count}
            suffix="字"
            valueStyle={{ fontSize: '16px' }}
          />

          <div>
            <Text strong>摘要：</Text>
            <Paragraph
              ellipsis={{ rows: 2, expandable: false }}
              style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}
            >
              {version.summary || <Text type="secondary">选择此版本并保存后将自动生成摘要</Text>}
            </Paragraph>
          </div>

          <Button
            type={isSelected ? 'primary' : 'default'}
            size="small"
            icon={<EyeOutlined />}
            onClick={(e) => {
              e.stopPropagation()
              setSelectedVersion(version.version_id)
            }}
            block
          >
            {isSelected ? '已选择' : '查看详情'}
          </Button>
        </Space>
      </Card>
    )
  }

  return (
    <Modal
      title={
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span>📚</span>
          <span>选择生成版本</span>
          <Tag color="blue">{versions.length} 个版本</Tag>
        </div>
      }
      open={visible}
      onCancel={onClose}
      onOk={handleSelect}
      okText="选择此版本保存"
      cancelText="取消"
      width={1200}
      okButtonProps={{ loading, icon: <CheckCircleOutlined /> }}
      styles={{
        body: { padding: '24px', height: '70vh', overflow: 'auto' }
      }}
    >
      {/* 对比模式开关 */}
      <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Space>
          <Text strong>查看模式：</Text>
          <Radio.Group value={compareMode} onChange={(e) => setCompareMode(e.target.value)}>
            <Radio.Button value={false}>单版本预览</Radio.Button>
            <Radio.Button value={true}>对比模式</Radio.Button>
          </Radio.Group>
        </Space>
        {currentVersion && (
          <Button
            size="small"
            icon={<CopyOutlined />}
            onClick={() => copyContent(currentVersion.content)}
          >
            复制内容
          </Button>
        )}
      </div>

      {/* 上下文信息 */}
      {context && (
        <>
          <Divider orientation="left">📋 使用上下文</Divider>
          <Row gutter={16} style={{ marginBottom: '16px' }}>
            {context.previous_chapter && (
              <Col span={8}>
                <Card size="small" title="上一章">
                  <Text>{context.previous_chapter.title}</Text>
                </Card>
              </Col>
            )}
            {context.characters?.length > 0 && (
              <Col span={8}>
                <Card size="small" title="登场人物">
                  <Space wrap>
                    {context.characters.map((c, i) => (
                      <Tag key={i} color="blue">{c}</Tag>
                    ))}
                  </Space>
                </Card>
              </Col>
            )}
            {context.world_settings?.length > 0 && (
              <Col span={8}>
                <Card size="small" title="世界观设定">
                  <Space wrap>
                    {context.world_settings.map((s, i) => (
                      <Tag key={i} color="green">{s}</Tag>
                    ))}
                  </Space>
                </Card>
              </Col>
            )}
          </Row>
          <Divider />
        </>
      )}

      {compareMode ? (
        /* 对比模式：左右对比 */
        <Row gutter={16}>
          {versions.map((version, index) => (
            <Col span={12} key={version.version_id}>
              <Card
                title={
                  <Space>
                    <span>版本 {index + 1}</span>
                    <Tag color="purple">温度 {['0.8', '0.85', '0.9'][index] || '未知'}</Tag>
                  </Space>
                }
                style={{ height: '50vh', overflow: 'auto' }}
                headStyle={{ position: 'sticky', top: 0, zIndex: 1, background: '#fff' }}
              >
                <div style={{ whiteSpace: 'pre-wrap', fontSize: '14px', lineHeight: '1.8' }}>
                  {version.content}
                </div>
              </Card>
            </Col>
          ))}
        </Row>
      ) : (
        /* 单版本模式：版本列表 + 详情预览 */
        <Row gutter={16}>
          <Col span={8}>
            <div style={{ height: '50vh', overflow: 'auto', paddingRight: '8px' }}>
              <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                {versions.map((version, index) => renderVersionCard(version, index))}
              </Space>
            </div>
          </Col>

          <Col span={16}>
            {currentVersion ? (
              <Card
                title={
                  <Space>
                    <span>版本预览</span>
                    <Tag color="blue">
                      {versions.findIndex(v => v.version_id === currentVersion.version_id) + 1}
                    </Tag>
                    <Tag color="purple">{currentVersion.word_count} 字</Tag>
                  </Space>
                }
                style={{ height: '50vh', overflow: 'auto' }}
                bodyStyle={{ height: 'calc(100% - 60px)', overflow: 'auto' }}
              >
                <div style={{ whiteSpace: 'pre-wrap', fontSize: '14px', lineHeight: '1.8' }}>
                  {currentVersion.content}
                </div>
              </Card>
            ) : (
              <Card style={{ height: '50vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Text type="secondary">请选择一个版本查看详情</Text>
              </Card>
            )}
          </Col>
        </Row>
      )}
    </Modal>
  )
}

export default VersionPreview
