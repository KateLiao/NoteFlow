# NoteFlow

一个智能手写笔记识别和处理工具，支持拍照识别手写文本、自动生成标签、编辑内容并同步到 flomo。

## ✨ 功能特点

- 📸 **图片上传**：支持拍照或选择图片
- 🔍 **手写识别**：基于通义千问VL模型的高精度识别
- 🏷️ **智能标签**：AI自动生成相关标签
- ✏️ **编辑功能**：可编辑识别文本和标签
- 📱 **移动适配**：响应式设计，完美适配手机端
- 🔄 **flomo同步**：一键发布到flomo笔记

## 🚀 快速开始

### 1. 环境配置

#### 方法一：自动设置（推荐）
```bash
# Linux/Mac
./setup.sh

# Windows
setup.bat
```

#### 方法二：手动设置
```bash
# 1. 复制环境变量模板
cp env.example .env

# 2. 编辑 .env 文件，填入你的API密钥
# DASHSCOPE_API_KEY=你的通义千问API密钥
# FLMO_WEBHOOK_URL=你的flomo webhook地址
```

### 2. 获取API密钥

#### 通义千问API密钥
1. 访问 [通义千问控制台](https://dashscope.console.aliyun.com/)
2. 登录/注册阿里云账号
3. 开通DashScope服务
4. 创建API Key

#### flomo webhook
1. 打开flomo应用
2. 进入 设置 → API & webhook
3. 创建新的webhook
4. 复制webhook URL

### 3. 启动项目

#### 后端启动
```bash
cd backend
pip install -r requirements.txt
python main.py
```

#### 前端启动
```bash
cd frontend
npm install
npm run dev
```

访问 `http://localhost:5173` 开始使用！

## 🛠️ 技术栈

- **前端**：React + Vite + Antd Mobile
- **后端**：Python + FastAPI
- **AI**：通义千问VL模型
- **集成**：flomo API

## 📁 项目结构

```
NoteFlow/
├── backend/              # 后端服务
│   ├── main.py          # FastAPI主服务
│   ├── handwriting_recognizer.py  # 核心识别模块
│   └── requirements.txt # Python依赖
├── frontend/            # 前端应用
│   ├── src/
│   │   ├── App.jsx     # 主应用组件
│   │   └── main.jsx    # 入口文件
│   ├── index.html      # HTML模板
│   └── package.json    # Node.js依赖
├── docs/               # 部署文档
│   ├── README.md       # 文档导航
│   └── ...            # 详细部署指南
├── env.example         # 环境变量模板
├── .gitignore         # Git忽略文件
├── setup.sh           # Linux/Mac环境设置
└── setup.bat          # Windows环境设置
```

## 🔒 安全须知

⚠️ **重要：API密钥安全**

- `.env` 文件包含敏感信息，已被 `.gitignore` 排除
- 请勿在代码中硬编码API密钥
- 生产环境请使用云服务商的密钥管理服务
- 定期轮换API密钥

## ☁️ 云部署

详细的云部署方案请查看 [docs/README.md](./docs/README.md)

支持的部署方式：
- **腾讯云全家桶**（推荐）：约60元/年
- **阿里云组合**：约84元/年  
- **华为云方案**：约68元/年

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📄 开源协议

本项目采用 MIT 协议 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🆘 常见问题

### Q: 提示"DASHSCOPE_API_KEY environment variable is required"
A: 请确保已正确配置 `.env` 文件，并填入有效的API密钥。

### Q: 图片上传失败
A: 检查图片大小（建议<6MB）和格式（支持jpg/png/webp）。

### Q: flomo同步失败
A: 检查webhook URL是否正确，网络是否正常。

### Q: 识别结果不准确
A: 确保图片清晰，手写内容工整，避免复杂背景。

---

## 📞 技术支持

如有问题，请：
1. 查看 [issues](../../issues) 中是否有类似问题
2. 创建新的 issue 描述问题
3. 提供错误日志和复现步骤

**让手写笔记数字化更简单！** 🎉 