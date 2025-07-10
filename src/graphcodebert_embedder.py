import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np
from typing import List, Dict, Tuple, Optional
import logging
from pathlib import Path
import json
from dataclasses import dataclass, asdict
from tqdm import tqdm
import networkx as nx

@dataclass
class CodeNode:
    """代码节点数据结构"""
    id: str
    file_path: str
    node_type: str  # class, method, field, etc.
    name: str
    code: str
    start_line: int
    end_line: int
    embedding: Optional[np.ndarray] = None
    
@dataclass
class CodeRelation:
    """代码关系数据结构"""
    source_id: str
    target_id: str
    relation_type: str  # call, reference, inherit, implement, etc.
    confidence: float

class GraphCodeBERTEmbedder:
    """基于GraphCodeBERT的代码嵌入器"""
    
    def __init__(self, model_name: str = "microsoft/graphcodebert-base"):
        """
        初始化GraphCodeBERT模型
        
        Args:
            model_name: 预训练模型名称
        """
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        
        # 加载tokenizer和model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        
        # 设置设备
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        self.model.eval()
        
        # 代码节点和关系存储
        self.code_nodes: Dict[str, CodeNode] = {}
        self.code_relations: List[CodeRelation] = []
        self.call_graph = nx.DiGraph()
        
        self.logger.info(f"GraphCodeBERT模型已加载到设备: {self.device}")
    
    def encode_code(self, code: str, max_length: int = 512) -> np.ndarray:
        """
        将代码编码为向量表示
        
        Args:
            code: 代码字符串
            max_length: 最大序列长度
            
        Returns:
            代码的向量表示
        """
        # 预处理代码
        code = self._preprocess_code(code)
        
        # 分词
        inputs = self.tokenizer(
            code,
            max_length=max_length,
            padding=True,
            truncation=True,
            return_tensors="pt"
        )
        
        # 移动到设备
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # 获取嵌入
        with torch.no_grad():
            outputs = self.model(**inputs)
            # 使用[CLS]标记的嵌入作为代码表示
            embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()
        
        return embedding.flatten()
    
    def encode_code_batch(self, codes: List[str], batch_size: int = 8) -> np.ndarray:
        """
        批量编码代码
        
        Args:
            codes: 代码字符串列表
            batch_size: 批次大小
            
        Returns:
            代码向量矩阵
        """
        embeddings = []
        
        for i in tqdm(range(0, len(codes), batch_size), desc="编码代码"):
            batch_codes = codes[i:i+batch_size]
            
            # 预处理代码
            processed_codes = [self._preprocess_code(code) for code in batch_codes]
            
            # 分词
            inputs = self.tokenizer(
                processed_codes,
                max_length=512,
                padding=True,
                truncation=True,
                return_tensors="pt"
            )
            
            # 移动到设备
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # 获取嵌入
            with torch.no_grad():
                outputs = self.model(**inputs)
                batch_embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
                embeddings.extend(batch_embeddings)
        
        return np.array(embeddings)
    
    def _preprocess_code(self, code: str) -> str:
        """
        预处理代码，添加特殊标记
        
        Args:
            code: 原始代码
            
        Returns:
            预处理后的代码
        """
        # 移除多余的空白和换行
        lines = code.strip().split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line:
                cleaned_lines.append(line)
        
        return ' '.join(cleaned_lines)
    
    def add_code_node(self, node: CodeNode) -> None:
        """
        添加代码节点
        
        Args:
            node: 代码节点
        """
        # 生成嵌入
        node.embedding = self.encode_code(node.code)
        
        # 存储节点
        self.code_nodes[node.id] = node
        
        # 添加到图中
        self.call_graph.add_node(node.id, **asdict(node))
        
        self.logger.debug(f"添加代码节点: {node.id}")
    
    def add_code_relation(self, relation: CodeRelation) -> None:
        """
        添加代码关系
        
        Args:
            relation: 代码关系
        """
        self.code_relations.append(relation)
        
        # 添加到图中
        self.call_graph.add_edge(
            relation.source_id,
            relation.target_id,
            relation_type=relation.relation_type,
            confidence=relation.confidence
        )
        
        self.logger.debug(f"添加代码关系: {relation.source_id} -> {relation.target_id}")
    
    def get_similar_nodes(self, query_code: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        获取与查询代码最相似的节点
        
        Args:
            query_code: 查询代码
            top_k: 返回前k个结果
            
        Returns:
            相似节点列表 (节点ID, 相似度)
        """
        query_embedding = self.encode_code(query_code)
        similarities = []
        
        for node_id, node in self.code_nodes.items():
            if node.embedding is not None:
                similarity = self._cosine_similarity(query_embedding, node.embedding)
                similarities.append((node_id, similarity))
        
        # 按相似度排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def get_upstream_dependencies(self, node_id: str, max_depth: int = 3) -> List[str]:
        """
        获取上游依赖
        
        Args:
            node_id: 节点ID
            max_depth: 最大深度
            
        Returns:
            上游依赖节点列表
        """
        if node_id not in self.call_graph:
            return []
        
        upstream = set()
        queue = [(node_id, 0)]
        visited = set()
        
        while queue:
            current, depth = queue.pop(0)
            if current in visited or depth >= max_depth:
                continue
            
            visited.add(current)
            
            # 获取所有指向当前节点的边
            predecessors = list(self.call_graph.predecessors(current))
            upstream.update(predecessors)
            
            # 添加到队列继续搜索
            for pred in predecessors:
                if pred not in visited:
                    queue.append((pred, depth + 1))
        
        return list(upstream)
    
    def get_downstream_dependencies(self, node_id: str, max_depth: int = 3) -> List[str]:
        """
        获取下游依赖
        
        Args:
            node_id: 节点ID
            max_depth: 最大深度
            
        Returns:
            下游依赖节点列表
        """
        if node_id not in self.call_graph:
            return []
        
        downstream = set()
        queue = [(node_id, 0)]
        visited = set()
        
        while queue:
            current, depth = queue.pop(0)
            if current in visited or depth >= max_depth:
                continue
            
            visited.add(current)
            
            # 获取所有从当前节点出发的边
            successors = list(self.call_graph.successors(current))
            downstream.update(successors)
            
            # 添加到队列继续搜索
            for succ in successors:
                if succ not in visited:
                    queue.append((succ, depth + 1))
        
        return list(downstream)
    
    def get_call_path(self, source_id: str, target_id: str) -> List[str]:
        """
        获取两个节点之间的调用路径
        
        Args:
            source_id: 源节点ID
            target_id: 目标节点ID
            
        Returns:
            调用路径节点列表
        """
        try:
            path = nx.shortest_path(self.call_graph, source_id, target_id)
            return path
        except nx.NetworkXNoPath:
            return []
    
    def analyze_impact(self, node_id: str) -> Dict[str, List[str]]:
        """
        分析节点的影响范围
        
        Args:
            node_id: 节点ID
            
        Returns:
            影响分析结果
        """
        return {
            'upstream': self.get_upstream_dependencies(node_id),
            'downstream': self.get_downstream_dependencies(node_id),
            'direct_callers': list(self.call_graph.predecessors(node_id)),
            'direct_callees': list(self.call_graph.successors(node_id))
        }
    
    def export_embeddings(self, output_path: str) -> None:
        """
        导出嵌入向量
        
        Args:
            output_path: 输出路径
        """
        data = {
            'nodes': {node_id: {
                'metadata': asdict(node),
                'embedding': node.embedding.tolist() if node.embedding is not None else None
            } for node_id, node in self.code_nodes.items()},
            'relations': [asdict(rel) for rel in self.code_relations]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"嵌入向量已导出到: {output_path}")
    
    def load_embeddings(self, input_path: str) -> None:
        """
        加载嵌入向量
        
        Args:
            input_path: 输入路径
        """
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 加载节点
        for node_id, node_data in data['nodes'].items():
            metadata = node_data['metadata']
            embedding = np.array(node_data['embedding']) if node_data['embedding'] else None
            
            node = CodeNode(**metadata)
            node.embedding = embedding
            self.code_nodes[node_id] = node
            
            # 添加到图中
            self.call_graph.add_node(node_id, **asdict(node))
        
        # 加载关系
        for rel_data in data['relations']:
            relation = CodeRelation(**rel_data)
            self.code_relations.append(relation)
            
            # 添加到图中
            self.call_graph.add_edge(
                relation.source_id,
                relation.target_id,
                relation_type=relation.relation_type,
                confidence=relation.confidence
            )
        
        self.logger.info(f"嵌入向量已从 {input_path} 加载")
    
    @staticmethod
    def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        计算余弦相似度
        
        Args:
            vec1: 向量1
            vec2: 向量2
            
        Returns:
            余弦相似度
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def get_statistics(self) -> Dict[str, int]:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        return {
            'total_nodes': len(self.code_nodes),
            'total_relations': len(self.code_relations),
            'total_edges': self.call_graph.number_of_edges(),
            'strongly_connected_components': nx.number_strongly_connected_components(self.call_graph),
            'weakly_connected_components': nx.number_weakly_connected_components(self.call_graph)
        } 