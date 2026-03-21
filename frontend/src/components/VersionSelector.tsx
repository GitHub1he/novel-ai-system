import React, { useState } from 'react';
import { Modal, Radio, Button, Typography, Space, Divider, Card, Row, Col, Input } from 'antd';
import { EyeOutlined, EditOutlined, CheckOutlined } from '@ant-design/icons';
import type { GeneratedVersion } from '../types';

const { Title, Text, Paragraph } = Typography;

interface VersionSelectorProps {
  visible: boolean;
  versions: GeneratedVersion[];
  onSelect: (versionId: string, editedContent?: string) => Promise<void>;
  onClose: () => void;
}

const VersionSelector: React.FC<VersionSelectorProps> = ({
  visible,
  versions,
  onSelect,
  onClose,
}) => {
  const [selectedVersionId, setSelectedVersionId] = useState<string>('');
  const [previewVersion, setPreviewVersion] = useState<GeneratedVersion | null>(null);
  const [editMode, setEditMode] = useState<{ [key: string]: string }>({});
  const [isEditing, setIsEditing] = useState(false);

  const handleSelectVersion = (e: any) => {
    setSelectedVersionId(e.target.value);
  };

  const handlePreview = (version: GeneratedVersion) => {
    setPreviewVersion(version);
    setEditMode({ ...editMode, [version.version_id]: version.content });
    setIsEditing(false);
  };

  const handleEdit = (versionId: string) => {
    setEditMode({ ...editMode, [versionId]: editMode[versionId] });
    setIsEditing(true);
  };

  const handleContentChange = (versionId: string, content: string) => {
    setEditMode({ ...editMode, [versionId]: content });
  };

  const handleApply = async () => {
    if (!selectedVersionId) return;

    const editedContent = editMode[selectedVersionId];
    await onSelect(selectedVersionId, editedContent);
  };

  const handleClose = () => {
    setSelectedVersionId('');
    setPreviewVersion(null);
    setEditMode({});
    setIsEditing(false);
    onClose();
  };

  return (
    <>
      <Modal
        title="选择生成版本"
        open={visible}
        onCancel={handleClose}
        footer={
          <Space>
            <Button onClick={handleClose}>取消</Button>
            <Button
              type="primary"
              onClick={handleApply}
              disabled={!selectedVersionId}
            >
              使用此版本
            </Button>
          </Space>
        }
        width={800}
        destroyOnClose
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <Title level={4}>请选择一个版本：</Title>

          <Radio.Group value={selectedVersionId} onChange={handleSelectVersion}>
            {versions.map((version) => (
              <Card
                key={version.version_id}
                size="small"
                style={{ marginBottom: 16 }}
                bodyStyle={{ padding: '16px' }}
              >
                <Row gutter={[16, 16]} align="middle">
                  <Col flex="auto">
                    <Radio
                      value={version.version_id}
                      style={{ marginBottom: 8 }}
                    >
                      <Title level={5} style={{ margin: 0 }}>
                        版本 {version.version_id}
                      </Title>
                    </Radio>
                    <Text type="secondary">
                      字数: {version.word_count}
                    </Text>
                  </Col>
                  <Col>
                    <Space>
                      <Button
                        type="text"
                        icon={<EyeOutlined />}
                        onClick={() => handlePreview(version)}
                      >
                        查看完整内容
                      </Button>
                      <Button
                        type="text"
                        icon={<EditOutlined />}
                        onClick={() => handleEdit(version.version_id)}
                        disabled={selectedVersionId !== version.version_id}
                      >
                        编辑
                      </Button>
                    </Space>
                  </Col>
                </Row>

                {selectedVersionId === version.version_id && (
                  <>
                    <Divider />
                    <div>
                      <Title level={5}>摘要：</Title>
                      <Paragraph>{version.summary}</Paragraph>

                      {isEditing && editMode[version.version_id] && (
                        <div>
                          <Title level={5}>编辑内容：</Title>
                          <Input.TextArea
                            value={editMode[version.version_id]}
                            onChange={(e) => handleContentChange(version.version_id, e.target.value)}
                            rows={8}
                            style={{ marginTop: 8 }}
                          />
                        </div>
                      )}
                    </div>
                  </>
                )}
              </Card>
            ))}
          </Radio.Group>
        </Space>
      </Modal>

      <Modal
        title={`版本 ${previewVersion?.version_id} - 完整内容`}
        open={!!previewVersion}
        onCancel={() => setPreviewVersion(null)}
        footer={null}
        width={900}
        style={{ top: 20 }}
        destroyOnClose
      >
        {previewVersion && (
          <div>
            <Space style={{ marginBottom: 16 }}>
              <Text strong>字数:</Text>
              <Text>{previewVersion.word_count}</Text>
              <Divider type="vertical" />
              <Text strong>摘要:</Text>
              <Text>{previewVersion.summary}</Text>
            </Space>

            <Divider />

            <Input.TextArea
              value={editMode[previewVersion.version_id] || previewVersion.content}
              onChange={(e) => handleContentChange(previewVersion.version_id, e.target.value)}
              rows={12}
              readOnly={!isEditing}
              style={{ backgroundColor: isEditing ? '#fafafa' : 'white' }}
            />

            {isEditing && (
              <Space style={{ marginTop: 16 }}>
                <Button type="primary" icon={<CheckOutlined />}>
                  保存编辑
                </Button>
                <Button onClick={() => setIsEditing(false)}>
                  取消编辑
                </Button>
              </Space>
            )}
          </div>
        )}
      </Modal>
    </>
  );
};

export default VersionSelector;