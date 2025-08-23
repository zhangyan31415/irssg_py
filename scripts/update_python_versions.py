#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动更新Python版本配置脚本

使用方法:
    python scripts/update_python_versions.py "3.9 3.10 3.11"

这个脚本会自动更新:
1. .github/workflows/build.yml
2. pyproject.toml

确保所有文件使用相同的Python版本配置。
"""

import sys
import re
import os
from pathlib import Path

def update_workflow_yml(python_versions):
    """更新GitHub Actions工作流中的Python版本配置"""
    workflow_path = Path(".github/workflows/build.yml")
    
    if not workflow_path.exists():
        print(f"❌ 文件不存在: {workflow_path}")
        return False
    
    # 生成cibuildwheel格式: "cp39-* cp310-* cp311-*"
    version_numbers = [v.replace(".", "") for v in python_versions]
    cibw_versions = [f"cp{v}-*" for v in version_numbers]
    cibw_format = " ".join(cibw_versions)
    
    # 读取文件
    content = workflow_path.read_text()
    
    # 替换CIBW_BUILD配置
    pattern = r'CIBW_BUILD: \${{ needs\.setup\.outputs\.python-versions-cibw }}'
    replacement = f'CIBW_BUILD: "{cibw_format}"'
    
    new_content = re.sub(pattern, replacement, content)
    
    if new_content != content:
        workflow_path.write_text(new_content)
        print(f"✅ 已更新 {workflow_path}: {cibw_format}")
        return True
    else:
        print(f"ℹ️  {workflow_path} 无需更新")
        return True

def update_pyproject_toml(python_versions):
    """更新pyproject.toml中的构建版本"""
    pyproject_path = Path("pyproject.toml")
    
    if not pyproject_path.exists():
        print(f"❌ 文件不存在: {pyproject_path}")
        return False
    
    # 生成pyproject格式: ["cp39-*", "cp310-*", "cp311-*"]
    version_numbers = [v.replace(".", "") for v in python_versions]
    cibw_versions = [f'"cp{v}-*"' for v in version_numbers]
    pyproject_format = f'[{", ".join(cibw_versions)}]'
    
    # 读取文件
    content = pyproject_path.read_text()
    
    # 替换build配置
    pattern = r'build = \[.*?\]'
    replacement = f'build = {pyproject_format}'
    
    new_content = re.sub(pattern, replacement, content)
    
    if new_content != content:
        pyproject_path.write_text(new_content)
        print(f"✅ 已更新 {pyproject_path}: {pyproject_format}")
        return True
    else:
        print(f"ℹ️  {pyproject_path} 无需更新")
        return True

def main():
    if len(sys.argv) != 2:
        print("❌ 用法: python scripts/update_python_versions.py \"3.9 3.10 3.11\"")
        sys.exit(1)
    
    python_versions_str = sys.argv[1]
    python_versions = python_versions_str.split()
    
    print(f"🎯 更新Python版本配置: {python_versions}")
    
    # 验证版本格式
    for version in python_versions:
        if not re.match(r'^\d+\.\d+$', version):
            print(f"❌ 无效的Python版本格式: {version}")
            sys.exit(1)
    
    # 更新文件
    success = True
    success &= update_workflow_yml(python_versions)
    success &= update_pyproject_toml(python_versions)
    
    if success:
        print("✅ 所有文件更新完成！")
        print("\n📋 下一步:")
        print("1. 检查 .github/workflows/build.yml 中的配置")
        print("2. 提交更改: git add . && git commit -m 'Update Python versions'")
    else:
        print("❌ 更新过程中出现错误")
        sys.exit(1)

if __name__ == "__main__":
    main() 