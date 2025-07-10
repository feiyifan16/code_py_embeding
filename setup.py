#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# 读取README文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取requirements文件
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="graphcodebert-java-embedder",
    version="1.0.0",
    author="AI Assistant",
    author_email="ai@example.com",
    description="基于GraphCodeBERT的Java代码嵌入和分析系统",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/code_py_embeding",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.910",
            "jupyter>=1.0",
            "notebook>=6.0",
        ],
        "gpu": [
            "torch>=1.10.0+cu111",
        ],
        "visualization": [
            "matplotlib>=3.5.0",
            "seaborn>=0.11.0",
            "plotly>=5.0.0",
            "graphviz>=0.20.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "java-code-embedder=src.main:main",
            "graphcodebert-embedder=src.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "src": ["*.py"],
    },
    zip_safe=False,
    keywords=[
        "code-embedding",
        "graphcodebert",
        "java-analysis",
        "code-search",
        "dependency-analysis",
        "transformers",
        "nlp",
        "machine-learning",
        "deep-learning",
        "code-intelligence",
    ],
    project_urls={
        "Bug Reports": "https://github.com/yourusername/code_py_embeding/issues",
        "Source": "https://github.com/yourusername/code_py_embeding",
        "Documentation": "https://github.com/yourusername/code_py_embeding/blob/main/README.md",
    },
) 