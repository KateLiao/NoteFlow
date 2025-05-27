import React, { useState } from 'react';
import axios from 'axios';
import {
  Button,
  ImageUploader,
  TextArea,
  Tag,
  Input,
  Toast,
  SpinLoading,
  Card,
  Space,
  NavBar,
  Dialog
} from 'antd-mobile';
import { CheckOutline, CloseOutline, CloseCircleOutline } from 'antd-mobile-icons';

export default function App() {
  const [step, setStep] = useState('upload'); // upload | loading | editing | done | error
  const [image, setImage] = useState(null);
  const [imageUrl, setImageUrl] = useState('');
  const [text, setText] = useState('');
  const [tags, setTags] = useState([]); // 标签对象数组: [{id, text, source}]
  const [tagInput, setTagInput] = useState('');
  const [loadingMsg, setLoadingMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  
  // 图片上传处理
  const handleImageUpload = async (file) => {
    // 确保我们有一个真正的File对象
    let actualFile = file;
    if (file && file.originFileObj) {
      // Antd Mobile可能将真正的File对象包装在originFileObj中
      actualFile = file.originFileObj;
    }
    
    if (!(actualFile instanceof File)) {
      setErrorMsg('文件格式不正确，请重新选择');
      setStep('error');
      return;
    }
    
    setStep('loading');
    setLoadingMsg('正在识别手写内容...');
    
    const formData = new FormData();
    formData.append('image', actualFile);
    formData.append('prompt_template', 'default');
    
    try {
      const res = await axios.post('/api/upload_image', formData);
      
      if (res.data.success) {
        setText(res.data.text);
        setImageUrl(res.data.image_url);
        setImage(actualFile);
        
        // 自动生成标签
        setLoadingMsg('正在生成标签...');
        const tagRes = await axios.post('/api/generate_tags', {
          text: res.data.text
        });
        
        if (tagRes.data.success) {
          // 将AI返回的字符串数组转换为标签对象数组
          const aiTags = tagRes.data.tags.map((tagText, index) => ({
            id: `ai_tag_${Date.now()}_${index}`,
            text: tagText,
            source: 'ai'
          }));
          
          setTags(aiTags);
        }
        
        setStep('editing');
      } else {
        setErrorMsg(res.data.msg || '未检测到手写内容');
        setStep('error');
      }
    } catch (error) {
      setErrorMsg('图片上传或识别失败，请重试');
      setStep('error');
    }
  };

  // 添加标签
  const handleAddTag = () => {
    const val = tagInput.trim().replace(/^#/, '');
    
    if (val && !tags.some(tag => tag.text === val)) {
      const newTag = {
        id: `tag_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        text: val,
        source: 'user'
      };
      
      setTags([...tags, newTag]);
      setTagInput('');
    }
  };

  // 删除标签
  const handleRemoveTag = (tag) => {
    setTags(tags.filter(t => t.id !== tag.id));
  };

  // 删除标签（带确认）
  const handleDeleteTag = (tag) => {
    Dialog.confirm({
      title: '删除标签',
      content: `确定要删除标签 "#${tag.text}" 吗？`,
      confirmText: '删除',
      cancelText: '取消',
      onConfirm: () => {
        handleRemoveTag(tag);
        Toast.show({
          icon: 'success',
          content: '标签已删除'
        });
      }
    });
  };

  // 发布到flomo
  const handlePublish = async () => {
    setStep('loading');
    setLoadingMsg('正在发布到flomo...');
    
    try {
      // 将标签对象数组转换为字符串数组
      const tagTexts = tags.map(tag => tag.text);
      
      const res = await axios.post('/api/publish_note', {
        text,
        tags: tagTexts, // 发送字符串数组保持API兼容
        image_urls: [imageUrl]
      });
      
      if (res.data.success) {
        Toast.show({
          icon: 'success',
          content: '已成功同步到flomo！'
        });
        setStep('done');
      } else {
        setErrorMsg(res.data.msg || '发布失败');
        setStep('error');
      }
    } catch (error) {
      setErrorMsg('发布失败，请重试');
      setStep('error');
    }
  };

  // 重新开始
  const handleRetry = () => {
    setImage(null);
    setImageUrl('');
    setText('');
    setTags([]);
    setTagInput('');
    setStep('upload');
    setErrorMsg('');
  };

  // 返回到上传页面
  const handleBack = () => {
    setImage(null);
    setImageUrl('');
    setText('');
    setTags([]);
    setTagInput('');
    setStep('upload');
    setErrorMsg('');
  };

  return (
    <div className="container">
      {/* 根据不同步骤显示不同的NavBar */}
      {step === 'editing' ? (
        <NavBar onBack={handleBack}>手写笔记智能识别 & flomo同步</NavBar>
      ) : (
        <NavBar>手写笔记智能识别 & flomo同步</NavBar>
      )}
      
      <div style={{ padding: '16px' }}>
        {/* 步骤1：上传图片 */}
        {step === 'upload' && (
          <Card>
            <Space direction='vertical' style={{ width: '100%' }}>
              <ImageUploader
                value={[]}
                onChange={(files) => {
                }}
                upload={async (file) => {
                  if (file instanceof File) {
                    handleImageUpload(file);
                  }
                  
                  // 返回URL用于显示预览
                  return {
                    url: URL.createObjectURL(file)
                  };
                }}
                maxCount={1}
                accept="image/*"
              />
              <div style={{ textAlign: 'center', color: '#999', fontSize: '14px' }}>
                支持拍照或选择本地图片，自动识别手写内容
              </div>
            </Space>
          </Card>
        )}

        {/* 步骤2：loading */}
        {step === 'loading' && (
          <Card>
            <div style={{ textAlign: 'center', padding: '40px 0' }}>
              <SpinLoading style={{ fontSize: '24px' }} />
              <div style={{ marginTop: '16px', color: '#1677ff' }}>{loadingMsg}</div>
            </div>
          </Card>
        )}

        {/* 步骤3：编辑文本和标签 */}
        {step === 'editing' && (
          <Space direction='vertical' style={{ width: '100%' }}>
            {/* 图片预览 */}
            <Card title="图片预览">
              {image && (
                <img 
                  src={URL.createObjectURL(image)} 
                  alt="预览" 
                  style={{ width: '100%', borderRadius: '8px' }}
                />
              )}
            </Card>

            {/* 识别文本 */}
            <Card title="识别文本">
              <TextArea
                placeholder="识别到的文本内容"
                value={text}
                onChange={setText}
                rows={4}
                showCount
                maxLength={500}
              />
            </Card>

            {/* 标签管理 */}
            <Card title="标签">
              <Space wrap style={{ marginBottom: '16px' }}>
                {tags.map(tag => (
                  <div
                    key={tag.id}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      backgroundColor: tag.source === 'ai' ? '#f6ffed' : '#e6f7ff',
                      border: `1px solid ${tag.source === 'ai' ? '#52c41a' : '#1677ff'}`,
                      borderRadius: '16px',
                      padding: '8px 12px',
                      fontSize: '14px',
                      fontWeight: '500',
                      margin: '4px',
                      minHeight: '32px'
                    }}
                  >
                    {tag.source === 'ai' && (
                      <span style={{ marginRight: '4px', fontSize: '14px' }}>🤖</span>
                    )}
                    <span style={{ 
                      color: tag.source === 'ai' ? '#52c41a' : '#1677ff',
                      marginRight: '6px'
                    }}>
                      #{tag.text}
                    </span>
                    <CloseCircleOutline
                      style={{
                        fontSize: '16px',
                        color: '#999',
                        cursor: 'pointer',
                        minWidth: '16px',
                        minHeight: '16px'
                      }}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteTag(tag);
                      }}
                    />
                  </div>
                ))}
              </Space>
              
              <Space>
                <Input
                  placeholder="输入标签"
                  value={tagInput}
                  onChange={setTagInput}
                  onEnterPress={handleAddTag}
                  style={{ flex: 1 }}
                />
                <Button color='primary' size='small' onClick={handleAddTag}>
                  添加
                </Button>
              </Space>
              
              {tags.length > 0 && (
                <div style={{ 
                  marginTop: '8px', 
                  fontSize: '12px', 
                  color: '#999',
                  textAlign: 'center'
                }}>
                  点击标签右侧 ✕ 按钮可删除，🤖 表示AI生成的标签
                </div>
              )}
            </Card>

            {/* 发布按钮 */}
            <Button 
              color='success' 
              size='large' 
              block 
              onClick={handlePublish}
              style={{ marginTop: '16px' }}
            >
              发布到flomo
            </Button>

            {/* 重新上传按钮 */}
            <Button 
              color='default' 
              size='large' 
              block 
              onClick={handleBack}
              style={{ marginTop: '8px' }}
            >
              重新上传图片
            </Button>
          </Space>
        )}

        {/* 步骤4：发布成功 */}
        {step === 'done' && (
          <Card>
            <div style={{ textAlign: 'center', padding: '40px 0' }}>
              <CheckOutline style={{ fontSize: '48px', color: '#00b578' }} />
              <div style={{ marginTop: '16px', fontSize: '18px', fontWeight: 'bold', color: '#00b578' }}>
                已同步到flomo！
              </div>
              <Button 
                color='primary' 
                onClick={handleRetry}
                style={{ marginTop: '24px' }}
              >
                再记一条
              </Button>
            </div>
          </Card>
        )}

        {/* 步骤5：错误提示 */}
        {step === 'error' && (
          <Card>
            <div style={{ textAlign: 'center', padding: '40px 0' }}>
              <CloseOutline style={{ fontSize: '48px', color: '#ff3141' }} />
              <div style={{ marginTop: '16px', fontSize: '16px', color: '#ff3141' }}>
                {errorMsg}
              </div>
              <Button 
                color='primary' 
                onClick={handleRetry}
                style={{ marginTop: '24px' }}
              >
                重新上传
              </Button>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
} 