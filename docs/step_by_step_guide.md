# 分步骤部署操作指南

## 准备阶段

### 1. 注册腾讯云账号
1. 访问 [腾讯云官网](https://cloud.tencent.com)
2. 点击"免费注册"
3. 使用手机号或邮箱注册
4. 完成手机验证

### 2. 实名认证
1. 登录控制台 → 账号信息 → 实名认证
2. 选择"个人认证"
3. 上传身份证正反面照片
4. 等待审核（通常5-10分钟）

### 3. 开通必要服务
1. **云函数SCF**：
   - 控制台 → 产品 → 云函数 → 立即使用
   - 同意服务条款并开通

2. **静态网站托管**：
   - 控制台 → 产品 → 静态网站托管 → 立即使用
   - 开通服务（免费）

---

## 后端部署详细步骤

### 1. 代码准备
```bash
# 1. 进入后端目录
cd NoteFlow/backend  

# 2. 创建云函数版本的requirements.txt
echo "fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
openai==1.3.0
requests==2.31.0
pydantic==2.5.0
mangum==0.17.0" > requirements-scf.txt

# 3. 创建部署目录
mkdir scf-deploy
cd scf-deploy

# 4. 复制源代码
cp ../main.py .
cp ../handwriting_recognizer.py .
cp ../requirements-scf.txt requirements.txt

# 5. 安装依赖到本地
pip install -r requirements.txt -t ./

# 6. 创建云函数入口文件
```

创建 `scf_handler.py`：
```python
import json
import os
from mangum import Mangum
from main import app

# 云函数处理器
handler = Mangum(app, lifespan="off")

def main_handler(event, context):
    """
    腾讯云函数入口点
    """
    return handler(event, context)
```

```bash
# 7. 打包部署文件
zip -r note-agent-scf.zip . -x "*.pyc" "__pycache__/*" "*.git*"
```

### 2. 腾讯云函数部署
1. **创建函数**：
   - 控制台 → 云函数 → 函数服务 → 新建
   - 函数名称：`note-agent-api`
   - 运行环境：`Python 3.9`
   - 创建方式：`空白函数`

2. **上传代码**：
   - 提交方法：`本地上传zip包`
   - 上传刚才打包的 `note-agent-scf.zip`
   - 入口函数：`scf_handler.main_handler`

3. **配置参数**：
   ```
   内存：512MB
   超时时间：60秒
   环境变量：
   - DASHSCOPE_API_KEY: sk-your-api-key
   - FLMO_WEBHOOK_URL: https://flomoapp.com/iwh/your-webhook
   ```

4. **创建API网关触发器**：
   - 触发器配置 → 创建触发器
   - 触发方式：`API网关触发器`
   - 集成响应：`启用`
   - 鉴权方法：`免鉴权`
   - 路径：`/`
   - 请求方法：`ANY`

5. **获取API地址**：
   - 触发器管理中复制访问路径
   - 格式类似：`https://service-xxx.gz.apigw.tencentcs.com/release/`

### 3. 测试后端API
```bash
# 测试健康检查
curl https://your-api-gateway-url.com/

# 应该返回：{"message":"笔记Agent API服务正在运行"}
```

---

## 前端部署详细步骤

### 1. 修改前端配置
编辑 `PRD/frontend/src/App.jsx`，修改API地址：
```javascript
// 在文件顶部添加
const API_BASE_URL = 'https://your-api-gateway-url.com';

// 修改所有API调用
const uploadImage = async (file) => {
  const formData = new FormData();
  formData.append('image', file);
  
  const response = await fetch(`${API_BASE_URL}/api/upload_image`, {
    method: 'POST',
    body: formData,
  });
  
  return response.json();
};
```

### 2. 构建前端
```bash
cd NoteFlow/frontend

# 安装依赖
npm install

# 构建生产版本
npm run build
```

### 3. 部署到静态网站托管
1. **创建静态站点**：
   - 控制台 → 静态网站托管 → 立即使用
   - 选择按量计费
   - 创建新的环境

2. **上传文件**：
   - 文件管理 → 上传文件夹
   - 选择 `PRD/frontend/dist` 文件夹
   - 等待上传完成

3. **配置域名**：
   - 基础配置 → 域名管理
   - 复制默认域名（格式：`xxx.tcloudbaseapp.com`）

4. **配置索引文档**：
   - 基础配置 → 基础设置
   - 索引文档：`index.html`
   - 错误文档：`index.html`

---

## 域名配置（可选）

### 1. 购买域名
1. 控制台 → 域名注册 → 域名查询
2. 输入想要的域名
3. 选择合适的后缀（.com/.cn/.net等）
4. 加入购物车并支付

### 2. 域名解析
1. 控制台 → 域名服务 → 我的域名
2. 点击域名进入管理页面
3. DNS解析 → 快速添加网站解析
4. 输入静态网站托管的默认域名

### 3. SSL证书申请
1. 控制台 → SSL证书 → 我的证书
2. 申请免费证书 → DV域名验证型
3. 绑定域名
4. 完成域名验证
5. 下载证书并配置到静态网站托管

---

## 环境变量管理

### 开发环境 (.env.local)
```
VITE_API_BASE_URL=http://localhost:8000
```

### 生产环境
在构建时通过环境变量传递：
```bash
VITE_API_BASE_URL=https://your-api-gateway-url.com npm run build
```

---

## 验证部署

### 1. 后端验证
```bash
# 测试健康检查
curl https://your-api-gateway-url.com/

# 测试CORS
curl -H "Origin: https://your-domain.com" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     https://your-api-gateway-url.com/api/upload_image
```

### 2. 前端验证
1. 访问你的域名
2. 尝试上传图片
3. 检查浏览器开发者工具的Network标签
4. 确认API调用正常

### 3. 完整流程测试
1. 上传手写笔记图片
2. 查看识别结果
3. 生成标签
4. 编辑内容
5. 发布到flomo

---

## 监控和日志

### 1. 云函数日志
- 控制台 → 云函数 → 函数管理 → 日志查询
- 可以查看详细的调用日志和错误信息

### 2. 静态网站访问统计
- 控制台 → 静态网站托管 → 统计分析
- 查看访问量、流量使用等

### 3. 设置告警
- 控制台 → 云监控 → 告警管理
- 设置云函数调用失败、超时等告警

---

## 故障排除

### 常见问题
1. **云函数冷启动慢**：
   - 解决：开启预置并发（付费功能）
   - 或者：设置定时触发器保持热启

2. **CORS错误**：
   - 检查API网关的CORS配置
   - 确认前端域名在允许列表中

3. **图片上传失败**：
   - 检查文件大小限制（云函数6MB）
   - 检查超时设置

4. **API调用超时**：
   - 增加云函数超时时间
   - 优化代码性能

### 成本优化建议
1. **合理设置内存**：根据实际使用调整函数内存
2. **定期清理日志**：避免日志占用过多存储空间
3. **监控用量**：设置用量告警，避免意外费用

---

## 后续维护

### 代码更新流程
1. 本地修改代码
2. 重新打包：`zip -r note-agent-scf.zip . -x "*.pyc" "__pycache__/*"`
3. 云函数控制台上传新的zip包
4. 前端重新构建并上传

### 版本管理
建议使用Git管理代码版本，并为每次部署打标签：
```bash
git tag -a v1.0.0 -m "初始部署版本"
git push origin v1.0.0
```

这样你就完成了完整的云端部署！ 
