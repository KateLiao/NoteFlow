@echo off
chcp 65001 > nul
echo 🚀 NoteFlow 项目环境设置向导
echo =================================

REM 检查是否存在 .env 文件
if exist ".env" (
    echo ⚠️  发现已存在的 .env 文件
    set /p "choice=是否要重新创建？(y/N): "
    if /i not "%choice%"=="y" (
        echo 保持现有配置，设置完成！
        pause
        exit /b 0
    )
)

REM 复制模板文件
if exist "env.example" (
    copy "env.example" ".env" > nul
    echo ✅ 已创建 .env 文件
) else (
    echo ❌ 未找到 env.example 模板文件
    pause
    exit /b 1
)

echo.
echo 📝 请编辑 .env 文件配置以下信息：
echo 1. DASHSCOPE_API_KEY - 通义千问API密钥
echo    获取地址: https://dashscope.console.aliyun.com/
echo.
echo 2. FLMO_WEBHOOK_URL - flomo webhook地址
echo    获取方法: flomo → 设置 → API ^& webhook
echo.
echo 3. VITE_API_BASE_URL - 前端API地址（开发环境一般不需要改）
echo.

REM 询问是否立即编辑
set /p "edit_choice=是否现在打开 .env 文件进行编辑？(Y/n): "
if /i not "%edit_choice%"=="n" (
    REM 尝试用不同的编辑器打开
    where code > nul 2>&1
    if not errorlevel 1 (
        start code .env
    ) else (
        where notepad > nul 2>&1
        if not errorlevel 1 (
            start notepad .env
        ) else (
            echo 请手动编辑 .env 文件
        )
    )
)

echo.
echo 🔒 安全提醒：
echo - .env 文件已被 .gitignore，不会提交到 Git
echo - 请勿在代码中硬编码 API 密钥
echo - 生产环境请使用云服务商的密钥管理服务
echo.
echo ✨ 设置完成！现在可以启动项目了。
pause 