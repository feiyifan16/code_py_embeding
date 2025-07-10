# GraphCodeBERT Java代码嵌入系统

基于GraphCodeBERT的Java代码嵌入和分析系统，用于向量化Java代码仓库、识别调用关系和引用关系，支持代码检索和上下游依赖分析。

## ✨ 功能特点

- 🧠 **智能代码嵌入**: 基于GraphCodeBERT预训练模型生成高质量代码向量
- 🔍 **代码搜索**: 支持语义搜索，找到功能相似的代码片段
- 📊 **依赖分析**: 自动识别类、方法间的调用关系和引用关系
- 🎯 **上下游追踪**: 分析代码的上游依赖和下游影响
- 💾 **向量数据库**: 支持ChromaDB和FAISS两种向量数据库
- 🔄 **交互式查询**: 提供命令行交互式查询界面
- 📈 **可视化分析**: 生成调用图和依赖关系图

## 📦 安装要求

确保您的系统满足以下要求：

- Python 3.8+
- CUDA (可选，用于GPU加速)
- 8GB+ RAM (推荐)

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone <repository-url>
cd code_py_embeding
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行示例

```bash
python example_usage.py
```

## 💡 使用方法

### 基本使用

```python
from src.main import JavaCodeEmbeddingSystem

# 初始化系统
system = JavaCodeEmbeddingSystem(
    model_name="microsoft/graphcodebert-base",
    vector_db_type="chromadb"
)

# 处理Java代码仓库
system.process_java_repository("/path/to/java/repo", "output.json")
```

### 代码搜索

```python
# 搜索相似代码
results = system.search_similar_code("public String getName()", top_k=10)

for result in results:
    print(f"相似度: {result['similarity']:.3f}")
    print(f"文件: {result['file_path']}")
    print(f"代码: {result['code']}")
```

### 依赖分析

```python
# 分析依赖关系
deps = system.analyze_dependencies("com.example.UserService")

print(f"上游依赖: {deps['upstream']}")
print(f"下游依赖: {deps['downstream']}")
print(f"直接调用者: {deps['direct_callers']}")
print(f"直接被调用者: {deps['direct_callees']}")
```

### 调用路径分析

```python
# 查找调用路径
path = system.find_call_path("com.example.UserController", "com.example.User")
print(f"调用路径: {' -> '.join(path)}")
```

## 🔧 命令行使用

### 基本命令

```bash
# 处理Java代码仓库
python -m src.main --repo-path /path/to/java/repo --output-file embeddings.json

# 启用交互式模式
python -m src.main --repo-path /path/to/java/repo --interactive

# 使用FAISS向量数据库
python -m src.main --repo-path /path/to/java/repo --vector-db faiss
```

### 交互式命令

启动交互式模式后，可以使用以下命令：

- `search <代码片段>` - 搜索相似代码
- `deps <节点ID>` - 分析依赖关系
- `path <源ID> <目标ID>` - 查找调用路径
- `info <节点ID>` - 获取节点信息
- `stats` - 显示统计信息
- `quit` - 退出

## 🏗️ 架构设计

### 核心组件

1. **GraphCodeBERTEmbedder**: 负责代码向量化和图构建
2. **JavaCodeParser**: 解析Java代码结构和关系
3. **VectorDatabase**: 向量数据库抽象层
4. **JavaCodeEmbeddingSystem**: 系统主控制器

### 数据流程

```
Java代码 → 语法解析 → 代码节点 → 向量化 → 向量数据库
             ↓
        关系提取 → 调用图构建 → 依赖分析
```

## 📊 支持的分析类型

### 代码节点类型

- **类 (Class)**: Java类定义
- **方法 (Method)**: 类方法
- **字段 (Field)**: 类字段
- **接口 (Interface)**: Java接口

### 关系类型

- **调用关系 (Call)**: 方法调用
- **引用关系 (Reference)**: 类型引用
- **继承关系 (Inherit)**: 类继承
- **实现关系 (Implement)**: 接口实现

## 🎯 应用场景

### 代码搜索与重用

- 查找功能相似的代码片段
- 识别重复或相似的实现
- 代码重构建议

### 依赖分析

- 影响分析：修改某个类/方法的影响范围
- 依赖梳理：理解代码间的依赖关系
- 架构分析：识别核心组件和边界

### 代码维护

- 识别紧耦合的代码
- 分析代码的可维护性
- 重构影响评估

## 🔧 配置选项

### 向量数据库配置

#### ChromaDB

```python
vector_db_config = {
    "collection_name": "code_embeddings",
    "persist_directory": "./chroma_db"
}
```

#### FAISS

```python
vector_db_config = {
    "dimension": 768,
    "index_file": "faiss_index.bin",
    "metadata_file": "metadata.json"
}
```

### 模型配置

支持的GraphCodeBERT模型：
- `microsoft/graphcodebert-base`
- `microsoft/graphcodebert-large`

## 📈 性能优化

### 批量处理

```python
# 批量编码以提高效率
embeddings = embedder.encode_code_batch(codes, batch_size=16)
```

### GPU加速

```python
# 自动检测并使用GPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
```

### 内存优化

- 使用向量数据库存储大量嵌入
- 支持增量更新
- 延迟加载机制

## 🐛 常见问题

### Q: 如何处理大型代码仓库？

A: 系统支持批量处理和增量更新，可以分批处理大型仓库。建议设置合适的batch_size和使用向量数据库持久化。

### Q: 支持哪些Java版本？

A: 系统使用javalang解析器，支持Java 8-17的语法特性。

### Q: 如何提高搜索精度？

A: 可以通过以下方式提高精度：
- 使用更大的GraphCodeBERT模型
- 调整相似度阈值
- 优化查询代码的表达方式

## 📚 API文档

### GraphCodeBERTEmbedder

```python
class GraphCodeBERTEmbedder:
    def encode_code(self, code: str) -> np.ndarray
    def add_code_node(self, node: CodeNode) -> None
    def get_similar_nodes(self, query_code: str, top_k: int) -> List[Tuple[str, float]]
    def analyze_impact(self, node_id: str) -> Dict[str, List[str]]
```

### JavaCodeParser

```python
class JavaCodeParser:
    def parse_java_file(self, file_path: str) -> Optional[JavaClass]
    def parse_java_directory(self, directory_path: str) -> List[JavaClass]
    def convert_to_code_nodes(self) -> List[CodeNode]
    def convert_to_code_relations(self) -> List[CodeRelation]
```

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 仓库
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 📄 许可证

MIT License

## 🙏 致谢

- Microsoft GraphCodeBERT 团队
- Hugging Face Transformers
- ChromaDB 和 FAISS 团队

---

如有问题或建议，请提交Issue或联系维护者。
自学的python代码平台
