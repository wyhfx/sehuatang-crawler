#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Docker 环境测试脚本
"""

import os
import sys
import subprocess
import time

def test_docker_installation():
    """测试Docker安装"""
    print("🔍 测试Docker安装...")
    
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Docker版本: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError:
        print("❌ Docker未安装或无法访问")
        return False
    except FileNotFoundError:
        print("❌ Docker命令未找到")
        return False

def test_docker_compose():
    """测试Docker Compose"""
    print("🔍 测试Docker Compose...")
    
    try:
        result = subprocess.run(['docker-compose', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Docker Compose版本: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError:
        print("❌ Docker Compose未安装或无法访问")
        return False
    except FileNotFoundError:
        print("❌ Docker Compose命令未找到")
        return False

def test_python_dependencies():
    """测试Python依赖"""
    print("🔍 测试Python依赖...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'sqlalchemy', 'requests', 
        'bs4', 'selenium', 'pydantic'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"⚠️ 缺少依赖包: {', '.join(missing_packages)}")
        return False
    
    return True

def test_selenium_setup():
    """测试Selenium设置"""
    print("🔍 测试Selenium设置...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # 检查Chrome环境变量
        chrome_bin = os.getenv('CHROME_BIN')
        chromedriver_path = os.getenv('CHROMEDRIVER_PATH')
        
        if chrome_bin:
            print(f"✅ Chrome路径: {chrome_bin}")
        else:
            print("⚠️ CHROME_BIN环境变量未设置")
        
        if chromedriver_path:
            print(f"✅ ChromeDriver路径: {chromedriver_path}")
        else:
            print("⚠️ CHROMEDRIVER_PATH环境变量未设置")
        
        print("✅ Selenium导入成功")
        return True
        
    except ImportError as e:
        print(f"❌ Selenium导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ Selenium设置失败: {e}")
        return False

def test_project_structure():
    """测试项目结构"""
    print("🔍 测试项目结构...")
    
    required_files = [
        'main.py',
        'requirements.txt',
        'Dockerfile',
        'docker-compose.yml',
        'sehuatang_crawler.py',
        'sehuatang_parser.py',
        'db.py'
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - 文件不存在")
            missing_files.append(file)
    
    if missing_files:
        print(f"⚠️ 缺少文件: {', '.join(missing_files)}")
        return False
    
    return True

def test_docker_build():
    """测试Docker构建"""
    print("🔍 测试Docker构建...")
    
    try:
        print("构建Docker镜像...")
        result = subprocess.run(['docker-compose', 'build'], 
                              capture_output=True, text=True, check=True)
        print("✅ Docker镜像构建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker构建失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def main():
    """主测试函数"""
    print("🚀 Sehuatang 爬虫系统 - Docker 环境测试")
    print("=" * 50)
    
    tests = [
        ("Docker安装", test_docker_installation),
        ("Docker Compose", test_docker_compose),
        ("项目结构", test_project_structure),
        ("Python依赖", test_python_dependencies),
        ("Selenium设置", test_selenium_setup),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！可以开始构建Docker镜像")
        print("\n🚀 下一步:")
        print("1. 运行: docker-compose build")
        print("2. 运行: docker-compose up -d")
        print("3. 访问: http://localhost:8000")
    else:
        print("⚠️ 部分测试失败，请检查环境配置")
        sys.exit(1)

if __name__ == "__main__":
    main()
