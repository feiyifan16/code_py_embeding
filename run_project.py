#!/usr/bin/env python3
"""
GraphCodeBERT Java代码嵌入系统启动脚本
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

def setup_environment():
    """设置环境变量和路径"""
    # 设置环境变量
    os.environ['PYTHONPATH'] = str(PROJECT_ROOT)
    
    # 创建必要的目录
    directories = [
        PROJECT_ROOT / 'output',
        PROJECT_ROOT / 'logs',
        PROJECT_ROOT / 'chroma_db',
        PROJECT_ROOT / 'models'
    ]
    
    for directory in directories:
        directory.mkdir(exist_ok=True)
    
    print(f"✅ 环境设置完成，项目根目录: {PROJECT_ROOT}")

def run_example():
    """运行示例"""
    print("🚀 运行示例程序...")
    try:
        # 动态导入以避免路径问题
        from example_usage import main as example_main
        example_main()
    except Exception as e:
        print(f"❌ 运行示例失败: {e}")
        print("💡 请确保所有依赖已正确安装")

def run_tests():
    """运行测试"""
    print("🧪 运行系统测试...")
    try:
        from test_system import main as test_main
        test_main()
    except Exception as e:
        print(f"❌ 运行测试失败: {e}")
        print("💡 请确保所有依赖已正确安装")

def run_main_system(args):
    """运行主系统"""
    print("🎯 启动主系统...")
    try:
        # 动态导入主系统
        from src.main import main as main_system
        
        # 设置命令行参数
        original_argv = sys.argv
        sys.argv = ['main.py']
        
        if args.repo_path:
            sys.argv.extend(['--repo-path', args.repo_path])
        if args.output_file:
            sys.argv.extend(['--output-file', args.output_file])
        if args.interactive:
            sys.argv.append('--interactive')
        if args.vector_db:
            sys.argv.extend(['--vector-db', args.vector_db])
        if args.model_name:
            sys.argv.extend(['--model-name', args.model_name])
        if args.log_level:
            sys.argv.extend(['--log-level', args.log_level])
        
        # 运行主系统
        main_system()
        
        # 恢复原始参数
        sys.argv = original_argv
        
    except Exception as e:
        print(f"❌ 运行主系统失败: {e}")
        import traceback
        traceback.print_exc()

def create_sample_java_project():
    """创建示例Java项目"""
    print("📁 创建示例Java项目...")
    
    sample_dir = PROJECT_ROOT / 'sample_java_project'
    sample_dir.mkdir(exist_ok=True)
    
    # 创建包结构
    (sample_dir / 'src' / 'main' / 'java' / 'com' / 'example' / 'model').mkdir(parents=True, exist_ok=True)
    (sample_dir / 'src' / 'main' / 'java' / 'com' / 'example' / 'service').mkdir(parents=True, exist_ok=True)
    (sample_dir / 'src' / 'main' / 'java' / 'com' / 'example' / 'controller').mkdir(parents=True, exist_ok=True)
    
    # 创建Java文件
    java_files = {
        'src/main/java/com/example/model/User.java': '''
package com.example.model;

import java.util.Objects;

public class User {
    private Long id;
    private String name;
    private String email;
    private int age;
    
    public User() {}
    
    public User(String name, String email, int age) {
        this.name = name;
        this.email = email;
        this.age = age;
    }
    
    public Long getId() {
        return id;
    }
    
    public void setId(Long id) {
        this.id = id;
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
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        User user = (User) obj;
        return age == user.age && 
               Objects.equals(id, user.id) && 
               Objects.equals(name, user.name) && 
               Objects.equals(email, user.email);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(id, name, email, age);
    }
    
    @Override
    public String toString() {
        return "User{" +
                "id=" + id +
                ", name='" + name + '\\'' +
                ", email='" + email + '\\'' +
                ", age=" + age +
                '}';
    }
}
''',
        'src/main/java/com/example/service/UserService.java': '''
package com.example.service;

import com.example.model.User;
import java.util.*;

public class UserService {
    private List<User> users = new ArrayList<>();
    private Long nextId = 1L;
    
    public User createUser(String name, String email, int age) {
        User user = new User(name, email, age);
        user.setId(nextId++);
        users.add(user);
        return user;
    }
    
    public User findUserById(Long id) {
        return users.stream()
                   .filter(user -> user.getId().equals(id))
                   .findFirst()
                   .orElse(null);
    }
    
    public User findUserByEmail(String email) {
        return users.stream()
                   .filter(user -> user.getEmail().equals(email))
                   .findFirst()
                   .orElse(null);
    }
    
    public List<User> getAllUsers() {
        return new ArrayList<>(users);
    }
    
    public List<User> getAdultUsers() {
        return users.stream()
                   .filter(User::isAdult)
                   .collect(ArrayList::new, ArrayList::add, ArrayList::addAll);
    }
    
    public boolean updateUser(Long id, User updatedUser) {
        for (int i = 0; i < users.size(); i++) {
            if (users.get(i).getId().equals(id)) {
                updatedUser.setId(id);
                users.set(i, updatedUser);
                return true;
            }
        }
        return false;
    }
    
    public boolean deleteUser(Long id) {
        return users.removeIf(user -> user.getId().equals(id));
    }
    
    public long getUserCount() {
        return users.size();
    }
    
    public double getAverageAge() {
        return users.stream()
                   .mapToInt(User::getAge)
                   .average()
                   .orElse(0.0);
    }
}
''',
        'src/main/java/com/example/controller/UserController.java': '''
package com.example.controller;

import com.example.model.User;
import com.example.service.UserService;
import java.util.List;

public class UserController {
    private UserService userService;
    
    public UserController(UserService userService) {
        this.userService = userService;
    }
    
    public User createUser(String name, String email, int age) {
        if (name == null || name.trim().isEmpty()) {
            throw new IllegalArgumentException("Name cannot be null or empty");
        }
        if (email == null || email.trim().isEmpty()) {
            throw new IllegalArgumentException("Email cannot be null or empty");
        }
        if (age < 0) {
            throw new IllegalArgumentException("Age cannot be negative");
        }
        
        // 检查邮箱是否已存在
        User existingUser = userService.findUserByEmail(email);
        if (existingUser != null) {
            throw new IllegalArgumentException("Email already exists: " + email);
        }
        
        return userService.createUser(name, email, age);
    }
    
    public User getUserById(Long id) {
        if (id == null) {
            throw new IllegalArgumentException("ID cannot be null");
        }
        return userService.findUserById(id);
    }
    
    public User getUserByEmail(String email) {
        if (email == null || email.trim().isEmpty()) {
            throw new IllegalArgumentException("Email cannot be null or empty");
        }
        return userService.findUserByEmail(email);
    }
    
    public List<User> getAllUsers() {
        return userService.getAllUsers();
    }
    
    public List<User> getAdultUsers() {
        return userService.getAdultUsers();
    }
    
    public boolean updateUser(Long id, String name, String email, int age) {
        if (id == null) {
            throw new IllegalArgumentException("ID cannot be null");
        }
        
        User existingUser = userService.findUserById(id);
        if (existingUser == null) {
            return false;
        }
        
        User updatedUser = new User(name, email, age);
        return userService.updateUser(id, updatedUser);
    }
    
    public boolean deleteUser(Long id) {
        if (id == null) {
            throw new IllegalArgumentException("ID cannot be null");
        }
        return userService.deleteUser(id);
    }
    
    public void printUserStatistics() {
        System.out.println("=== User Statistics ===");
        System.out.println("Total users: " + userService.getUserCount());
        System.out.println("Adult users: " + userService.getAdultUsers().size());
        System.out.println("Average age: " + String.format("%.2f", userService.getAverageAge()));
    }
}
'''
    }
    
    # 写入文件
    for file_path, content in java_files.items():
        full_path = sample_dir / file_path
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
    
    print(f"✅ 示例Java项目已创建: {sample_dir}")
    return str(sample_dir)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="GraphCodeBERT Java代码嵌入系统启动器")
    parser.add_argument("--mode", choices=["test", "example", "main", "sample"], 
                       default="example", help="运行模式")
    parser.add_argument("--repo-path", help="Java代码仓库路径")
    parser.add_argument("--output-file", help="输出文件路径")
    parser.add_argument("--interactive", action="store_true", help="启用交互式模式")
    parser.add_argument("--vector-db", choices=["chromadb", "faiss"], 
                       default="chromadb", help="向量数据库类型")
    parser.add_argument("--model-name", default="microsoft/graphcodebert-base", 
                       help="GraphCodeBERT模型名称")
    parser.add_argument("--log-level", default="INFO", help="日志级别")
    
    args = parser.parse_args()
    
    # 设置日志
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 GraphCodeBERT Java代码嵌入系统启动器")
    print("=" * 50)
    
    # 设置环境
    setup_environment()
    
    try:
        if args.mode == "test":
            run_tests()
        elif args.mode == "example":
            run_example()
        elif args.mode == "sample":
            sample_path = create_sample_java_project()
            print(f"\n🎯 示例项目已创建，可以使用以下命令分析:")
            print(f"python run_project.py --mode main --repo-path {sample_path}")
        elif args.mode == "main":
            if not args.repo_path:
                print("❌ 主模式需要指定 --repo-path 参数")
                sample_path = create_sample_java_project()
                print(f"💡 已创建示例项目，使用路径: {sample_path}")
                args.repo_path = sample_path
            
            run_main_system(args)
        
    except KeyboardInterrupt:
        print("\n🛑 程序被用户中断")
    except Exception as e:
        print(f"❌ 运行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 