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
  NavBar
} from 'antd-mobile';
import { CheckOutline, CloseOutline } from 'antd-mobile-icons';

export default function App() {
  const [step, setStep] = useState('upload'); // upload | loading | editing | done | error
  const [image, setImage] = useState(null);
  const [imageUrl, setImageUrl] = useState('');
  const [text, setText] = useState('');
  const [tags, setTags] = useState([]);
  const [tagInput, setTagInput] = useState('');
  const [loadingMsg, setLoadingMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  // 图片上传处理
  const handleImageUpload = async (file) => {
    console.log('=== handleImageUpload 调试信息 ===');
    console.log('接收到的参数:', file);
    console.log('参数类型:', typeof file);
    console.log('是否为 File 对象:', file instanceof File);
    console.log('是否为 Blob 对象:', file instanceof Blob);
    console.log('参数详细内容:', file);
    
    // 确保我们有一个真正的File对象
    let actualFile = file;
    if (file && file.originFileObj) {
      // Antd Mobile可能将真正的File对象包装在originFileObj中
      console.log('发现 originFileObj:', file.originFileObj);
      actualFile = file.originFileObj;
    }
    
    console.log('最终使用的文件对象:', actualFile);
    console.log('最终文件对象类型:', typeof actualFile);
    console.log('最终文件是否为 File:', actualFile instanceof File);
    
    if (!(actualFile instanceof File)) {
      console.error('错误：不是有效的File对象');
      setErrorMsg('文件格式不正确，请重新选择');
      setStep('error');
      return;
    }
    
    setStep('loading');
    setLoadingMsg('正在识别手写内容...');
    
    const formData = new FormData();
    formData.append('image', actualFile);
    formData.append('prompt_template', 'default');
    
    console.log('FormData 内容:');
    for (let [key, value] of formData.entries()) {
      console.log(key, ':', value);
      if (value instanceof File) {
        console.log(`  - ${key} 是 File 对象, name: ${value.name}, size: ${value.size}, type: ${value.type}`);
      }
    }
    
    try {
      console.log('开始发送请求...');
      const res = await axios.post('/api/upload_image', formData);
      console.log('请求成功，响应:', res.data);
      
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
          setTags(tagRes.data.tags);
        }
        
        setStep('editing');
      } else {
        setErrorMsg(res.data.msg || '未检测到手写内容');
        setStep('error');
      }
    } catch (error) {
      console.error('上传错误详情:', error);
      console.error('错误响应:', error.response?.data);
      setErrorMsg('图片上传或识别失败，请重试');
      setStep('error');
    }
  };

  // 添加标签
  const handleAddTag = () => {
    const val = tagInput.trim().replace(/^#/, '');
    if (val && !tags.includes(val)) {
      setTags([...tags, val]);
      setTagInput('');
    }
  };

  // 删除标签
  const handleRemoveTag = (tag) => {
    setTags(tags.filter(t => t !== tag));
  };

  // 发布到flomo
  const handlePublish = async () => {
    setStep('loading');
    setLoadingMsg('正在发布到flomo...');
    
    try {
      const res = await axios.post('/api/publish_note', {
        text,
        tags,
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
                  console.log('=== ImageUploader onChange 调试信息 ===');
                  console.log('files 参数:', files);
                  console.log('files 数组长度:', files.length);
                  // 不在这里处理文件上传，因为这里接收到的已经不是原始File对象
                }}
                upload={async (file) => {
                  console.log('=== ImageUploader upload 调试信息 ===');
                  console.log('upload file 参数:', file);
                  console.log('upload file 类型:', typeof file);
                  console.log('upload file 是否为 File:', file instanceof File);
                  
                  // 在这里直接处理文件上传，因为这里能拿到真正的File对象
                  if (file instanceof File) {
                    console.log('开始在upload中处理文件...');
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
                  <Tag
                    key={tag}
                    color='#1677ff'
                    closable
                    onClose={() => handleRemoveTag(tag)}
                  >
                    #{tag}
                  </Tag>
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