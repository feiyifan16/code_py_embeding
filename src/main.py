#!/usr/bin/env python3
"""
GraphCodeBERT Java代码嵌入系统
主程序文件
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Dict, Optional
from tqdm import tqdm

try:
    from .graphcodebert_embedder import GraphCodeBERTEmbedder, CodeNode, CodeRelation
    from .java_parser import JavaCodeParser
    from .vector_database import VectorDatabaseFactory, VectorDatabaseInterface
except ImportError:
    from graphcodebert_embedder import GraphCodeBERTEmbedder, CodeNode, CodeRelation
    from java_parser import JavaCodeParser
    from vector_database import VectorDatabaseFactory, VectorDatabaseInterface

class JavaCodeEmbeddingSystem:
    """Java代码嵌入系统"""
    
    def __init__(self, model_name: str = "microsoft/graphcodebert-base", 
                 vector_db_type: str = "chromadb", 
                 vector_db_config: Optional[Dict] = None):
        """
        初始化系统
        
        Args:
            model_name: GraphCodeBERT模型名称
            vector_db_type: 向量数据库类型
            vector_db_config: 向量数据库配置
        """
        self.logger = logging.getLogger(__name__)
        
        # 初始化组件
        self.embedder = GraphCodeBERTEmbedder(model_name)
        self.parser = JavaCodeParser()
        
        # 初始化向量数据库
        if vector_db_config is None:
            vector_db_config = {}
        self.vector_db = VectorDatabaseFactory.create_database(vector_db_type, **vector_db_config)
        
        self.logger.info("Java代码嵌入系统初始化完成")
    
    def process_java_repository(self, repo_path: str, output_file: Optional[str] = None) -> None:
        """
        处理Java代码仓库
        
        Args:
            repo_path: 仓库路径
            output_file: 输出文件路径
        """
        self.logger.info(f"开始处理Java代码仓库: {repo_path}")
        
        # 解析Java代码
        parsed_classes = self.parser.parse_java_directory(repo_path)
        self.logger.info(f"解析完成，共找到 {len(parsed_classes)} 个Java类")
        
        # 转换为代码节点
        code_nodes = self.parser.convert_to_code_nodes()
        self.logger.info(f"转换完成，共生成 {len(code_nodes)} 个代码节点")
        
        # 生成嵌入向量
        self.logger.info("开始生成代码嵌入向量...")
        for node in tqdm(code_nodes, desc="生成嵌入向量"):
            self.embedder.add_code_node(node)
        
        # 添加调用关系
        code_relations = self.parser.convert_to_code_relations()
        self.logger.info(f"添加 {len(code_relations)} 个代码关系")
        for relation in code_relations:
            self.embedder.add_code_relation(relation)
        
        # 存储到向量数据库
        self.logger.info("将嵌入向量存储到向量数据库...")
        self.vector_db.add_embeddings(code_nodes)
        
        # 导出结果
        if output_file:
            self.embedder.export_embeddings(output_file)
            self.logger.info(f"结果已导出到: {output_file}")
        
        # 打印统计信息
        stats = self.embedder.get_statistics()
        self.logger.info(f"处理完成 - 统计信息: {stats}")
    
    def search_similar_code(self, query_code: str, top_k: int = 10) -> List[Dict]:
        """
        搜索相似代码
        
        Args:
            query_code: 查询代码
            top_k: 返回前k个结果
            
        Returns:
            相似代码列表
        """
        # 使用嵌入器搜索
        embedder_results = self.embedder.get_similar_nodes(query_code, top_k)
        
        # 使用向量数据库搜索
        query_embedding = self.embedder.encode_code(query_code)
        db_results = self.vector_db.search(query_embedding, top_k)
        
        # 合并结果
        results = []
        for node_id, similarity in embedder_results:
            node = self.embedder.code_nodes.get(node_id)
            if node:
                results.append({
                    'node_id': node_id,
                    'similarity': similarity,
                    'node_type': node.node_type,
                    'name': node.name,
                    'file_path': node.file_path,
                    'code': node.code
                })
        
        return results
    
    def analyze_dependencies(self, node_id: str) -> Dict:
        """
        分析依赖关系
        
        Args:
            node_id: 节点ID
            
        Returns:
            依赖分析结果
        """
        return self.embedder.analyze_impact(node_id)
    
    def find_call_path(self, source_id: str, target_id: str) -> List[str]:
        """
        查找调用路径
        
        Args:
            source_id: 源节点ID
            target_id: 目标节点ID
            
        Returns:
            调用路径
        """
        return self.embedder.get_call_path(source_id, target_id)
    
    def get_node_info(self, node_id: str) -> Optional[Dict]:
        """
        获取节点信息
        
        Args:
            node_id: 节点ID
            
        Returns:
            节点信息
        """
        node = self.embedder.code_nodes.get(node_id)
        if node:
            return {
                'id': node.id,
                'file_path': node.file_path,
                'node_type': node.node_type,
                'name': node.name,
                'code': node.code,
                'start_line': node.start_line,
                'end_line': node.end_line
            }
        return None
    
    def interactive_query(self):
        """
        交互式查询模式
        """
        print("🚀 Java代码嵌入系统 - 交互式查询模式")
        print("可用命令:")
        print("  search <代码片段>  - 搜索相似代码")
        print("  deps <节点ID>      - 分析依赖关系") 
        print("  path <源ID> <目标ID> - 查找调用路径")
        print("  info <节点ID>      - 获取节点信息")
        print("  stats              - 显示统计信息")
        print("  quit               - 退出")
        print()
        
        while True:
            try:
                user_input = input(">>> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == "quit":
                    break
                
                parts = user_input.split()
                command = parts[0].lower()
                
                if command == "search" and len(parts) > 1:
                    query_code = " ".join(parts[1:])
                    results = self.search_similar_code(query_code)
                    
                    print(f"\n找到 {len(results)} 个相似代码:")
                    for i, result in enumerate(results[:5]):  # 显示前5个结果
                        print(f"{i+1}. {result['name']} ({result['node_type']})")
                        print(f"   文件: {result['file_path']}")
                        print(f"   相似度: {result['similarity']:.3f}")
                        print(f"   代码: {result['code'][:100]}...")
                        print()
                
                elif command == "deps" and len(parts) == 2:
                    node_id = parts[1]
                    deps = self.analyze_dependencies(node_id)
                    
                    print(f"\n节点 {node_id} 的依赖分析:")
                    print(f"上游依赖: {deps['upstream']}")
                    print(f"下游依赖: {deps['downstream']}")
                    print(f"直接调用者: {deps['direct_callers']}")
                    print(f"直接被调用者: {deps['direct_callees']}")
                    print()
                
                elif command == "path" and len(parts) == 3:
                    source_id, target_id = parts[1], parts[2]
                    path = self.find_call_path(source_id, target_id)
                    
                    if path:
                        print(f"\n调用路径 {source_id} -> {target_id}:")
                        print(" -> ".join(path))
                    else:
                        print(f"\n未找到从 {source_id} 到 {target_id} 的调用路径")
                    print()
                
                elif command == "info" and len(parts) == 2:
                    node_id = parts[1]
                    info = self.get_node_info(node_id)
                    
                    if info:
                        print(f"\n节点信息:")
                        print(f"ID: {info['id']}")
                        print(f"类型: {info['node_type']}")
                        print(f"名称: {info['name']}")
                        print(f"文件: {info['file_path']}")
                        print(f"行号: {info['start_line']}-{info['end_line']}")
                        print(f"代码: {info['code']}")
                    else:
                        print(f"\n未找到节点: {node_id}")
                    print()
                
                elif command == "stats":
                    stats = self.embedder.get_statistics()
                    print(f"\n系统统计信息:")
                    for key, value in stats.items():
                        print(f"{key}: {value}")
                    print()
                
                else:
                    print("无效命令，请重新输入")
                    
            except KeyboardInterrupt:
                print("\n程序已中断")
                break
            except Exception as e:
                print(f"错误: {str(e)}")

def setup_logging(level: str = "INFO"):
    """
    设置日志
    
    Args:
        level: 日志级别
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('code_embedding.log', encoding='utf-8')
        ]
    )

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="GraphCodeBERT Java代码嵌入系统")
    parser.add_argument("--repo-path", required=True, help="Java代码仓库路径")
    parser.add_argument("--model-name", default="microsoft/graphcodebert-base", 
                       help="GraphCodeBERT模型名称")
    parser.add_argument("--vector-db", choices=["chromadb", "faiss"], default="chromadb",
                       help="向量数据库类型")
    parser.add_argument("--output-file", help="输出文件路径")
    parser.add_argument("--interactive", action="store_true", help="启用交互式查询模式")
    parser.add_argument("--log-level", default="INFO", help="日志级别")
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.log_level)
    
    # 创建系统实例
    system = JavaCodeEmbeddingSystem(
        model_name=args.model_name,
        vector_db_type=args.vector_db
    )
    
    # 处理代码仓库
    system.process_java_repository(args.repo_path, args.output_file)
    
    # 交互式查询
    if args.interactive:
        system.interactive_query()

if __name__ == "__main__":
    main() 