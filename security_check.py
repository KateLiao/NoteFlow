#!/usr/bin/env python3
"""
NoteFlow项目安全检查脚本
用于检测代码中可能存在的敏感信息泄露
"""

import os
import re
import sys
from pathlib import Path

class SecurityChecker:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.issues = []
        
        # 敏感信息模式
        self.patterns = {
            'api_key': {
                'pattern': r'sk-[a-zA-Z0-9]{32,}',
                'description': '通义千问API密钥',
                'severity': 'HIGH'
            },
            'flomo_webhook': {
                'pattern': r'https://flomoapp\.com/iwh/[A-Za-z0-9]+/[a-f0-9]{32}',
                'description': 'flomo webhook完整URL',
                'severity': 'HIGH'
            },
            'hardcoded_secret': {
                'pattern': r'(password|secret|key)\s*=\s*["\'][^"\']{8,}["\']',
                'description': '硬编码的密码或密钥',
                'severity': 'MEDIUM'
            }
        }
        
        # 排除的文件和目录
        self.exclude_patterns = [
            '*.pyc', '__pycache__', '.git', 'node_modules',
            '.env', '.env.*', 'dist', 'build'
        ]
        
        # 文档中允许的示例
        self.allowed_examples = [
            'sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
            'sk-your-api-key',
            'sk-xxxxxxxx'
        ]

    def should_skip_file(self, file_path):
        """检查是否应该跳过此文件"""
        file_str = str(file_path)
        for pattern in self.exclude_patterns:
            if pattern.replace('*', '') in file_str:
                return True
        return False

    def is_allowed_example(self, match):
        """检查是否是允许的示例"""
        return match in self.allowed_examples

    def check_file(self, file_path):
        """检查单个文件"""
        if self.should_skip_file(file_path):
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            for pattern_name, pattern_info in self.patterns.items():
                matches = re.findall(pattern_info['pattern'], content, re.IGNORECASE)
                
                for match in matches:
                    # 跳过文档中的示例
                    if pattern_name == 'api_key' and self.is_allowed_example(match):
                        continue
                        
                    # 记录问题
                    self.issues.append({
                        'file': str(file_path.relative_to(self.project_root)),
                        'pattern': pattern_name,
                        'match': match,
                        'description': pattern_info['description'],
                        'severity': pattern_info['severity']
                    })
                    
        except Exception as e:
            print(f"警告：无法读取文件 {file_path}: {e}")

    def scan_directory(self):
        """扫描整个项目目录"""
        print("🔍 开始安全扫描...")
        
        # 扫描所有文件
        for file_path in self.project_root.rglob('*'):
            if file_path.is_file():
                self.check_file(file_path)
                
        return len(self.issues) == 0

    def generate_report(self):
        """生成安全报告"""
        print("\n" + "="*60)
        print("🛡️  NoteFlow 安全检查报告")
        print("="*60)
        
        if not self.issues:
            print("✅ 未发现安全问题！")
            print("项目可以安全地上传到GitHub。")
            return True
            
        # 按严重程度分组
        high_issues = [i for i in self.issues if i['severity'] == 'HIGH']
        medium_issues = [i for i in self.issues if i['severity'] == 'MEDIUM']
        
        if high_issues:
            print(f"🚨 发现 {len(high_issues)} 个高风险问题：")
            for issue in high_issues:
                print(f"   - {issue['file']}: {issue['description']}")
                print(f"     匹配内容: {issue['match'][:50]}...")
                print()
                
        if medium_issues:
            print(f"⚠️  发现 {len(medium_issues)} 个中风险问题：")
            for issue in medium_issues:
                print(f"   - {issue['file']}: {issue['description']}")
                print(f"     匹配内容: {issue['match'][:50]}...")
                print()
        
        print("🔧 建议的修复措施：")
        print("1. 将硬编码的API密钥移动到环境变量")
        print("2. 确保 .env 文件在 .gitignore 中")
        print("3. 使用 env.example 作为模板")
        print("4. 运行 ./setup.sh 重新配置环境")
        
        return False

    def check_gitignore(self):
        """检查.gitignore文件是否正确配置"""
        gitignore_path = self.project_root / '.gitignore'
        
        if not gitignore_path.exists():
            print("❌ 未找到 .gitignore 文件")
            return False
            
        try:
            with open(gitignore_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ 读取 .gitignore 文件失败: {e}")
            return False
            
        required_patterns = ['.env', 'secret', 'key']
        missing = []
        
        for pattern in required_patterns:
            if pattern not in content:
                missing.append(pattern)
                
        if missing:
            print(f"⚠️  .gitignore 缺少模式: {', '.join(missing)}")
            return False
            
        return True

    def check_env_files(self):
        """检查环境文件配置"""
        checks = []
        
        # 检查 .env 文件是否存在（不应该提交）
        env_path = self.project_root / '.env'
        if env_path.exists():
            checks.append("⚠️  发现 .env 文件，确保它在 .gitignore 中")
        else:
            checks.append("✅ 未发现 .env 文件")
            
        # 检查 env.example 是否存在
        example_path = self.project_root / 'env.example'
        if example_path.exists():
            checks.append("✅ 找到 env.example 模板文件")
        else:
            checks.append("❌ 未找到 env.example 模板文件")
            
        return checks

def main():
    """主函数"""
    current_dir = Path.cwd()
    
    # 检查是否在项目根目录
    if not (current_dir / 'backend').exists() or not (current_dir / 'frontend').exists():
        print("❌ 请在NoteFlow项目根目录下运行此脚本")
        return 1
        
    checker = SecurityChecker(current_dir)
    
    print("🔍 NoteFlow 安全检查工具")
    print("检查项目中是否存在敏感信息泄露...")
    print()
    
    # 执行各项检查
    print("📁 检查环境文件配置...")
    env_checks = checker.check_env_files()
    for check in env_checks:
        print(f"   {check}")
    print()
    
    print("📄 检查 .gitignore 配置...")
    gitignore_ok = checker.check_gitignore()
    if gitignore_ok:
        print("   ✅ .gitignore 配置正确")
    print()
    
    # 扫描代码
    scan_ok = checker.scan_directory()
    
    # 生成报告
    report_ok = checker.generate_report()
    
    # 总结
    print("\n" + "="*60)
    if scan_ok and report_ok and gitignore_ok:
        print("🎉 安全检查通过！项目可以安全上传到GitHub。")
        print("\n📋 上传前最后检查清单：")
        print("   ✅ 代码中无硬编码API密钥")
        print("   ✅ .gitignore 配置正确")
        print("   ✅ env.example 模板存在")
        print("   ✅ 安全扫描通过")
        return 0
    else:
        print("❌ 发现安全问题，请修复后再上传！")
        return 1

if __name__ == "__main__":
    exit(main()) 