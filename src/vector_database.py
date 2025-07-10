import numpy as np
import chromadb
import faiss
import json
from typing import List, Dict, Tuple, Optional, Union
import logging
from abc import ABC, abstractmethod
try:
    from .graphcodebert_embedder import CodeNode, CodeRelation
except ImportError:
    from graphcodebert_embedder import CodeNode, CodeRelation
from pathlib import Path

class VectorDatabaseInterface(ABC):
    """向量数据库接口"""
    
    @abstractmethod
    def add_embeddings(self, nodes: List[CodeNode]) -> None:
        """添加向量嵌入"""
        pass
    
    @abstractmethod
    def search(self, query_embedding: np.ndarray, top_k: int = 10) -> List[Tuple[str, float]]:
        """向量搜索"""
        pass
    
    @abstractmethod
    def get_node(self, node_id: str) -> Optional[CodeNode]:
        """获取节点"""
        pass
    
    @abstractmethod
    def update_node(self, node: CodeNode) -> None:
        """更新节点"""
        pass
    
    @abstractmethod
    def delete_node(self, node_id: str) -> None:
        """删除节点"""
        pass
    
    @abstractmethod
    def get_all_nodes(self) -> List[CodeNode]:
        """获取所有节点"""
        pass

class ChromaDBInterface(VectorDatabaseInterface):
    """ChromaDB向量数据库接口"""
    
    def __init__(self, collection_name: str = "code_embeddings", persist_directory: str = "./chroma_db"):
        """
        初始化ChromaDB
        
        Args:
            collection_name: 集合名称
            persist_directory: 持久化目录
        """
        self.logger = logging.getLogger(__name__)
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        
        # 初始化ChromaDB客户端
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # 创建或获取集合
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        self.logger.info(f"ChromaDB集合 '{collection_name}' 已初始化")
    
    def add_embeddings(self, nodes: List[CodeNode]) -> None:
        """
        添加向量嵌入
        
        Args:
            nodes: 代码节点列表
        """
        ids = []
        embeddings = []
        metadatas = []
        documents = []
        
        for node in nodes:
            if node.embedding is not None:
                ids.append(node.id)
                embeddings.append(node.embedding.tolist())
                metadatas.append({
                    "file_path": node.file_path,
                    "node_type": node.node_type,
                    "name": node.name,
                    "start_line": node.start_line,
                    "end_line": node.end_line
                })
                documents.append(node.code)
        
        if ids:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents
            )
            self.logger.info(f"已添加 {len(ids)} 个向量嵌入到ChromaDB")
    
    def search(self, query_embedding: np.ndarray, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        向量搜索
        
        Args:
            query_embedding: 查询向量
            top_k: 返回前k个结果
            
        Returns:
            搜索结果列表 (节点ID, 相似度)
        """
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k
        )
        
        search_results = []
        if results['ids'] and results['distances']:
            for node_id, distance in zip(results['ids'][0], results['distances'][0]):
                # ChromaDB返回的是距离，需要转换为相似度
                similarity = 1.0 - distance
                search_results.append((node_id, similarity))
        
        return search_results
    
    def get_node(self, node_id: str) -> Optional[CodeNode]:
        """
        获取节点
        
        Args:
            node_id: 节点ID
            
        Returns:
            代码节点或None
        """
        results = self.collection.get(ids=[node_id])
        
        if results['ids']:
            metadata = results['metadatas'][0]
            document = results['documents'][0]
            embedding = np.array(results['embeddings'][0]) if results['embeddings'] else None
            
            return CodeNode(
                id=node_id,
                file_path=metadata['file_path'],
                node_type=metadata['node_type'],
                name=metadata['name'],
                code=document,
                start_line=metadata['start_line'],
                end_line=metadata['end_line'],
                embedding=embedding
            )
        
        return None
    
    def update_node(self, node: CodeNode) -> None:
        """
        更新节点
        
        Args:
            node: 代码节点
        """
        if node.embedding is not None:
            self.collection.update(
                ids=[node.id],
                embeddings=[node.embedding.tolist()],
                metadatas=[{
                    "file_path": node.file_path,
                    "node_type": node.node_type,
                    "name": node.name,
                    "start_line": node.start_line,
                    "end_line": node.end_line
                }],
                documents=[node.code]
            )
            self.logger.debug(f"已更新节点: {node.id}")
    
    def delete_node(self, node_id: str) -> None:
        """
        删除节点
        
        Args:
            node_id: 节点ID
        """
        self.collection.delete(ids=[node_id])
        self.logger.debug(f"已删除节点: {node_id}")
    
    def get_all_nodes(self) -> List[CodeNode]:
        """
        获取所有节点
        
        Returns:
            所有代码节点列表
        """
        results = self.collection.get()
        nodes = []
        
        for i, node_id in enumerate(results['ids']):
            metadata = results['metadatas'][i]
            document = results['documents'][i]
            embedding = np.array(results['embeddings'][i]) if results['embeddings'] else None
            
            node = CodeNode(
                id=node_id,
                file_path=metadata['file_path'],
                node_type=metadata['node_type'],
                name=metadata['name'],
                code=document,
                start_line=metadata['start_line'],
                end_line=metadata['end_line'],
                embedding=embedding
            )
            nodes.append(node)
        
        return nodes

class FAISSInterface(VectorDatabaseInterface):
    """FAISS向量数据库接口"""
    
    def __init__(self, dimension: int = 768, index_file: str = "faiss_index.bin", metadata_file: str = "metadata.json"):
        """
        初始化FAISS
        
        Args:
            dimension: 向量维度
            index_file: 索引文件路径
            metadata_file: 元数据文件路径
        """
        self.logger = logging.getLogger(__name__)
        self.dimension = dimension
        self.index_file = index_file
        self.metadata_file = metadata_file
        
        # 初始化FAISS索引
        self.index = faiss.IndexFlatIP(dimension)  # 使用内积作为相似度度量
        
        # 存储节点元数据
        self.node_metadata: Dict[int, CodeNode] = {}
        self.id_to_index: Dict[str, int] = {}
        self.index_to_id: Dict[int, str] = {}
        self.next_index = 0
        
        # 加载已有的索引和元数据
        self._load_index()
        
        self.logger.info(f"FAISS索引已初始化，维度: {dimension}")
    
    def add_embeddings(self, nodes: List[CodeNode]) -> None:
        """
        添加向量嵌入
        
        Args:
            nodes: 代码节点列表
        """
        embeddings = []
        valid_nodes = []
        
        for node in nodes:
            if node.embedding is not None:
                embeddings.append(node.embedding)
                valid_nodes.append(node)
        
        if embeddings:
            # 添加向量到索引
            embeddings_array = np.array(embeddings).astype('float32')
            self.index.add(embeddings_array)
            
            # 更新元数据
            for node in valid_nodes:
                index = self.next_index
                self.node_metadata[index] = node
                self.id_to_index[node.id] = index
                self.index_to_id[index] = node.id
                self.next_index += 1
            
            self.logger.info(f"已添加 {len(embeddings)} 个向量嵌入到FAISS")
            
            # 保存索引
            self._save_index()
    
    def search(self, query_embedding: np.ndarray, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        向量搜索
        
        Args:
            query_embedding: 查询向量
            top_k: 返回前k个结果
            
        Returns:
            搜索结果列表 (节点ID, 相似度)
        """
        query_vector = query_embedding.reshape(1, -1).astype('float32')
        scores, indices = self.index.search(query_vector, top_k)
        
        search_results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx in self.index_to_id:
                node_id = self.index_to_id[idx]
                search_results.append((node_id, float(score)))
        
        return search_results
    
    def get_node(self, node_id: str) -> Optional[CodeNode]:
        """
        获取节点
        
        Args:
            node_id: 节点ID
            
        Returns:
            代码节点或None
        """
        if node_id in self.id_to_index:
            index = self.id_to_index[node_id]
            return self.node_metadata.get(index)
        return None
    
    def update_node(self, node: CodeNode) -> None:
        """
        更新节点
        
        Args:
            node: 代码节点
        """
        if node.id in self.id_to_index:
            index = self.id_to_index[node.id]
            self.node_metadata[index] = node
            self.logger.debug(f"已更新节点: {node.id}")
            
            # 保存索引
            self._save_index()
    
    def delete_node(self, node_id: str) -> None:
        """
        删除节点
        
        Args:
            node_id: 节点ID
        """
        if node_id in self.id_to_index:
            index = self.id_to_index[node_id]
            del self.node_metadata[index]
            del self.id_to_index[node_id]
            del self.index_to_id[index]
            self.logger.debug(f"已删除节点: {node_id}")
            
            # 注意：FAISS不支持直接删除向量，这里只是删除元数据
            # 实际应用中可能需要重建索引
    
    def get_all_nodes(self) -> List[CodeNode]:
        """
        获取所有节点
        
        Returns:
            所有代码节点列表
        """
        return list(self.node_metadata.values())
    
    def _save_index(self) -> None:
        """保存索引和元数据"""
        # 保存FAISS索引
        faiss.write_index(self.index, self.index_file)
        
        # 保存元数据
        metadata = {
            'node_metadata': {
                str(k): {
                    'id': v.id,
                    'file_path': v.file_path,
                    'node_type': v.node_type,
                    'name': v.name,
                    'code': v.code,
                    'start_line': v.start_line,
                    'end_line': v.end_line,
                    'embedding': v.embedding.tolist() if v.embedding is not None else None
                } for k, v in self.node_metadata.items()
            },
            'id_to_index': self.id_to_index,
            'index_to_id': {str(k): v for k, v in self.index_to_id.items()},
            'next_index': self.next_index
        }
        
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    def _load_index(self) -> None:
        """加载索引和元数据"""
        try:
            # 加载FAISS索引
            if Path(self.index_file).exists():
                self.index = faiss.read_index(self.index_file)
            
            # 加载元数据
            if Path(self.metadata_file).exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                # 恢复节点元数据
                for k, v in metadata['node_metadata'].items():
                    index = int(k)
                    embedding = np.array(v['embedding']) if v['embedding'] else None
                    node = CodeNode(
                        id=v['id'],
                        file_path=v['file_path'],
                        node_type=v['node_type'],
                        name=v['name'],
                        code=v['code'],
                        start_line=v['start_line'],
                        end_line=v['end_line'],
                        embedding=embedding
                    )
                    self.node_metadata[index] = node
                
                self.id_to_index = metadata['id_to_index']
                self.index_to_id = {int(k): v for k, v in metadata['index_to_id'].items()}
                self.next_index = metadata['next_index']
                
                self.logger.info("已加载FAISS索引和元数据")
        
        except Exception as e:
            self.logger.warning(f"加载索引失败: {str(e)}")

class VectorDatabaseFactory:
    """向量数据库工厂"""
    
    @staticmethod
    def create_database(db_type: str = "chromadb", **kwargs) -> VectorDatabaseInterface:
        """
        创建向量数据库实例
        
        Args:
            db_type: 数据库类型 ("chromadb" 或 "faiss")
            **kwargs: 其他参数
            
        Returns:
            向量数据库接口实例
        """
        if db_type.lower() == "chromadb":
            return ChromaDBInterface(**kwargs)
        elif db_type.lower() == "faiss":
            return FAISSInterface(**kwargs)
        else:
            raise ValueError(f"不支持的数据库类型: {db_type}") 