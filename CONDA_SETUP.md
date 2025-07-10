# 使用Conda构建和运行GraphCodeBERT Java代码嵌入系统

## 📋 前提条件

1. **安装Conda**
   - 下载并安装 [Anaconda](https://www.anaconda.com/download) 或 [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
   - 确保conda命令可用

2. **系统要求**
   - Python 3.8+
   - 8GB+ RAM (推荐)
   - 20GB+ 硬盘空间

## 🚀 快速开始

### 方法1: 使用自动安装脚本

#### Linux/macOS:
```bash
# 给脚本执行权限
chmod +x install_conda.sh

# 运行安装脚本
./install_conda.sh
```

#### Windows:
```batch
# 运行安装脚本
install_conda.bat
```

### 方法2: 手动安装

#### 步骤1: 创建conda环境
```bash
# 创建环境
conda env create -f environment.yml

# 激活环境
conda activate graphcodebert-java-embedder
```

#### 步骤2: 验证安装
```bash
# 运行测试
python run_project.py --mode test
```

#### 步骤3: 创建示例项目
```bash
# 创建示例Java项目
python run_project.py --mode sample
```

#### 步骤4: 运行示例
```bash
# 运行完整示例
python run_project.py --mode example
```

## 📊 使用GPU加速 (可选)

如果您有NVIDIA GPU，可以使用GPU加速：

### 步骤1: 修改environment.yml
```yaml
# 删除这一行
- cpuonly

# 添加这一行
- cudatoolkit=11.8  # 或其他兼容版本
```

### 步骤2: 重新创建环境
```bash
conda env remove -n graphcodebert-java-embedder
conda env create -f environment.yml
```

## 🎯 运行项目

### 1. 分析Java代码仓库

```bash
# 激活环境
conda activate graphcodebert-java-embedder

# 分析Java代码仓库
python run_project.py --mode main --repo-path /path/to/your/java/repo
```

### 2. 启用交互式模式

```bash
# 启动交互式模式
python run_project.py --mode main --repo-path /path/to/your/java/repo --interactive
```

### 3. 自定义配置

```bash
# 使用FAISS向量数据库
python run_project.py --mode main --repo-path /path/to/your/java/repo --vector-db faiss

# 使用不同的模型
python run_project.py --mode main --repo-path /path/to/your/java/repo --model-name microsoft/graphcodebert-large

# 保存结果到文件
python run_project.py --mode main --repo-path /path/to/your/java/repo --output-file results.json
```

## 📝 项目结构说明

```
项目目录/
├── environment.yml          # Conda环境配置
├── run_project.py           # 项目启动脚本
├── install_conda.sh         # Linux/macOS安装脚本
├── install_conda.bat        # Windows安装脚本
├── config.yaml              # 系统配置文件
├── src/                     # 源代码
│   ├── graphcodebert_embedder.py
│   ├── java_parser.py
│   ├── vector_database.py
│   └── main.py
├── example_usage.py         # 使用示例
└── test_system.py           # 测试脚本
```

## 🔧 常见问题与解决方案

### Q1: 创建环境时下载速度慢

**解决方案**: 使用国内镜像源
```bash
# 添加清华大学镜像
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
```

### Q2: 模型下载失败

**解决方案**: 
1. 检查网络连接
2. 配置代理（如果需要）
3. 使用HuggingFace镜像

```bash
# 设置HuggingFace镜像
export HF_ENDPOINT=https://hf-mirror.com
```

### Q3: 内存不足

**解决方案**:
1. 减少批处理大小
2. 使用更小的模型
3. 增加虚拟内存

```bash
# 使用更小的批处理大小
python run_project.py --mode main --repo-path /path/to/repo --batch-size 4
```

### Q4: Java解析错误

**解决方案**:
1. 确保Java代码语法正确
2. 检查Java版本兼容性
3. 忽略测试文件

```yaml
# 在config.yaml中配置忽略模式
parser:
  ignore_patterns:
    - "*Test.java"
    - "*Tests.java"
```

## 🎛️ 高级配置

### 自定义配置文件

编辑 `config.yaml` 文件来自定义系统行为：

```yaml
# 模型配置
model:
  name: "microsoft/graphcodebert-base"
  batch_size: 8
  max_length: 512

# 向量数据库配置
vector_database:
  type: "chromadb"
  chromadb:
    collection_name: "my_code_embeddings"
    persist_directory: "./my_chroma_db"

# 分析配置
analysis:
  similarity_threshold: 0.7
  max_dependency_depth: 3
  include_test_code: false
```

### 性能优化

1. **使用GPU加速**
2. **增加批处理大小**
3. **使用SSD存储**
4. **配置充足的内存**

## 📚 更多信息

- [项目README](README.md) - 详细的项目文档
- [配置文件说明](config.yaml) - 所有配置选项
- [使用示例](example_usage.py) - 代码示例
- [测试脚本](test_system.py) - 系统测试

## 📞 获取帮助

如果遇到问题，请：

1. 查看错误日志
2. 检查系统配置
3. 运行测试脚本
4. 查阅文档

```bash
# 查看详细帮助
python run_project.py --help

# 运行诊断
python run_project.py --mode test

# 查看日志
tail -f code_embedding.log
```

---

**注意**: 首次运行时，系统会自动下载GraphCodeBERT预训练模型，可能需要几分钟时间。 