import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Layout, List, Button, Input, Card, Empty, Spin } from 'antd'
import { BulbOutlined, RobotOutlined } from '@ant-design/icons'
import { projectApi, chapterApi } from '../services/api'
import type { Project, Chapter } from '../types'

const { Sider, Content } = Layout

const ProjectDetail = () => {
  const { id } = useParams<{ id: string }>()
  const [project, setProject] = useState<Project | null>(null)
  const [chapters, setChapters] = useState<Chapter[]>([])
  const [currentChapter, setCurrentChapter] = useState<Chapter | null>(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [prompt, setPrompt] = useState('')

  useEffect(() => {
    fetchProject()
    fetchChapters()
  }, [id])

  const fetchProject = async () => {
    try {
      const response = await projectApi.get(Number(id))
      setProject(response.data)
    } catch (error) {
      console.error('加载项目失败', error)
    }
  }

  const fetchChapters = async () => {
    setLoading(true)
    try {
      // TODO: 实现章节列表API
      setLoading(false)
    } catch (error) {
      setLoading(false)
      console.error('加载章节失败', error)
    }
  }

  const handleGenerate = async () => {
    if (!currentChapter || !prompt) return

    setGenerating(true)
    try {
      const response = await chapterApi.generate(currentChapter.id, prompt)
      setCurrentChapter({
        ...currentChapter,
        content: response.data.content,
        word_count: response.data.word_count,
      })
      setPrompt('')
    } catch (error) {
      console.error('生成失败', error)
    } finally {
      setGenerating(false)
    }
  }

  if (!project) {
    return (
      <div style={{ textAlign: 'center', padding: '100px' }}>
        <Spin size="large" />
      </div>
    )
  }

  return (
    <Layout style={{ height: 'calc(100vh - 112px)' }}>
      {/* 左侧：章节列表 */}
      <Sider width={240} theme="light" style={{ borderRight: '1px solid #f0f0f0' }}>
        <div style={{ padding: '16px' }}>
          <h3>章节目录</h3>
          <Button type="primary" size="small" block style={{ marginBottom: 16 }}>
            新建章节
          </Button>
          {chapters.length === 0 ? (
            <Empty description="暂无章节" image={Empty.PRESENTED_IMAGE_SIMPLE} />
          ) : (
            <List
              size="small"
              dataSource={chapters}
              renderItem={(chapter) => (
                <List.Item
                  style={{ cursor: 'pointer', padding: '8px' }}
                  onClick={() => setCurrentChapter(chapter)}
                >
                  <div>
                    <div>第{chapter.chapter_number}章</div>
                    <div style={{ fontSize: '12px', color: '#999' }}>{chapter.title}</div>
                  </div>
                </List.Item>
              )}
            />
          )}
        </div>
      </Sider>

      {/* 中间：编辑器 */}
      <Content style={{ padding: '0 24px', overflowY: 'auto' }}>
        {currentChapter ? (
          <div>
            <div style={{ padding: '16px 0', borderBottom: '1px solid #f0f0f0' }}>
              <h2>第{currentChapter.chapter_number}章 {currentChapter.title}</h2>
              <span style={{ color: '#999' }}>
                {currentChapter.word_count}字
              </span>
            </div>
            <div
              style={{
                padding: '24px 0',
                minHeight: '500px',
                lineHeight: '1.8',
                fontSize: '16px',
              }}
              contentEditable
              suppressContentEditableWarning
            >
              {currentChapter.content || '在此处开始创作...'}
            </div>
          </div>
        ) : (
          <div
            style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              height: '100%',
            }}
          >
            <Empty description="请选择或创建章节" />
          </div>
        )}

        {/* AI指令输入 */}
        {currentChapter && (
          <Card
            style={{ position: 'fixed', bottom: 16, left: 264, right: 264, zIndex: 100 }}
            size="small"
          >
            <Input
              placeholder="输入创作指令，例如：写一段主角与反派的对话..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onPressEnter={handleGenerate}
              disabled={generating}
              suffix={
                <Button
                  type="primary"
                  icon={<RobotOutlined />}
                  size="small"
                  onClick={handleGenerate}
                  loading={generating}
                >
                  AI生成
                </Button>
              }
            />
          </Card>
        )}
      </Content>

      {/* 右侧：上下文面板 */}
      <Sider width={280} theme="light" style={{ borderLeft: '1px solid #f0f0f0' }}>
        <div style={{ padding: '16px' }}>
          <h3><BulbOutlined /> 上下文</h3>
          <Card size="small" title="项目信息" style={{ marginBottom: 16 }}>
            <p><strong>书名：</strong>{project.title}</p>
            <p><strong>类型：</strong>{project.genre}</p>
            <p><strong>文风：</strong>{project.style || '未设置'}</p>
          </Card>
          <Card size="small" title="快捷指令">
            <Button size="small" block style={{ marginBottom: 8 }}>插入场景描写</Button>
            <Button size="small" block style={{ marginBottom: 8 }}>插入对话</Button>
            <Button size="small" block>插入心理活动</Button>
          </Card>
        </div>
      </Sider>
    </Layout>
  )
}

export default ProjectDetail
