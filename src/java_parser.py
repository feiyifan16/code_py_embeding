import javalang
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
import logging
import re
from dataclasses import dataclass
try:
    from .graphcodebert_embedder import CodeNode, CodeRelation
except ImportError:
    from graphcodebert_embedder import CodeNode, CodeRelation

@dataclass
class JavaMethod:
    """Java方法信息"""
    name: str
    class_name: str
    parameters: List[str]
    return_type: str
    modifiers: Set[str]
    body: str
    start_line: int
    end_line: int
    
@dataclass
class JavaClass:
    """Java类信息"""
    name: str
    package: str
    methods: List[JavaMethod]
    fields: List[str]
    imports: List[str]
    extends: Optional[str]
    implements: List[str]
    start_line: int
    end_line: int

class JavaCodeParser:
    """Java代码解析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.parsed_files: Dict[str, JavaClass] = {}
        self.method_calls: List[Tuple[str, str]] = []  # (caller, callee)
        self.type_references: List[Tuple[str, str]] = []  # (referrer, referenced)
        
    def parse_java_file(self, file_path: str) -> Optional[JavaClass]:
        """
        解析Java文件
        
        Args:
            file_path: Java文件路径
            
        Returns:
            解析后的Java类信息
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析Java代码
            tree = javalang.parse.parse(content)
            
            # 提取类信息
            for path, node in tree.filter(javalang.tree.ClassDeclaration):
                java_class = self._extract_class_info(node, tree, content, file_path)
                if java_class:
                    self.parsed_files[file_path] = java_class
                    return java_class
            
            # 处理接口
            for path, node in tree.filter(javalang.tree.InterfaceDeclaration):
                java_class = self._extract_interface_info(node, tree, content, file_path)
                if java_class:
                    self.parsed_files[file_path] = java_class
                    return java_class
                    
        except Exception as e:
            self.logger.error(f"解析Java文件失败 {file_path}: {str(e)}")
            return None
    
    def parse_java_directory(self, directory_path: str) -> List[JavaClass]:
        """
        解析Java目录
        
        Args:
            directory_path: Java目录路径
            
        Returns:
            解析后的Java类列表
        """
        java_files = list(Path(directory_path).rglob("*.java"))
        parsed_classes = []
        
        for java_file in java_files:
            java_class = self.parse_java_file(str(java_file))
            if java_class:
                parsed_classes.append(java_class)
        
        # 分析调用关系
        self._analyze_method_calls()
        self._analyze_type_references()
        
        return parsed_classes
    
    def _extract_class_info(self, class_node: javalang.tree.ClassDeclaration, 
                           tree: javalang.tree.CompilationUnit, 
                           content: str, 
                           file_path: str) -> JavaClass:
        """
        提取类信息
        
        Args:
            class_node: 类节点
            tree: 语法树
            content: 文件内容
            file_path: 文件路径
            
        Returns:
            Java类信息
        """
        # 获取包名
        package = tree.package.name if tree.package else ""
        
        # 获取导入
        imports = []
        if tree.imports:
            for imp in tree.imports:
                imports.append(imp.path)
        
        # 获取方法
        methods = []
        for method in class_node.methods:
            java_method = self._extract_method_info(method, class_node.name, content)
            if java_method:
                methods.append(java_method)
        
        # 获取字段
        fields = []
        for field in class_node.fields:
            for declarator in field.declarators:
                fields.append(declarator.name)
        
        # 获取继承和实现
        extends = class_node.extends.name if class_node.extends else None
        implements = []
        if class_node.implements:
            for impl in class_node.implements:
                implements.append(impl.name)
        
        # 获取行号
        start_line = getattr(class_node, 'position', None)
        start_line = start_line.line if start_line else 1
        
        return JavaClass(
            name=class_node.name,
            package=package,
            methods=methods,
            fields=fields,
            imports=imports,
            extends=extends,
            implements=implements,
            start_line=start_line,
            end_line=start_line + content.count('\n')  # 简化处理
        )
    
    def _extract_interface_info(self, interface_node: javalang.tree.InterfaceDeclaration,
                              tree: javalang.tree.CompilationUnit,
                              content: str,
                              file_path: str) -> JavaClass:
        """
        提取接口信息
        
        Args:
            interface_node: 接口节点
            tree: 语法树
            content: 文件内容
            file_path: 文件路径
            
        Returns:
            Java类信息（接口作为特殊类处理）
        """
        # 获取包名
        package = tree.package.name if tree.package else ""
        
        # 获取导入
        imports = []
        if tree.imports:
            for imp in tree.imports:
                imports.append(imp.path)
        
        # 获取方法
        methods = []
        for method in interface_node.methods:
            java_method = self._extract_method_info(method, interface_node.name, content)
            if java_method:
                methods.append(java_method)
        
        # 获取继承的接口
        extends_list = []
        if interface_node.extends:
            for ext in interface_node.extends:
                extends_list.append(ext.name)
        
        # 获取行号
        start_line = getattr(interface_node, 'position', None)
        start_line = start_line.line if start_line else 1
        
        return JavaClass(
            name=interface_node.name,
            package=package,
            methods=methods,
            fields=[],
            imports=imports,
            extends=None,
            implements=extends_list,  # 接口继承其他接口
            start_line=start_line,
            end_line=start_line + content.count('\n')  # 简化处理
        )
    
    def _extract_method_info(self, method_node: javalang.tree.MethodDeclaration,
                           class_name: str,
                           content: str) -> JavaMethod:
        """
        提取方法信息
        
        Args:
            method_node: 方法节点
            class_name: 类名
            content: 文件内容
            
        Returns:
            Java方法信息
        """
        # 获取参数
        parameters = []
        if method_node.parameters:
            for param in method_node.parameters:
                param_type = param.type.name if hasattr(param.type, 'name') else str(param.type)
                parameters.append(f"{param_type} {param.name}")
        
        # 获取返回类型
        return_type = method_node.return_type.name if method_node.return_type else "void"
        
        # 获取修饰符
        modifiers = set(method_node.modifiers) if method_node.modifiers else set()
        
        # 获取方法体
        body = self._extract_method_body(method_node, content)
        
        # 获取行号
        start_line = getattr(method_node, 'position', None)
        start_line = start_line.line if start_line else 1
        
        return JavaMethod(
            name=method_node.name,
            class_name=class_name,
            parameters=parameters,
            return_type=return_type,
            modifiers=modifiers,
            body=body,
            start_line=start_line,
            end_line=start_line + body.count('\n')  # 简化处理
        )
    
    def _extract_method_body(self, method_node: javalang.tree.MethodDeclaration, 
                           content: str) -> str:
        """
        提取方法体
        
        Args:
            method_node: 方法节点
            content: 文件内容
            
        Returns:
            方法体字符串
        """
        if not method_node.body:
            return ""
        
        # 简化处理：返回方法签名
        params = []
        if method_node.parameters:
            for param in method_node.parameters:
                param_type = param.type.name if hasattr(param.type, 'name') else str(param.type)
                params.append(f"{param_type} {param.name}")
        
        return_type = method_node.return_type.name if method_node.return_type else "void"
        modifiers = " ".join(method_node.modifiers) if method_node.modifiers else ""
        
        signature = f"{modifiers} {return_type} {method_node.name}({', '.join(params)})"
        return signature
    
    def _analyze_method_calls(self):
        """
        分析方法调用关系
        """
        for file_path, java_class in self.parsed_files.items():
            for method in java_class.methods:
                # 简化处理：通过正则表达式查找方法调用
                self._find_method_calls_in_body(method.body, f"{java_class.name}.{method.name}")
    
    def _find_method_calls_in_body(self, method_body: str, caller_id: str):
        """
        在方法体中查找方法调用
        
        Args:
            method_body: 方法体
            caller_id: 调用者ID
        """
        # 简化的方法调用模式匹配
        # 匹配类似 "methodName()" 或 "object.methodName()" 的模式
        method_call_pattern = r'(\w+)\.(\w+)\s*\('
        matches = re.findall(method_call_pattern, method_body)
        
        for match in matches:
            object_name, method_name = match
            callee_id = f"{object_name}.{method_name}"
            self.method_calls.append((caller_id, callee_id))
    
    def _analyze_type_references(self):
        """
        分析类型引用关系
        """
        for file_path, java_class in self.parsed_files.items():
            class_id = java_class.name
            
            # 分析继承关系
            if java_class.extends:
                self.type_references.append((class_id, java_class.extends))
            
            # 分析实现关系
            for impl in java_class.implements:
                self.type_references.append((class_id, impl))
            
            # 分析导入关系
            for imp in java_class.imports:
                imported_class = imp.split('.')[-1]
                self.type_references.append((class_id, imported_class))
    
    def convert_to_code_nodes(self) -> List[CodeNode]:
        """
        转换为CodeNode列表
        
        Returns:
            CodeNode列表
        """
        code_nodes = []
        
        for file_path, java_class in self.parsed_files.items():
            # 创建类节点
            class_node = CodeNode(
                id=f"{java_class.package}.{java_class.name}",
                file_path=file_path,
                node_type="class",
                name=java_class.name,
                code=f"class {java_class.name}",
                start_line=java_class.start_line,
                end_line=java_class.end_line
            )
            code_nodes.append(class_node)
            
            # 创建方法节点
            for method in java_class.methods:
                method_node = CodeNode(
                    id=f"{java_class.package}.{java_class.name}.{method.name}",
                    file_path=file_path,
                    node_type="method",
                    name=method.name,
                    code=method.body,
                    start_line=method.start_line,
                    end_line=method.end_line
                )
                code_nodes.append(method_node)
        
        return code_nodes
    
    def convert_to_code_relations(self) -> List[CodeRelation]:
        """
        转换为CodeRelation列表
        
        Returns:
            CodeRelation列表
        """
        code_relations = []
        
        # 转换方法调用关系
        for caller, callee in self.method_calls:
            relation = CodeRelation(
                source_id=caller,
                target_id=callee,
                relation_type="call",
                confidence=0.8
            )
            code_relations.append(relation)
        
        # 转换类型引用关系
        for referrer, referenced in self.type_references:
            relation = CodeRelation(
                source_id=referrer,
                target_id=referenced,
                relation_type="reference",
                confidence=0.9
            )
            code_relations.append(relation)
        
        return code_relations 