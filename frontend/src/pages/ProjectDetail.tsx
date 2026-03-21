import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Layout, List, Button, Input, Card, Empty, Spin, Tabs, Space, Modal, message, Select } from 'antd'
const { TextArea } = Input
import {
  BulbOutlined,
  RobotOutlined,
  TeamOutlined,
  GlobalOutlined,
  BookOutlined,
  PlusOutlined,
  EditOutlined,
  ArrowLeftOutlined,
} from '@ant-design/icons'
import { projectApi, chapterApi } from '../services/api'
import CharacterManagement from '../components/CharacterManagement'
import WorldSettingManagement from '../components/WorldSettingManagement'
import ProjectStyleSettings from '../components/ProjectStyleSettings'
import ContextAnalysisView from '../components/ContextAnalysisView'
import type { Project, Chapter } from '../types'

const { Content, Sider } = Layout

const CHAPTER_STATUS_OPTIONS = [
  { label: '草稿', value: 'draft' },
  { label: '修订中', value: 'revising' },
  { label: '已完成', value: 'completed' },
]

const PROJECT_STATUS_CONFIG = {
  draft: { color: '#8c8c8c', label: '草稿' },
  revising: { color: '#1890ff', label: '修订中' },
  completed: { color: '#52c41a', label: '已完成' },
}

const ProjectDetail = () => {
  const { id } = useParams<{ id: string }>()
  const [project, setProject] = useState<Project | null>(null)
  const [chapters, setChapters] = useState<Chapter[]>([])
  const [currentChapter, setCurrentChapter] = useState<Chapter | null>(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [prompt, setPrompt] = useState('')
  const [activeTab, setActiveTab] = useState('chapters')
  const [createModalVisible, setCreateModalVisible] = useState(false)
  const [newChapterTitle, setNewChapterTitle] = useState('')
  const [newChapterNumber, setNewChapterNumber] = useState(1)
  const [creating, setCreating] = useState(false)
  const [outlineModalVisible, setOutlineModalVisible] = useState(false)
  const [outlineContent, setOutlineContent] = useState('')
  const [saving, setSaving] = useState(false)
  const [loadingChapter, setLoadingChapter] = useState(false)
  const [styleSettingsVisible, setStyleSettingsVisible] = useState(false)
  const [contextAnalysisVisible, setContextAnalysisVisible] = useState(false)
  const [plotDirection, setPlotDirection] = useState('')

  useEffect(() => {
    fetchProject()
    fetchChapters()
  }, [id])

  const fetchProject = async () => {
    try {
      const response = await projectApi.get(Number(id))
      if (response.data.code !== 200) {
        console.error('加载项目失败:', response.data.message)
        return
      }
      setProject(response.data.data)
    } catch (error) {
      console.error('加载项目失败', error)
    }
  }

  const fetchChapters = async () => {
    setLoading(true)
    try {
      const response = await chapterApi.list(Number(id))
      if (response.data.code !== 200) {
        console.error('加载章节失败:', response.data.message)
        return
      }
      setChapters(response.data.data.chapters)

      // 自动计算下一章序号
      if (response.data.data.chapters.length > 0) {
        const maxChapter = Math.max(...response.data.data.chapters.map((c: Chapter) => c.chapter_number))
        setNewChapterNumber(maxChapter + 1)
      } else {
        setNewChapterNumber(1)
      }
    } catch (error) {
      console.error('加载章节失败', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateChapter = async () => {
    if (!newChapterTitle.trim()) {
      message.error('请输入章节标题')
      return
    }

    setCreating(true)
    try {
      const response = await chapterApi.create({
        project_id: Number(id),
        title: newChapterTitle,
        chapter_number: newChapterNumber,
      })
      if (response.data.code !== 200) {
        message.error('创建章节失败: ' + response.data.message)
        return
      }
      message.success('章节创建成功')
      setCreateModalVisible(false)
      setNewChapterTitle('')
      fetchChapters()
    } catch (error) {
      message.error('创建章节失败')
      console.error('创建章节失败', error)
    } finally {
      setCreating(false)
    }
  }

  const handleEditOutline = () => {
    if (!currentChapter) return
    setOutlineContent(currentChapter.outline || '')
    setOutlineModalVisible(true)
  }

  const handleSaveOutline = async () => {
    if (!currentChapter) return

    setSaving(true)
    try {
      const response = await chapterApi.update(currentChapter.id, {
        outline: outlineContent
      })
      if (response.data.code === 200) {
        message.success('大纲保存成功')
        setCurrentChapter({
          ...currentChapter,
          outline: outlineContent
        })
        setOutlineModalVisible(false)
      } else {
        message.error('大纲保存失败: ' + response.data.message)
      }
    } catch (error) {
      message.error('大纲保存失败')
      console.error('大纲保存失败', error)
    } finally {
      setSaving(false)
    }
  }

  const handleSaveContent = async () => {
    if (!currentChapter) return

    setSaving(true)
    try {
      const response = await chapterApi.update(currentChapter.id, {
        content: currentChapter.content
      })
      if (response.data.code === 200) {
        message.success('内容保存成功')
        // 更新当前章节的word_count
        setCurrentChapter(response.data.data)
      } else {
        message.error('内容保存失败: ' + response.data.message)
      }
    } catch (error) {
      message.error('内容保存失败')
      console.error('内容保存失败', error)
    } finally {
      setSaving(false)
    }
  }

  const handleSelectChapter = async (chapter: Chapter) => {
    setLoadingChapter(true)
    try {
      const response = await chapterApi.get(chapter.id)
      if (response.data.code === 200) {
        setCurrentChapter(response.data.data)
      } else {
        message.error('加载章节失败: ' + response.data.message)
      }
    } catch (error) {
      message.error('加载章节失败')
      console.error('加载章节失败', error)
    } finally {
      setLoadingChapter(false)
    }
  }

  const handleStatusChange = async (newStatus: string) => {
    if (!currentChapter) return

    try {
      const response = await chapterApi.update(currentChapter.id, {
        status: newStatus as 'draft' | 'revising' | 'completed'
      })
      if (response.data.code === 200) {
        setCurrentChapter(response.data.data)
        message.success('状态已更新')
        // 刷新章节列表以更新状态显示
        fetchChapters()
      } else {
        message.error('状态更新失败: ' + response.data.message)
      }
    } catch (error) {
      message.error('状态更新失败')
      console.error('状态更新失败', error)
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
      message.success('生成成功')
    } catch (error) {
      message.error('生成失败')
      console.error('生成失败', error)
    } finally {
      setGenerating(false)
    }
  }

  const handleSaveStyleSettings = async (data: any) => {
    if (!project) return

    try {
      const response = await projectApi.update(Number(id), data)
      if (response.data.code === 200) {
        setProject(response.data.data)
      }
    } catch (error) {
      throw error
    }
  }

  const handleOpenContextAnalysis = () => {
    if (currentChapter) {
      setContextAnalysisVisible(true)
    } else {
      message.warning('请先选择一个章节')
    }
  }

  const handleCloseContextAnalysis = () => {
    setContextAnalysisVisible(false)
    setPlotDirection('')
  }

  const handleContextAnalysisConfirm = (selectedContext: any) => {
    // 处理用户选择的上下文
    console.log('Selected context:', selectedContext)

    // 这里可以添加生成逻辑，根据选择的上下文生成内容
    message.success('已选择上下文，可以开始生成内容')

    setContextAnalysisVisible(false)
    setPlotDirection('')
  }

  if (!project) {
    return (
      <div style={{ textAlign: 'center', padding: '100px' }}>
        <Spin size="large" />
      </div>
    )
  }

  return (
    <Layout style={{ height: 'calc(100vh - 64px)', background: '#fff' }}>
      {/* 中间：主活动区 - Tab切换 */}
      <Content style={{ overflowY: 'auto', background: '#fff' }}>
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          size="large"
          tabBarStyle={{ padding: '0 24px', margin: 0 }}
          items={[
            {
              key: 'chapters',
              label: (
                <span>
                  <BookOutlined /> 章节创作
                </span>
              ),
              children: (
                <div style={{ padding: '0 24px 24px' }}>
                  {loadingChapter ? (
                    <div style={{ textAlign: 'center', padding: '100px 0' }}>
                      <Spin size="large" tip="加载章节中..." />
                    </div>
                  ) : currentChapter ? (
                    <>
                      {/* 章节标题栏 */}
                      <Card
                        bordered={false}
                        style={{
                          borderRadius: 8,
                          marginBottom: 16,
                          backgroundColor: '#f5f5f5',
                        }}
                        bodyStyle={{ padding: '16px 24px' }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <div>
                            <h2 style={{ margin: 0, fontSize: '20px', fontWeight: 600, color: '#262626' }}>
                              第{currentChapter.chapter_number}章 {currentChapter.title}
                            </h2>
                            <Space style={{ marginTop: 8, color: '#8c8c8c', fontSize: '14px' }}>
                              <span>{currentChapter.word_count}字</span>
                              <span>·</span>
                              <span>状态：</span>
                              <Select
                                value={currentChapter.status}
                                onChange={handleStatusChange}
                                options={CHAPTER_STATUS_OPTIONS}
                                style={{
                                  fontSize: '14px',
                                  fontWeight: 500,
                                }}
                                size="small"
                              />
                              {currentChapter.outline && (
                                <>
                                  <span>·</span>
                                  <span>已有大纲</span>
                                </>
                              )}
                            </Space>
                          </div>
                          <Space>
                            <Button
                              icon={<ArrowLeftOutlined />}
                              onClick={() => setCurrentChapter(null)}
                              style={{ borderColor: '#d9d9d9' }}
                            >
                              返回列表
                            </Button>
                            <Button
                              icon={<EditOutlined />}
                              onClick={handleEditOutline}
                              style={{ borderColor: '#d9d9d9' }}
                            >
                              编辑大纲
                            </Button>
                            <Button
                              onClick={handleOpenContextAnalysis}
                              type="default"
                            >
                              上下文分析
                            </Button>
                            <Button
                              onClick={handleSaveContent}
                              loading={saving}
                              type="default"
                            >
                              保存内容
                            </Button>
                            <Button type="primary">导出</Button>
                          </Space>
                        </div>
                      </Card>

                      {/* 编辑区 */}
                      <div style={{ marginTop: '24px' }}>
                        <TextArea
                          value={currentChapter.content || ''}
                          onChange={(e) => {
                            const content = e.target.value
                            setCurrentChapter({
                              ...currentChapter,
                              content: content,
                              word_count: content.length,
                            })
                          }}
                          placeholder="在此处开始创作...&#10;&#10;提示：&#10;1. 可以直接在编辑框中撰写内容&#10;2. 使用下方的AI指令输入框可以让AI辅助创作&#10;3. 内容会自动保存到本地状态，点击保存按钮提交到服务器"
                          autoSize={{
                            minRows: 20,
                            maxRows: 30,
                          }}
                          style={{
                            fontSize: '16px',
                            lineHeight: '1.8',
                            color: '#262626',
                            backgroundColor: '#fafafa',
                            borderColor: '#d9d9d9',
                            borderRadius: '4px',
                            padding: '16px',
                          }}
                        />
                      </div>

                      {/* AI指令输入 */}
                      <Card
                        bordered={false}
                        style={{
                          position: 'sticky',
                          bottom: 0,
                          zIndex: 100,
                          marginTop: '16px',
                          borderRadius: 8,
                          backgroundColor: '#f0f2ff',
                          border: '1px solid #d6e4ff',
                        }}
                        bodyStyle={{ padding: '16px' }}
                      >
                        <div style={{ marginBottom: '8px', fontSize: '14px', color: '#595959', fontWeight: 500 }}>
                          <RobotOutlined style={{ marginRight: '8px', color: '#1890ff' }} />
                          AI 辅助创作
                        </div>
                        <Input
                          placeholder="输入创作指令，例如：写一段主角与反派的对话..."
                          value={prompt}
                          onChange={(e) => setPrompt(e.target.value)}
                          onPressEnter={handleGenerate}
                          disabled={generating}
                          size="large"
                          suffix={
                            <Button
                              type="primary"
                              icon={<RobotOutlined />}
                              onClick={handleGenerate}
                              loading={generating}
                              style={{ marginLeft: '8px' }}
                            >
                              AI生成
                            </Button>
                          }
                        />
                      </Card>
                    </>
                  ) : (
                    <>
                      {/* 章节列表 */}
                      <Card
                        bordered={false}
                        style={{
                          borderRadius: 8,
                          marginBottom: 16,
                          backgroundColor: '#fafafa',
                        }}
                        bodyStyle={{ padding: '16px 24px' }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 600, color: '#262626' }}>
                            章节列表
                          </h2>
                          <Button
                            type="primary"
                            icon={<PlusOutlined />}
                            onClick={() => setCreateModalVisible(true)}
                          >
                            新建章节
                          </Button>
                        </div>
                      </Card>

                      {loading ? (
                        <div style={{ textAlign: 'center', padding: '60px 0' }}>
                          <Spin size="large" tip="加载中..." />
                        </div>
                      ) : chapters.length === 0 ? (
                        <Empty
                          description={
                            <div>
                              <p style={{ fontSize: '16px', color: '#8c8c8c' }}>暂无章节</p>
                              <Button
                                type="primary"
                                icon={<PlusOutlined />}
                                size="large"
                                style={{ marginTop: 16 }}
                                onClick={() => setCreateModalVisible(true)}
                              >
                                创建第一章
                              </Button>
                            </div>
                          }
                          style={{ padding: '80px 0' }}
                        />
                      ) : (
                        <List
                          dataSource={chapters}
                          renderItem={(chapter) => (
                            <List.Item
                              style={{
                                cursor: loadingChapter ? 'wait' : 'pointer',
                                padding: '20px',
                                borderRadius: 8,
                                border: '1px solid #e8e8e8',
                                marginBottom: 12,
                                transition: 'all 0.3s',
                                backgroundColor: '#fff',
                              }}
                              onClick={() => handleSelectChapter(chapter)}
                              className="chapter-item"
                              onMouseEnter={(e) => {
                                if (!loadingChapter) {
                                  e.currentTarget.style.borderColor = '#1890ff'
                                  e.currentTarget.style.boxShadow = '0 2px 8px rgba(24,144,255,0.15)'
                                }
                              }}
                              onMouseLeave={(e) => {
                                e.currentTarget.style.borderColor = '#e8e8e8'
                                e.currentTarget.style.boxShadow = 'none'
                              }}
                            >
                              <List.Item.Meta
                                title={
                                  <div style={{ fontSize: '16px', fontWeight: 500, color: '#262626' }}>
                                    第{chapter.chapter_number}章 {chapter.title}
                                  </div>
                                }
                                description={
                                  <Space style={{ marginTop: '8px' }}>
                                    <span style={{
                                      fontSize: '14px',
                                      color: chapter.word_count > 0 ? '#52c41a' : '#8c8c8c'
                                    }}>
                                      {chapter.word_count}字
                                    </span>
                                    <span>·</span>
                                    <span style={{
                                      fontSize: '14px',
                                      color: PROJECT_STATUS_CONFIG[chapter.status as keyof typeof PROJECT_STATUS_CONFIG]?.color || '#8c8c8c',
                                      fontWeight: 500
                                    }}>
                                      {PROJECT_STATUS_CONFIG[chapter.status as keyof typeof PROJECT_STATUS_CONFIG]?.label || chapter.status}
                                    </span>
                                    {chapter.has_outline && (
                                      <>
                                        <span>·</span>
                                        <span style={{ fontSize: '14px', color: '#1890ff' }}>
                                          已有大纲
                                        </span>
                                      </>
                                    )}
                                  </Space>
                                }
                              />
                            </List.Item>
                          )}
                        />
                      )}
                    </>
                  )}
                </div>
              ),
            },
            {
              key: 'characters',
              label: (
                <span>
                  <TeamOutlined /> 人物管理
                </span>
              ),
              children: (
                <div style={{ padding: '0 24px 24px' }}>
                  <div style={{ padding: '16px 0', borderBottom: '1px solid #f0f0f0' }}>
                    <h2 style={{ margin: 0 }}>人物管理</h2>
                  </div>
                  <CharacterManagement projectId={Number(id)} />
                </div>
              ),
            },
            {
              key: 'world',
              label: (
                <span>
                  <GlobalOutlined /> 世界观设定
                </span>
              ),
              children: (
                <div style={{ padding: '0 24px 24px' }}>
                  <div style={{ padding: '16px 0', borderBottom: '1px solid #f0f0f0' }}>
                    <h2 style={{ margin: 0 }}>世界观设定</h2>
                  </div>
                  <WorldSettingManagement projectId={Number(id)} />
                </div>
              ),
            },
          ]}
        />
      </Content>

      {/* 右侧：智能上下文面板 (300px) */}
      <Sider width={300} theme="light" style={{ borderLeft: '1px solid #f0f0f0', overflowY: 'auto' }}>
        <div style={{ padding: '16px' }}>
          <h3 style={{ marginBottom: 16 }}>
            <BulbOutlined /> 上下文
          </h3>

          {/* 项目信息 */}
          <Card
            size="small"
            title={<span style={{ fontSize: '14px', fontWeight: 600 }}>📚 项目信息</span>}
            style={{ marginBottom: 16, borderRadius: 8 }}
            headStyle={{ backgroundColor: '#fafafa', borderBottom: '1px solid #f0f0f0' }}
          >
            <p style={{ margin: '8px 0', fontSize: '13px', color: '#595959' }}>
              <strong style={{ color: '#262626' }}>书名：</strong>{project.title}
            </p>
            <p style={{ margin: '8px 0', fontSize: '13px', color: '#595959' }}>
              <strong style={{ color: '#262626' }}>类型：</strong>
              {(() => {
                try {
                  const genres = JSON.parse(project.genre)
                  return Array.isArray(genres) ? genres.join('、') : project.genre
                } catch {
                  return project.genre || '-'
                }
              })()}
            </p>
            <p style={{ margin: '8px 0', fontSize: '13px', color: '#595959' }}>
              <strong style={{ color: '#262626' }}>文风：</strong>
              <Button
                type="link"
                size="small"
                style={{ padding: 0, height: 'auto', fontSize: '13px' }}
                onClick={() => setStyleSettingsVisible(true)}
              >
                {project.style ? '设置文风' : '点击设置'}
              </Button>
            </p>
            <p style={{ margin: '8px 0', fontSize: '13px', color: '#595959' }}>
              <strong style={{ color: '#262626' }}>目标字数：</strong>{project.target_words_per_chapter}字/章
            </p>
          </Card>

          {/* 文风设置入口 */}
          <Card
            size="small"
            style={{ marginBottom: 16, borderRadius: 8, cursor: 'pointer', border: '1px dashed #d9d9d9' }}
            hoverable
            onClick={() => setStyleSettingsVisible(true)}
            bodyStyle={{ padding: '12px' }}
          >
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', marginBottom: '8px' }}>🎨</div>
              <div style={{ fontSize: '14px', fontWeight: 500, color: '#262626' }}>
                文风设置
              </div>
              <div style={{ fontSize: '12px', color: '#8c8c8c', marginTop: '4px' }}>
                {project.style ? `当前：${project.style}` : '未设置'}
              </div>
            </div>
          </Card>

          {/* 快捷指令 */}
          <Card
            size="small"
            title={<span style={{ fontSize: '14px', fontWeight: 600 }}>⚡ 快捷指令</span>}
            style={{ marginBottom: 16, borderRadius: 8 }}
            headStyle={{ backgroundColor: '#fafafa', borderBottom: '1px solid #f0f0f0' }}
          >
            <Space direction="vertical" style={{ width: '100%' }} size="small">
              <Button size="small" block style={{ textAlign: 'left' }}>
                插入场景描写
              </Button>
              <Button size="small" block style={{ textAlign: 'left' }}>
                插入对话
              </Button>
              <Button size="small" block style={{ textAlign: 'left' }}>
                插入心理活动
              </Button>
              <Button size="small" block style={{ textAlign: 'left' }}>
                插入战斗场面
              </Button>
            </Space>
          </Card>

          {/* 当前章节设定（有选中章节时显示） */}
          {currentChapter && activeTab === 'chapters' && (
            <Card
              size="small"
              title={<span style={{ fontSize: '14px', fontWeight: 600 }}>📖 当前章节</span>}
              style={{ marginBottom: 16, borderRadius: 8 }}
              headStyle={{ backgroundColor: '#fafafa', borderBottom: '1px solid #f0f0f0' }}
            >
              <p style={{ margin: '8px 0', fontSize: '13px', color: '#595959' }}>
                <strong style={{ color: '#262626' }}>章节号：</strong>第{currentChapter.chapter_number}章
              </p>
              <p style={{ margin: '8px 0', fontSize: '13px', color: '#595959' }}>
                <strong style={{ color: '#262626' }}>字数：</strong>{currentChapter.word_count}字
              </p>
              <p style={{ margin: '8px 0', fontSize: '13px', color: '#595959' }}>
                <strong style={{ color: '#262626' }}>状态：</strong>
                <span style={{
                  color: currentChapter.status === 'completed' ? '#52c41a' : '#faad14',
                  fontWeight: 500
                }}>
                  {currentChapter.status === 'completed' ? '已完成' : '草稿'}
                </span>
              </p>
              {currentChapter.summary && (
                <p style={{ margin: '8px 0', fontSize: '13px', color: '#595959' }}>
                  <strong style={{ color: '#262626' }}>摘要：</strong>
                  <div style={{ fontSize: '12px', color: '#8c8c8c', marginTop: 4, lineHeight: '1.6' }}>
                    {currentChapter.summary}
                  </div>
                </p>
              )}
            </Card>
          )}

          {/* 提示 */}
          <Card
            size="small"
            bordered={false}
            style={{
              background: 'linear-gradient(135deg, #f6ffed 0%, #f0f5ff 100%)',
              borderColor: '#b7eb8f',
              borderRadius: 8,
            }}
            bodyStyle={{ padding: '12px' }}
          >
            <p style={{ margin: 0, fontSize: '13px', color: '#52c41a', lineHeight: '1.6' }}>
              💡 <strong>提示：</strong>使用AI生成时，系统会自动注入当前项目的人物、世界观等设定，确保内容一致性。
            </p>
          </Card>
        </div>
      </Sider>

      {/* 创建章节模态框 */}
      <Modal
        title={<span style={{ fontSize: '18px', fontWeight: 600 }}>📝 新建章节</span>}
        open={createModalVisible}
        onOk={handleCreateChapter}
        onCancel={() => {
          setCreateModalVisible(false)
          setNewChapterTitle('')
        }}
        confirmLoading={creating}
        okText="创建"
        cancelText="取消"
        okButtonProps={{ style: { borderRadius: 6 } }}
        cancelButtonProps={{ style: { borderRadius: 6 } }}
      >
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <div>
            <div style={{ marginBottom: 8, fontWeight: 500, color: '#262626' }}>章节号：</div>
            <Input
              type="number"
              value={newChapterNumber}
              onChange={(e) => setNewChapterNumber(Number(e.target.value))}
              placeholder="请输入章节号"
              min={1}
              size="large"
            />
          </div>
          <div>
            <div style={{ marginBottom: 8, fontWeight: 500, color: '#262626' }}>章节标题：</div>
            <Input
              value={newChapterTitle}
              onChange={(e) => setNewChapterTitle(e.target.value)}
              placeholder="请输入章节标题"
              onPressEnter={handleCreateChapter}
              size="large"
            />
          </div>
        </Space>
      </Modal>

      {/* 编辑大纲模态框 */}
      <Modal
        title={<span style={{ fontSize: '18px', fontWeight: 600 }}>📋 编辑大纲</span>}
        open={outlineModalVisible}
        onOk={handleSaveOutline}
        onCancel={() => {
          setOutlineModalVisible(false)
          setOutlineContent('')
        }}
        confirmLoading={saving}
        okText="保存"
        cancelText="取消"
        width={600}
        okButtonProps={{ style: { borderRadius: 6 } }}
        cancelButtonProps={{ style: { borderRadius: 6 } }}
      >
        <div>
          <div style={{ marginBottom: 12, fontWeight: 500, color: '#262626' }}>大纲内容：</div>
          <Input.TextArea
            value={outlineContent}
            onChange={(e) => setOutlineContent(e.target.value)}
            placeholder="请输入本章大纲，包括主要情节、关键事件等...&#10;&#10;例如：&#10;1. 主角收到神秘信件&#10;2. 发现信中隐藏的线索&#10;3. 决定前往下一个地点调查"
            autoSize={{ minRows: 10, maxRows: 18 }}
            style={{ fontSize: '14px', lineHeight: '1.6' }}
          />
        </div>
      </Modal>

      {/* 文风设置模态框 */}
      <ProjectStyleSettings
        visible={styleSettingsVisible}
        onClose={() => setStyleSettingsVisible(false)}
        project={project}
        onSave={handleSaveStyleSettings}
      />

      {/* 上下文分析模态框 */}
      <ContextAnalysisView
        visible={contextAnalysisVisible}
        projectId={Number(id)}
        plotDirection={plotDirection}
        chapterNumber={currentChapter?.chapter_number || 0}
        previousChapterId={chapters.find(c => c.chapter_number === (currentChapter?.chapter_number || 0) - 1)?.id}
        onConfirm={handleContextAnalysisConfirm}
        onCancel={handleCloseContextAnalysis}
      />
    </Layout>
  )
}

export default ProjectDetail
