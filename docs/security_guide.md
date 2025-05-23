# API密钥安全配置指南

本文档记录了NoteFlow项目API密钥管理的完整流程，确保敏感信息不会泄露到版本控制系统。

## 🚨 安全问题识别

在准备上传GitHub之前，我们发现了以下安全问题：

### 发现的泄露
1. **通义千问API密钥**：在 `handwriting_recognizer.py` 中硬编码
2. **flomo webhook URL**：在同一文件中硬编码
3. **文档示例**：部分文档包含真实密钥示例

### 风险评估
- 🔴 **高风险**：API密钥泄露可能导致账户滥用
- 🔴 **高风险**：webhook URL泄露可能导致笔记被恶意推送
- 🟡 **中风险**：可能产生意外的API调用费用

## 🛡️ 解决方案实施

### 第一步：代码重构
**目标**：移除所有硬编码的敏感信息

**修改文件**：`NoteFlow/backend/handwriting_recognizer.py`
```python
# 修改前（不安全）
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "sk-[真实密钥被移除]")
FLMO_WEBHOOK_URL = "https://flomoapp.com/iwh/[真实webhook被移除]"

# 修改后（安全）
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
FLMO_WEBHOOK_URL = os.getenv("FLMO_WEBHOOK_URL")

# 添加验证
if not DASHSCOPE_API_KEY:
    raise ValueError("DASHSCOPE_API_KEY environment variable is required")
if not FLMO_WEBHOOK_URL:
    raise ValueError("FLMO_WEBHOOK_URL environment variable is required")
```

### 第二步：环境变量管理
**创建的文件**：
1. `env.example` - 环境变量模板（安全，可提交）
2. `.gitignore` - Git忽略规则（防止意外提交）

**env.example 内容**：
```bash
# 通义千问API配置
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# flomo webhook配置
FLMO_WEBHOOK_URL=https://flomoapp.com/iwh/xxxxxxxx/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 开发环境API地址
VITE_API_BASE_URL=http://localhost:8000
```

### 第三步：自动化设置
**创建的脚本**：
- `setup.sh` - Linux/Mac自动设置
- `setup.bat` - Windows自动设置

**功能**：
- 自动复制环境变量模板
- 引导用户配置API密钥
- 提供安全提醒

### 第四步：文档更新
**更新的文档**：
- `README.md` - 添加安全配置指南
- `docs/` - 更新部署文档中的示例

## 🔒 Git安全配置

### .gitignore 规则
```gitignore
# 环境变量文件 - 重要：不要提交真实的API密钥
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# API密钥相关文件
**/config/secrets.*
**/keys/
*secret*
*key*
```

### 提交前检查清单
- [ ] 代码中无硬编码API密钥
- [ ] `.env` 文件已添加到 `.gitignore`
- [ ] 文档中使用示例密钥（不是真实密钥）
- [ ] Git历史中无敏感信息泄露
- [ ] 环境变量模板文件完整

## 🚀 开发者使用流程

### 新开发者设置
1. **克隆仓库**：
   ```bash
   git clone https://github.com/your-username/NoteFlow.git
   cd NoteFlow
   ```

2. **环境设置**：
   ```bash
   # 自动设置（推荐）
   ./setup.sh  # Linux/Mac
   setup.bat   # Windows
   
   # 手动设置
   cp env.example .env
   # 编辑 .env 文件填入真实密钥
   ```

3. **验证配置**：
   ```bash
   cd backend
   python -c "import handwriting_recognizer; print('✅ 配置正确')"
   ```

### 密钥获取指南
#### 通义千问API密钥
1. 访问 [DashScope控制台](https://dashscope.console.aliyun.com/)
2. 登录/注册阿里云账号
3. 开通DashScope服务
4. 创建API Key（格式：sk-xxxxxxxx）

#### flomo webhook
1. 打开flomo应用
2. 设置 → API & webhook
3. 创建新webhook
4. 复制完整URL

## 🌩️ 生产环境安全

### 云部署最佳实践
1. **使用云服务商密钥管理**：
   - 腾讯云：SCF环境变量
   - 阿里云：函数计算环境变量
   - 华为云：FunctionGraph环境变量

2. **密钥轮换**：
   - 定期更换API密钥
   - 监控密钥使用情况
   - 设置用量告警

3. **访问控制**：
   - 最小权限原则
   - IP白名单（如支持）
   - 请求频率限制

### 监控和审计
```bash
# 检查环境变量是否正确设置
echo $DASHSCOPE_API_KEY | head -c 10
echo $FLMO_WEBHOOK_URL | grep -o "flomoapp.com"

# 验证API连通性
curl -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
     "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
```

## 🔧 故障排除

### 常见错误
1. **"DASHSCOPE_API_KEY environment variable is required"**
   - 检查 `.env` 文件是否存在
   - 确认密钥格式正确（sk-开头）
   - 验证文件权限

2. **"FLMO_WEBHOOK_URL environment variable is required"**
   - 检查webhook URL完整性
   - 确认flomo服务正常
   - 测试网络连通性

3. **权限被拒绝**
   - 检查API密钥是否有效
   - 确认服务已开通
   - 检查账户余额

### 调试命令
```bash
# 检查环境变量
env | grep -E "(DASHSCOPE|FLMO)"

# 测试API连通性
python -c "
import os
print('DASHSCOPE_API_KEY:', 'sk-' + '*' * 20 if os.getenv('DASHSCOPE_API_KEY') else 'Not set')
print('FLMO_WEBHOOK_URL:', 'Set' if os.getenv('FLMO_WEBHOOK_URL') else 'Not set')
"
```

## 📋 安全检查表

### 上传前必检项目
- [ ] 搜索并移除所有硬编码密钥
- [ ] 确认 `.env` 在 `.gitignore` 中
- [ ] 测试环境变量设置脚本
- [ ] 检查文档中的示例密钥
- [ ] 验证新开发者设置流程

### 定期检查项目
- [ ] 审查代码提交中的敏感信息
- [ ] 更新依赖库版本
- [ ] 检查API密钥有效性
- [ ] 监控API使用量和费用
- [ ] 测试密钥轮换流程

## 🚨 应急响应

### 如果密钥泄露
1. **立即行动**：
   - 禁用泄露的API密钥
   - 生成新的API密钥
   - 更新所有部署环境

2. **清理历史**：
   ```bash
   # 如果已提交到Git，需要清理历史
   git filter-branch --force --index-filter \
   'git rm --cached --ignore-unmatch backend/handwriting_recognizer.py' \
   --prune-empty --tag-name-filter cat -- --all
   ```

3. **监控异常**：
   - 检查API调用日志
   - 监控账户使用情况
   - 观察异常访问模式

## 📚 相关资源

- [GitHub安全最佳实践](https://docs.github.com/en/code-security)
- [阿里云DashScope安全指南](https://help.aliyun.com/zh/dashscope/)
- [flomo API文档](https://flomoapp.com/mine/api)

---

**安全无小事，预防胜于治疗！** 🛡️ 