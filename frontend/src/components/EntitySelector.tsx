import { useState, useEffect } from 'react'
import { Select, Tag, Space, Spin } from 'antd'
import { UserOutlined, GlobalOutlined } from '@ant-design/icons'
import { characterApi, worldSettingApi } from '../services/api'
import type { Character, WorldSetting } from '../types'

interface EntitySelectorProps {
  value?: number[]
  onChange?: (value: number[]) => void
  projectId: number
  placeholder?: string
}

const EntitySelector = ({ value = [], onChange, projectId, placeholder }: EntitySelectorProps) => {
  const [loading, setLoading] = useState(false)
  const [characters, setCharacters] = useState<Character[]>([])
  const [worldSettings, setWorldSettings] = useState<WorldSetting[]>([])
  const [searchText, setSearchText] = useState('')

  useEffect(() => {
    fetchEntities()
  }, [projectId])

  const fetchEntities = async () => {
    setLoading(true)
    try {
      // 并行获取人物和世界观设定
      const [charRes, worldRes] = await Promise.all([
        characterApi.list(projectId),
        worldSettingApi.list(projectId)
      ])

      if (charRes.data.code === 200) {
        setCharacters(charRes.data.data.characters)
      }

      if (worldRes.data.code === 200) {
        setWorldSettings(worldRes.data.data.settings)
      }
    } catch (error) {
      console.error('加载实体失败', error)
    } finally {
      setLoading(false)
    }
  }

  // 过滤实体
  const filteredCharacters = characters.filter(c =>
    c.name.toLowerCase().includes(searchText.toLowerCase())
  )

  const filteredWorldSettings = worldSettings.filter(s =>
    s.name.toLowerCase().includes(searchText.toLowerCase())
  )

  // 根据ID获取实体名称
  const getEntityName = (id: number) => {
    const character = characters.find(c => c.id === id)
    if (character) return `${character.name} (人物)`

    const setting = worldSettings.find(s => s.id === id)
    if (setting) return `${setting.name} (设定)`

    return `实体 ${id}`
  }

  // Select的选项数据
  const selectOptions = [
    {
      label: `人物 (${filteredCharacters.length})`,
      title: '人物',
      options: filteredCharacters.map(c => ({
        label: c.name,
        value: c.id,
        key: `char-${c.id}`,
      }))
    },
    {
      label: `世界观 (${filteredWorldSettings.length})`,
      title: '世界观',
      options: filteredWorldSettings.map(s => ({
        label: s.name,
        value: s.id,
        key: `world-${s.id}`,
      }))
    },
  ].filter(group => group.options.length > 0)

  return (
    <div>
      <Select
        mode="multiple"
        style={{ width: '100%' }}
        placeholder={placeholder || '选择关联的实体'}
        value={value}
        onChange={onChange}
        filterOption={false}
        onSearch={setSearchText}
        searchValue={searchText}
        loading={loading}
        showSearch
        allowClear
        maxTagCount={5}
        options={selectOptions}
        notFoundContent={searchText ? '未找到匹配的实体' : '暂无可关联的实体'}
      />

      {/* 已选择的实体标签展示 */}
      {value.length > 0 && (
        <div style={{ marginTop: 8 }}>
          <Space size={4} wrap>
            {value.slice(0, 10).map(id => {
              const character = characters.find(c => c.id === id)
              const setting = worldSettings.find(s => s.id === id)

              return (
                <Tag
                  key={id}
                  closable
                  onClose={() => {
                    onChange?.(value.filter(v => v !== id))
                  }}
                  color={character ? 'blue' : 'green'}
                  icon={character ? <UserOutlined /> : <GlobalOutlined />}
                >
                  {character ? character.name : setting?.name}
                </Tag>
              )
            })}
            {value.length > 10 && (
              <Tag>+{value.length - 10} 更多</Tag>
            )}
          </Space>
        </div>
      )}
    </div>
  )
}

export default EntitySelector
