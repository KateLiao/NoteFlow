#!/bin/bash

echo "🚀 NoteFlow 项目环境设置向导"
echo "================================="

# 检查是否存在 .env 文件
if [ -f ".env" ]; then
    echo "⚠️  发现已存在的 .env 文件"
    read -p "是否要重新创建？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "保持现有配置，设置完成！"
        exit 0
    fi
fi

# 复制模板文件
if [ -f "env.example" ]; then
    cp env.example .env
    echo "✅ 已创建 .env 文件"
else
    echo "❌ 未找到 env.example 模板文件"
    exit 1
fi

echo ""
echo "📝 请编辑 .env 文件配置以下信息："
echo "1. DASHSCOPE_API_KEY - 通义千问API密钥"
echo "   获取地址: https://dashscope.console.aliyun.com/"
echo ""
echo "2. FLMO_WEBHOOK_URL - flomo webhook地址"
echo "   获取方法: flomo → 设置 → API & webhook"
echo ""
echo "3. VITE_API_BASE_URL - 前端API地址（开发环境一般不需要改）"
echo ""

# 询问是否立即编辑
read -p "是否现在打开 .env 文件进行编辑？(Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    # 尝试用不同的编辑器打开
    if command -v code &> /dev/null; then
        code .env
    elif command -v nano &> /dev/null; then
        nano .env
    elif command -v vim &> /dev/null; then
        vim .env
    else
        echo "请手动编辑 .env 文件"
    fi
fi

echo ""
echo "🔒 安全提醒："
echo "- .env 文件已被 .gitignore，不会提交到 Git"
echo "- 请勿在代码中硬编码 API 密钥"
echo "- 生产环境请使用云服务商的密钥管理服务"
echo ""
echo "✨ 设置完成！现在可以启动项目了。" 