#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫功能测试脚本
"""

import os
import sys
from sehuatang_crawler import SehuatangCrawler

def test_crawler():
    """测试爬虫功能"""
    print("🧪 开始测试爬虫功能...")
    
    # 设置代理（如果需要）
    proxy = os.getenv('HTTP_PROXY') or os.getenv('HTTPS_PROXY')
    if proxy:
        print(f"🔗 使用代理: {proxy}")
    
    # 创建爬虫实例
    crawler = SehuatangCrawler(proxy=proxy)
    
    # 测试获取论坛列表
    print("\n📋 测试获取论坛列表...")
    try:
        posts = crawler.get_forum_list("2")  # 亚洲无码区
        if posts:
            print(f"✅ 成功获取 {len(posts)} 个帖子")
            print(f"📝 第一个帖子: {posts[0]['title']}")
        else:
            print("❌ 未获取到帖子")
            return False
    except Exception as e:
        print(f"❌ 获取论坛列表失败: {e}")
        return False
    
    # 测试爬取单个帖子
    print("\n📄 测试爬取单个帖子...")
    if posts:
        try:
            post_data = crawler.get_post_content(posts[0]['url'])
            if post_data:
                print(f"✅ 成功爬取帖子: {post_data['title']}")
                print(f"🔢 番号: {post_data.get('code', '未识别')}")
                print(f"📏 大小: {post_data.get('size', '未知')}")
                print(f"🔗 磁力链接数量: {len(post_data.get('magnets', []))}")
                print(f"🖼️ 图片数量: {len(post_data.get('images', []))}")
                print(f"🔓 是否有码: {'无码' if post_data.get('is_uncensored') else '有码'}")
            else:
                print("❌ 爬取帖子失败")
                return False
        except Exception as e:
            print(f"❌ 爬取单个帖子失败: {e}")
            return False
    
    print("\n🎉 爬虫功能测试完成！")
    return True

def test_parser_integration():
    """测试与解析器的集成"""
    print("\n🔗 测试与解析器集成...")
    
    try:
        from sehuatang_parser import parse_sehuatang_post
        
        # 模拟HTML内容
        test_html = """
        <html>
        <head><title>STARS-123 测试影片</title></head>
        <body>
        <td class="t_f">
        STARS-123 测试影片 3.5GB 无码流出
        magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678
        </td>
        </body>
        </html>
        """
        
        result = parse_sehuatang_post(test_html, "http://test.com")
        if result:
            print(f"✅ 解析成功: {result.get('title', '未知')}")
            print(f"🔢 番号: {result.get('code', '未识别')}")
        else:
            print("❌ 解析失败")
            return False
            
    except Exception as e:
        print(f"❌ 解析器集成测试失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Sehuatang 爬虫系统测试")
    print("=" * 50)
    
    # 测试爬虫功能
    if test_crawler():
        print("✅ 爬虫功能测试通过")
    else:
        print("❌ 爬虫功能测试失败")
        sys.exit(1)
    
    # 测试解析器集成
    if test_parser_integration():
        print("✅ 解析器集成测试通过")
    else:
        print("❌ 解析器集成测试失败")
        sys.exit(1)
    
    print("\n🎊 所有测试通过！系统可以正常使用。")
