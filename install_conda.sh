#!/bin/bash

# GraphCodeBERT Java代码嵌入系统 - Conda环境安装脚本

echo "🚀 GraphCodeBERT Java代码嵌入系统 - Conda环境安装"
echo "=================================================="

# 检查conda是否已安装
if ! command -v conda &> /dev/null; then
    echo "❌ 错误: conda未安装"
    echo "请先安装Anaconda或Miniconda:"
    echo "https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

echo "✅ 检测到conda已安装"

# 检查environment.yml文件是否存在
if [ ! -f "environment.yml" ]; then
    echo "❌ 错误: environment.yml文件不存在"
    exit 1
fi

# 创建conda环境
ENV_NAME="graphcodebert-java-embedder"
echo "🔧 创建conda环境: $ENV_NAME"

# 检查环境是否已存在
if conda env list | grep -q "^$ENV_NAME "; then
    echo "⚠️  环境 $ENV_NAME 已存在，正在更新..."
    conda env update -f environment.yml
else
    echo "📦 创建新环境..."
    conda env create -f environment.yml
fi

if [ $? -eq 0 ]; then
    echo "✅ Conda环境创建/更新成功"
    echo ""
    echo "🎯 激活环境并运行项目:"
    echo "conda activate $ENV_NAME"
    echo "python run_project.py --mode sample  # 创建示例项目"
    echo "python run_project.py --mode test    # 运行测试"
    echo "python run_project.py --mode example # 运行示例"
    echo ""
    echo "🔧 或者直接运行主程序:"
    echo "python run_project.py --mode main --repo-path /path/to/java/repo"
    echo ""
    echo "📚 查看帮助:"
    echo "python run_project.py --help"
else
    echo "❌ 环境创建失败"
    exit 1
fi 