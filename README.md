# 🖋️ NoteFlow - 智能手写笔记识别工具

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688.svg)](https://fastapi.tiangolo.com/)

**基于通义千问VL模型的手写笔记识别工具，支持智能标签生成和flomo同步**

[功能演示](#-功能特色) •
[快速开始](#-快速开始) •
[部署指南](#-部署指南) •
[API文档](#-api文档)

</div>

## 📱 功能特色

### 🎯 核心功能
- **📷 智能识别**: 基于通义千问VL模型，精准识别手写内容
- **🏷️ 智能标签**: AI自动生成相关标签，便于分类管理
- **✏️ 实时编辑**: 支持识别结果的实时编辑和优化
- **🔄 一键同步**: 直接同步到flomo，无缝融入笔记工作流
- **📱 移动适配**: 基于Antd Mobile，完美支持移动端操作

### 🚀 技术亮点
- **零配置启动**: 提供自动化环境配置脚本
- **安全第一**: 完整的API密钥管理和安全检查
- **云原生**: 支持多种云平台一键部署
- **响应式设计**: 自适应桌面端和移动端
- **完整文档**: 从开发到部署的完整指南

## 🏗️ 技术架构

### 前端技术栈
- **React 18** - 现代化用户界面
- **Vite** - 极速构建工具
- **Antd Mobile** - 移动端UI组件库
- **Axios** - HTTP客户端

### 后端技术栈
- **Python FastAPI** - 高性能API框架
- **通义千问VL** - 阿里云多模态AI模型
- **Python-multipart** - 文件上传处理
- **Uvicorn** - ASGI服务器

### 部署架构
- **云函数**: 无服务器后端部署
- **静态托管**: CDN加速的前端部署
- **API网关**: 统一的API访问入口

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- 通义千问API密钥
- flomo账号和webhook地址

### 一键环境配置

**Linux/Mac**:
```bash
git clone https://github.com/你的用户名/NoteFlow.git
cd NoteFlow
chmod +x setup.sh
./setup.sh
```

**Windows**:
```cmd
git clone https://github.com/你的用户名/NoteFlow.git
cd NoteFlow
setup.bat
```

### 手动配置

1. **克隆项目**
```bash
git clone https://github.com/你的用户名/NoteFlow.git
cd NoteFlow
```

2. **配置环境变量**
```bash
cp env.example .env
# 编辑 .env 文件，填入你的API密钥
```

3. **安装后端依赖**
```bash
cd backend
pip install -r requirements.txt
```

4. **安装前端依赖**
```bash
cd frontend
npm install
```

5. **启动开发服务**
```bash
# 启动后端（在backend目录）
python main.py

# 启动前端（在frontend目录）
npm run dev
```

6. **访问应用**
打开浏览器访问 `http://localhost:5173`

## ⚙️ 配置说明

### 环境变量配置
```bash
# 通义千问API配置
DASHSCOPE_API_KEY=sk-your-dashscope-api-key

# flomo webhook配置  
FLMO_WEBHOOK_URL=https://flomoapp.com/iwh/your-webhook-id/your-webhook-token

# 开发环境API地址
VITE_API_BASE_URL=http://localhost:8000
```

### 获取API密钥

**通义千问API密钥**:
1. 访问 [阿里云控制台](https://dashscope.console.aliyun.com/)
2. 开通DashScope服务
3. 创建API密钥
4. 详细步骤参考 [docs/security_guide.md](docs/security_guide.md)

**flomo webhook**:
1. 在flomo中创建webhook
2. 复制webhook URL
3. 详细配置参考 [docs/deployment_guide.md](docs/deployment_guide.md)

## 📦 部署指南

### 云平台部署
支持一键部署到主流云平台，成本低至 **60元/年**：

| 平台 | 成本 | 推荐度 | 文档链接 |
|------|------|--------|----------|
| 腾讯云 | 60元/年 | ⭐⭐⭐⭐⭐ | [部署指南](docs/step_by_step_guide.md) |
| 华为云 | 68元/年 | ⭐⭐⭐⭐ | [部署指南](docs/deployment_guide.md) |
| 阿里云 | 84元/年 | ⭐⭐⭐⭐ | [部署指南](docs/cost_analysis.md) |

### Docker部署
```bash
# 构建并运行
docker-compose up --build

# 后台运行
docker-compose up -d
```

### 本地部署
详细步骤参考 [docs/step_by_step_guide.md](docs/step_by_step_guide.md)

## 🔒 安全须知

⚠️ **重要提醒**：
- 从不在代码中硬编码API密钥
- 使用环境变量管理敏感信息
- 定期轮换API密钥
- 启用访问日志监控

**安全检查**：
```bash
# 运行安全检查脚本
python security_check.py
```

详细安全配置参考 [docs/security_guide.md](docs/security_guide.md)

## 📚 文档目录

### 🚀 部署运维
- [快速部署指南](docs/step_by_step_guide.md) - 完整部署流程
- [部署配置手册](docs/deployment_guide.md) - 详细配置说明
- [成本分析报告](docs/cost_analysis.md) - 各平台成本对比

### 🔒 安全配置
- [安全配置指南](docs/security_guide.md) - API密钥管理
- [安全配置流程](docs/security_setup_process.md) - 完整安全流程

### 🛠️ 开发维护
- [软件需求规格](docs/software_requirements.md) - 功能需求
- [系统架构设计](docs/system_architecture.md) - 技术架构
- [开发修复记录](docs/development_fix_record.md) - 问题修复记录

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源协议发布。

## 🙏 致谢

- [通义千问](https://tongyi.aliyun.com/) - 提供强大的多模态AI能力
- [flomo](https://flomoapp.com/) - 优秀的笔记管理工具
- [Antd Mobile](https://mobile.ant.design/) - 精美的移动端组件库
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的Python API框架

## 📞 联系我们

- 提交 [Issue](../../issues) 报告问题
- 发起 [Discussion](../../discussions) 参与讨论
- 查看 [Wiki](../../wiki) 获取更多信息

---

<div align="center">
如果这个项目对你有帮助，请给一个 ⭐ Star 支持一下！
</div> 