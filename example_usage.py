#!/usr/bin/env python3
"""
GraphCodeBERT Java代码嵌入系统使用示例
"""

import os
import sys
import logging
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import JavaCodeEmbeddingSystem

def create_sample_java_code():
    """创建示例Java代码用于测试"""
    sample_dir = Path("sample_java_code")
    sample_dir.mkdir(exist_ok=True)
    
    # 创建示例Java类
    java_files = {
        "User.java": """
package com.example.model;

public class User {
    private String name;
    private String email;
    private int age;
    
    public User(String name, String email, int age) {
        this.name = name;
        this.email = email;
        this.age = age;
    }
    
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public String getEmail() {
        return email;
    }
    
    public void setEmail(String email) {
        this.email = email;
    }
    
    public int getAge() {
        return age;
    }
    
    public void setAge(int age) {
        this.age = age;
    }
    
    public boolean isAdult() {
        return age >= 18;
    }
    
    @Override
    public String toString() {
        return "User{name='" + name + "', email='" + email + "', age=" + age + "}";
    }
}
""",
        "UserService.java": """
package com.example.service;

import com.example.model.User;
import java.util.List;
import java.util.ArrayList;

public class UserService {
    private List<User> users;
    
    public UserService() {
        this.users = new ArrayList<>();
    }
    
    public void addUser(User user) {
        users.add(user);
    }
    
    public void removeUser(User user) {
        users.remove(user);
    }
    
    public List<User> getAllUsers() {
        return new ArrayList<>(users);
    }
    
    public List<User> getAdultUsers() {
        List<User> adults = new ArrayList<>();
        for (User user : users) {
            if (user.isAdult()) {
                adults.add(user);
            }
        }
        return adults;
    }
    
    public User findUserByEmail(String email) {
        for (User user : users) {
            if (user.getEmail().equals(email)) {
                return user;
            }
        }
        return null;
    }
    
    public void updateUser(User oldUser, User newUser) {
        int index = users.indexOf(oldUser);
        if (index != -1) {
            users.set(index, newUser);
        }
    }
}
""",
        "UserController.java": """
package com.example.controller;

import com.example.model.User;
import com.example.service.UserService;

public class UserController {
    private UserService userService;
    
    public UserController(UserService userService) {
        this.userService = userService;
    }
    
    public void createUser(String name, String email, int age) {
        User user = new User(name, email, age);
        userService.addUser(user);
    }
    
    public void deleteUser(String email) {
        User user = userService.findUserByEmail(email);
        if (user != null) {
            userService.removeUser(user);
        }
    }
    
    public void updateUserAge(String email, int newAge) {
        User user = userService.findUserByEmail(email);
        if (user != null) {
            User updatedUser = new User(user.getName(), user.getEmail(), newAge);
            userService.updateUser(user, updatedUser);
        }
    }
    
    public void printAllUsers() {
        for (User user : userService.getAllUsers()) {
            System.out.println(user.toString());
        }
    }
    
    public void printAdultUsers() {
        for (User user : userService.getAdultUsers()) {
            System.out.println(user.toString());
        }
    }
}
"""
    }
    
    # 写入Java文件
    for filename, content in java_files.items():
        file_path = sample_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print(f"已创建示例Java代码到 {sample_dir}")
    return str(sample_dir)

def example_basic_usage():
    """基本使用示例"""
    print("=" * 50)
    print("📋 基本使用示例")
    print("=" * 50)
    
    # 创建示例代码
    sample_dir = create_sample_java_code()
    
    # 初始化系统
    system = JavaCodeEmbeddingSystem(
        model_name="microsoft/graphcodebert-base",
        vector_db_type="chromadb"
    )
    
    # 处理Java仓库
    system.process_java_repository(sample_dir, "embeddings_output.json")
    
    print("\n✅ 基本处理完成")

def example_code_search():
    """代码搜索示例"""
    print("\n" + "=" * 50)
    print("🔍 代码搜索示例")
    print("=" * 50)
    
    # 创建示例代码
    sample_dir = create_sample_java_code()
    
    # 初始化系统
    system = JavaCodeEmbeddingSystem(
        model_name="microsoft/graphcodebert-base",
        vector_db_type="chromadb"
    )
    
    # 处理Java仓库
    system.process_java_repository(sample_dir)
    
    # 搜索相似代码
    query_codes = [
        "public String getName()",
        "public void addUser(User user)",
        "for (User user : users)"
    ]
    
    for query in query_codes:
        print(f"\n🔍 搜索查询: {query}")
        results = system.search_similar_code(query, top_k=3)
        
        if results:
            print(f"找到 {len(results)} 个相似代码:")
            for i, result in enumerate(results):
                print(f"  {i+1}. {result['name']} ({result['node_type']})")
                print(f"     文件: {result['file_path']}")
                print(f"     相似度: {result['similarity']:.3f}")
        else:
            print("未找到相似代码")

def example_dependency_analysis():
    """依赖分析示例"""
    print("\n" + "=" * 50)
    print("📊 依赖分析示例")
    print("=" * 50)
    
    # 创建示例代码
    sample_dir = create_sample_java_code()
    
    # 初始化系统
    system = JavaCodeEmbeddingSystem(
        model_name="microsoft/graphcodebert-base",
        vector_db_type="chromadb"
    )
    
    # 处理Java仓库
    system.process_java_repository(sample_dir)
    
    # 分析依赖关系
    node_ids = [
        "com.example.model.User",
        "com.example.service.UserService",
        "com.example.controller.UserController"
    ]
    
    for node_id in node_ids:
        print(f"\n📊 分析节点: {node_id}")
        deps = system.analyze_dependencies(node_id)
        
        print(f"  上游依赖: {deps['upstream']}")
        print(f"  下游依赖: {deps['downstream']}")
        print(f"  直接调用者: {deps['direct_callers']}")
        print(f"  直接被调用者: {deps['direct_callees']}")

def example_interactive_mode():
    """交互式模式示例"""
    print("\n" + "=" * 50)
    print("🎯 交互式模式示例")
    print("=" * 50)
    
    # 创建示例代码
    sample_dir = create_sample_java_code()
    
    # 初始化系统
    system = JavaCodeEmbeddingSystem(
        model_name="microsoft/graphcodebert-base",
        vector_db_type="chromadb"
    )
    
    # 处理Java仓库
    system.process_java_repository(sample_dir)
    
    print("\n启动交互式查询模式...")
    print("提示：可以尝试以下命令:")
    print("  stats")
    print("  search getName")
    print("  info com.example.model.User")
    print("  quit")
    
    # 启动交互式模式
    system.interactive_query()

def main():
    """主函数"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 GraphCodeBERT Java代码嵌入系统 - 使用示例")
    print("=" * 50)
    
    try:
        # 运行示例
        example_basic_usage()
        example_code_search()
        example_dependency_analysis()
        
        # 询问是否启动交互式模式
        response = input("\n是否启动交互式模式? (y/n): ").strip().lower()
        if response == 'y':
            example_interactive_mode()
        
    except KeyboardInterrupt:
        print("\n程序已中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 