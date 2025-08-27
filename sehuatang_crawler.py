#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sehuatang 爬虫系统 (Selenium版本)
用于爬取 Sehuatang 论坛的帖子页面
"""

import logging
import time
import os
import re
import json
from typing import List, Dict, Optional
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

class SehuatangCrawler:
    def __init__(self, proxy: Optional[str] = None):
        self.driver = None
        self.progress_callback = None
        self.log_callback = None
        self.proxy = proxy
        self.logs = []  # 存储操作日志
        
        # 论坛主题配置
        self.themes = {
            "36": {"name": "亚洲无码", "url": "https://sehuatang.org/forum-36-1.html", "hot": "https://sehuatang.org/forum.php?mod=forumdisplay&fid=36&filter=heat&orderby=heats"},
            "37": {"name": "亚洲有码", "url": "https://sehuatang.org/forum-37-1.html", "hot": None},
            "2": {"name": "国产原创", "url": "https://sehuatang.org/forum-2-1.html", "hot": "https://sehuatang.org/forum.php?mod=forumdisplay&fid=2&filter=heat&orderby=heats"},
            "103": {"name": "高清中文字幕", "url": "https://sehuatang.org/forum-103-1.html", "hot": "https://sehuatang.org/forum.php?mod=forumdisplay&fid=103&filter=heat&orderby=heats"},
            "104": {"name": "素人原创", "url": "https://sehuatang.org/forum-104-1.html", "hot": None},
            "39": {"name": "动漫原创", "url": "https://sehuatang.org/forum-39-1.html", "hot": None},
            "152": {"name": "韩国主播", "url": "https://sehuatang.org/forum-152-1.html", "hot": "https://sehuatang.org/forum.php?mod=forumdisplay&fid=152&filter=heat&orderby=heats"}
        }
        
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def add_log(self, message: str, level: str = "INFO"):
        """添加日志"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.logs.append(log_entry)
        self.logger.info(message)
        
        # 调用日志回调函数
        if self.log_callback:
            try:
                self.log_callback(timestamp, level, message)
            except Exception as e:
                self.logger.error(f"日志回调执行失败: {e}")

    def get_logs(self):
        """获取所有日志"""
        return self.logs

    def set_progress_callback(self, callback):
        """设置进度回调函数"""
        self.progress_callback = callback

    def set_log_callback(self, callback):
        """设置日志回调函数"""
        self.log_callback = callback

    def setup_driver(self):
        """设置 Selenium WebDriver，支持代理"""
        options = webdriver.ChromeOptions()
        
        # 关键：指向系统 chromium
        chrome_bin = os.getenv("CHROME_BIN", "/usr/bin/chromium")
        if os.path.exists(chrome_bin):
            options.binary_location = chrome_bin
        
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/139.0.0.0 Safari/537.36")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # 添加代理支持
        if self.proxy:
            self.add_log(f"使用代理: {self.proxy}")
            options.add_argument(f'--proxy-server={self.proxy}')
        
        try:
            # 关键：指向系统 chromedriver
            chromedriver_path = os.getenv("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")
            if os.path.exists(chromedriver_path):
                service = Service(chromedriver_path)
                driver = webdriver.Chrome(service=service, options=options)
            else:
                # 如果没有指定路径，使用默认的
                driver = webdriver.Chrome(options=options)
            return driver
        except Exception as e:
            self.add_log(f"Chrome WebDriver 初始化失败: {str(e)}", "ERROR")
            raise

    def fetch_page(self, url: str, retries: int = 3) -> str:
        """使用 Selenium 抓取页面内容，包含重试机制和年龄确认处理"""
        for attempt in range(retries):
            try:
                self.add_log(f"尝试抓取 {url} (第 {attempt + 1}/{retries} 次)")
                self.driver.get(url)
                wait = WebDriverWait(self.driver, 10)
                
                # 检查是否是年龄验证页面
                current_url = self.driver.current_url
                page_title = self.driver.title
                
                if "SEHUATANG.ORG" in page_title and "满18岁" in self.driver.page_source:
                    self.add_log("检测到年龄验证页面，尝试点击进入按钮")
                    try:
                        # 尝试点击中文的进入按钮
                        enter_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'a.enter-btn')
                        if enter_buttons:
                            enter_buttons[0].click()
                            self.add_log("已点击年龄验证进入按钮")
                            time.sleep(3)  # 等待页面重定向
                        else:
                            # 尝试点击英文按钮
                            enter_buttons = self.driver.find_elements(By.XPATH, '//a[contains(text(), "If you are over 18")]')
                            if enter_buttons:
                                enter_buttons[0].click()
                                self.add_log("已点击英文年龄验证按钮")
                                time.sleep(3)
                    except Exception as age_error:
                        self.add_log(f"年龄验证处理: {str(age_error)}")
                
                # 等待页面加载完成
                time.sleep(2)
                
                # 再次检查页面内容
                html = self.driver.page_source
                if "满18岁" in html or "SEHUATANG.ORG" in self.driver.title:
                    self.add_log("仍然在年龄验证页面，可能需要手动处理", "WARNING")
                    return ""
                
                self.add_log(f"成功抓取 {url}")
                return html
                
            except Exception as e:
                self.add_log(f"抓取 {url} 失败 (第 {attempt + 1}/{retries} 次): {str(e)}", "ERROR")
                if attempt < retries - 1:
                    wait_time = 2 ** (attempt + 1)
                    self.add_log(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    self.add_log(f"达到最大重试次数，跳过 {url}", "ERROR")
                    return ""
        return ""

    def extract_thread_urls(self, html: str) -> List[Dict]:
        """从主页面提取所有主题的第一页链接，返回帖子信息列表"""
        soup = BeautifulSoup(html, 'html.parser')
        posts = []
        thread_base = {}
        
        # 多种可能的链接模式
        patterns = [
            r'thread-\d+-\d+-\d+\.html',
            r'thread-\d+\.html',
            r'thread\.php\?tid=\d+',
            r'forum\.php\?mod=viewthread&tid=\d+'
        ]
        
        # 查找所有链接
        for a_tag in soup.find_all('a', href=True):
            href = a_tag.get('href', '')
            title = a_tag.get_text(strip=True)
            
            # 检查是否匹配任何模式
            for pattern in patterns:
                if re.search(pattern, href):
                    # 处理相对URL
                    if href.startswith('/'):
                        href = f"https://sehuatang.org{href}"
                    elif not href.startswith('http'):
                        href = f"https://sehuatang.org/{href}"
                    
                    # 提取主题ID并生成第一页链接
                    if 'thread-' in href and '.html' in href:
                        # 处理 thread-xxx-xxx-xxx.html 格式
                        match = re.match(r'.*?(thread-\d+)-\d+-\d+\.html', href)
                        if match:
                            thread_id = match.group(1)
                            if thread_id not in thread_base:
                                full_url = f"https://sehuatang.org/{thread_id}-1-1.html"
                                thread_base[thread_id] = full_url
                                posts.append({
                                    'title': title,
                                    'url': full_url,
                                    'author': '未知',
                                    'post_time': '',
                                    'replies': '0',
                                    'views': '0'
                                })
                                self.add_log(f"找到主题第一页链接: {full_url}")
                    elif 'tid=' in href:
                        # 处理 tid=xxx 格式
                        match = re.search(r'tid=(\d+)', href)
                        if match:
                            tid = match.group(1)
                            thread_id = f"thread-{tid}"
                            if thread_id not in thread_base:
                                full_url = f"https://sehuatang.org/{thread_id}-1-1.html"
                                thread_base[thread_id] = full_url
                                posts.append({
                                    'title': title,
                                    'url': full_url,
                                    'author': '未知',
                                    'post_time': '',
                                    'replies': '0',
                                    'views': '0'
                                })
                                self.add_log(f"找到主题第一页链接: {full_url}")
                    break  # 匹配到一个模式就够了
        
        if not posts:
            self.add_log("未找到任何主题链接，检查HTML结构或选择器", "WARNING")
        
        return posts

    def get_forum_list(self, forum_id: str = "2") -> List[Dict]:
        """获取论坛帖子列表"""
        try:
            if forum_id not in self.themes:
                self.add_log(f"无效的论坛ID: {forum_id}", "ERROR")
                return []
            
            theme_info = self.themes[forum_id]
            url = theme_info["url"]
            self.add_log(f"正在获取论坛列表: {url}")
            
            # 初始化WebDriver
            if not self.driver:
                self.driver = self.setup_driver()
            
            # 抓取页面
            html = self.fetch_page(url)
            if not html:
                return []
            
            # 提取帖子信息
            posts = self.extract_thread_urls(html)
            self.add_log(f"成功获取 {len(posts)} 个帖子")
            return posts
            
        except Exception as e:
            self.add_log(f"获取论坛列表失败: {e}", "ERROR")
            return []

    def get_post_content(self, post_url: str) -> Optional[Dict]:
        """获取帖子详细内容"""
        try:
            self.add_log(f"正在获取帖子内容: {post_url}")
            
            # 确保WebDriver已初始化
            if not self.driver:
                self.driver = self.setup_driver()
            
            # 抓取页面
            html = self.fetch_page(post_url)
            if not html:
                return None
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # 提取帖子标题
            title_elem = soup.find('span', id='thread_subject')
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            # 提取帖子内容
            content_elem = soup.find('td', class_='t_f')
            content = content_elem.get_text(strip=True) if content_elem else ""
            
            # 提取图片链接
            images = []
            if content_elem:
                img_tags = content_elem.find_all('img')
                for img in img_tags:
                    src = img.get('src') or img.get('data-src')
                    if src:
                        if not src.startswith('http'):
                            src = f"https://sehuatang.org{src}" if src.startswith('/') else f"https://sehuatang.org/{src}"
                        images.append(src)
            
            # 提取磁力链接
            magnets = self.extract_magnet_links(html)
            
            # 提取番号
            code = self._extract_code(title + " " + content)
            
            # 提取文件大小
            size = self._extract_size(content)
            
            # 判断是否有码
            is_uncensored = self._is_uncensored(title + " " + content)
            
            post_data = {
                'title': title,
                'content': content,
                'url': post_url,
                'images': images,
                'magnets': magnets,
                'code': code,
                'size': size,
                'is_uncensored': is_uncensored,
                'crawl_time': datetime.now().isoformat()
            }
            
            self.add_log(f"成功获取帖子内容: {title}")
            return post_data
            
        except Exception as e:
            self.add_log(f"获取帖子内容失败 {post_url}: {e}", "ERROR")
            return None

    def extract_magnet_links(self, html: str) -> List[str]:
        """从二级页面提取磁力链接"""
        soup = BeautifulSoup(html, 'html.parser')
        magnet_links = []
        
        # 从多个可能的内容区域提取磁力链接
        for tag in soup.select('div.blockcode, div.t_msgfont, div.postcontent, div.message, p, td.t_f'):
            text = tag.get_text()
            magnet_matches = re.findall(r'magnet:\?xt=urn:[a-z0-9]+:[a-z0-9]{32,}', text, re.IGNORECASE)
            magnet_links.extend(magnet_matches)
        
        # 从链接标签中提取
        for a_tag in soup.select('a'):
            href = a_tag.get('href', '')
            if href.startswith('magnet:'):
                magnet_links.append(href)
        
        # 去重
        return list(set(magnet_links))

    def _extract_code(self, text: str) -> Optional[str]:
        """提取番号"""
        patterns = [
            r'([A-Z]{2,10}-\d{2,5})',  # 标准格式：ABP-123
            r'([A-Z]{2,10}\s+\d{2,5})',  # 空格分隔：ABP 123
            r'([A-Z]{2,10}_\d{2,5})',   # 下划线分隔：ABP_123
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                code = match.group(1)
                # 标准化格式
                code = re.sub(r'[\s_]', '-', code.upper())
                return code
        
        return None

    def _extract_size(self, text: str) -> Optional[str]:
        """提取文件大小"""
        size_match = re.search(r'(\d+(?:\.\d+)?)\s*(GB|MB|G|M)', text, re.IGNORECASE)
        if size_match:
            size = size_match.group(1)
            unit = size_match.group(2).upper()
            # 标准化单位
            if unit in ["G", "GB"]:
                return f"{size}GB"
            elif unit in ["M", "MB"]:
                return f"{size}MB"
        return None

    def _is_uncensored(self, text: str) -> bool:
        """判断是否为无码"""
        uncensored_keywords = [
            "无码", "無碼", "uncensored", "无修正", "無修正",
            "流出", "破解", "破解版", "破解版流出"
        ]
        return any(keyword in text for keyword in uncensored_keywords)

    def crawl_forum_pages(self, forum_id: str = "2", start_page: int = 1, end_page: int = 1) -> List[Dict]:
        """爬取指定页面的帖子"""
        try:
            # 验证主题ID
            if forum_id not in self.themes:
                self.add_log(f"无效的主题ID: {forum_id}", "ERROR")
                return []
            
            theme_info = self.themes[forum_id]
            self.add_log(f"开始爬取主题: {theme_info['name']} (ID: {forum_id})")
            self.add_log(f"爬取页数: 第{start_page}页到第{end_page}页")
            
            # 初始化WebDriver
            if not self.driver:
                self.driver = self.setup_driver()
            
            all_posts = []
            
            # 遍历指定页数
            for page_num in range(start_page, end_page + 1):
                self.add_log(f"开始处理第 {page_num} 页")
                
                # 构建URL
                start_url = theme_info["url"].replace("-1.html", f"-{page_num}.html")
                
                # 抓取主页面
                main_html = self.fetch_page(start_url)
                if not main_html:
                    self.add_log(f"无法访问第 {page_num} 页: {start_url}", "ERROR")
                    continue
                
                # 提取所有主题第一页链接
                thread_urls = self.extract_thread_urls(main_html)
                if not thread_urls:
                    self.add_log(f"第 {page_num} 页未找到任何主题链接", "WARNING")
                    continue
                
                self.add_log(f"第 {page_num} 页找到 {len(thread_urls)} 个主题")
                
                # 遍历二级页面提取详细信息
                for i, post_info in enumerate(thread_urls[:10], 1):  # 限制每页最多10个帖子
                    self.add_log(f"处理第 {page_num} 页 {i}/{len(thread_urls)}: {post_info['url']}")
                    
                    post_content = self.get_post_content(post_info['url'])
                    if post_content:
                        # 合并帖子列表信息和详细内容
                        post_content.update({
                            'author': post_info.get('author', ''),
                            'post_time': post_info.get('post_time', ''),
                            'replies': post_info.get('replies', ''),
                            'views': post_info.get('views', '')
                        })
                        all_posts.append(post_content)
                    
                    # 添加延迟，避免请求过快
                    time.sleep(1)
                
                # 页面间延迟
                if page_num < end_page:
                    time.sleep(3)
            
            self.add_log(f"爬取完成，共获取 {len(all_posts)} 个帖子")
            return all_posts
            
        except Exception as e:
            self.add_log(f"爬取过程中发生错误: {str(e)}", "ERROR")
            return []

    def save_posts_to_file(self, posts: List[Dict], filename: str = None):
        """保存帖子数据到文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sehuatang_posts_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(posts, f, ensure_ascii=False, indent=2)
            
            self.add_log(f"帖子数据已保存到: {filename}")
            
        except Exception as e:
            self.add_log(f"保存文件失败: {e}", "ERROR")

    def close(self):
        """关闭WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                self.add_log("WebDriver已关闭")
            except Exception as e:
                self.add_log(f"关闭WebDriver失败: {e}", "ERROR")

def main():
    """主函数"""
    # 设置代理（如果需要）
    proxy = os.getenv('HTTP_PROXY') or os.getenv('HTTPS_PROXY')
    
    # 创建爬虫实例
    crawler = SehuatangCrawler(proxy=proxy)
    
    try:
        # 爬取帖子
        posts = crawler.crawl_forum_pages(
            forum_id="2",  # 国产原创区
            start_page=1,
            end_page=1
        )
        
        # 保存结果
        if posts:
            crawler.save_posts_to_file(posts)
            print(f"成功爬取 {len(posts)} 个帖子")
        else:
            print("未获取到任何帖子")
    finally:
        # 确保关闭WebDriver
        crawler.close()

if __name__ == "__main__":
    main()
