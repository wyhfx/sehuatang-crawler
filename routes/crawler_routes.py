# routes/crawler_routes.py
import json
import logging
from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db import get_db
from sehuatang_crawler import SehuatangCrawler
from magnet_manager import get_magnet_manager
from settings_manager import get_settings_manager

router = APIRouter()
logger = logging.getLogger(__name__)

class CrawlRequest(BaseModel):
    forum_id: str = "2"
    start_page: int = 1
    end_page: int = 1
    save_to_db: bool = True
    proxy: Optional[str] = None

class CrawlResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict] = None

@router.post("/api/crawler/start")
def start_crawling(request: CrawlRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """启动爬虫任务"""
    try:
        # 获取设置管理器
        settings_manager = get_settings_manager(db)
        
        # 获取代理配置
        proxy_config = settings_manager.get_proxy_config()
        proxy = request.proxy or proxy_config.get("proxy_url") if proxy_config.get("proxy_enabled") == "true" else None
        
        # 创建爬虫实例
        crawler = SehuatangCrawler(proxy=proxy)
        
        # 在后台执行爬虫任务
        background_tasks.add_task(
            crawl_and_process_posts,
            crawler,
            request.forum_id,
            request.start_page,
            request.end_page,
            request.save_to_db,
            db
        )
        
        return CrawlResponse(
            success=True,
            message="爬虫任务已启动，正在后台执行",
            data={
                "forum_id": request.forum_id,
                "start_page": request.start_page,
                "end_page": request.end_page,
                "save_to_db": request.save_to_db
            }
        )
        
    except Exception as e:
        logger.error(f"启动爬虫失败: {e}")
        raise HTTPException(status_code=500, detail=f"启动爬虫失败: {str(e)}")

@router.post("/api/crawler/crawl-single")
def crawl_single_post(post_url: str, db: Session = Depends(get_db)):
    """爬取单个帖子"""
    try:
        # 获取设置管理器
        settings_manager = get_settings_manager(db)
        
        # 获取代理配置
        proxy_config = settings_manager.get_proxy_config()
        proxy = proxy_config.get("proxy_url") if proxy_config.get("proxy_enabled") == "true" else None
        
        # 创建爬虫实例
        crawler = SehuatangCrawler(proxy=proxy)
        
        # 爬取帖子内容
        post_data = crawler.get_post_content(post_url)
        
        if not post_data:
            raise HTTPException(status_code=404, detail="无法获取帖子内容")
        
        # 如果启用了数据库保存
        if post_data.get('code') and post_data.get('magnets'):
            magnet_manager = get_magnet_manager(db, settings_manager)
            
            # 将爬取的数据转换为解析器格式
            html_content = f"""
            <html>
            <head><title>{post_data['title']}</title></head>
            <body>
            <td class="t_f">{post_data['content']}</td>
            </body>
            </html>
            """
            
            # 解析并保存到数据库
            result = magnet_manager.parse_and_save_sehuatang_post(html_content, post_url)
            
            if result:
                return CrawlResponse(
                    success=True,
                    message="帖子爬取并保存成功",
                    data={
                        "post": post_data,
                        "saved_to_db": True,
                        "db_result": result
                    }
                )
        
        return CrawlResponse(
            success=True,
            message="帖子爬取成功",
            data={
                "post": post_data,
                "saved_to_db": False
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"爬取单个帖子失败: {e}")
        raise HTTPException(status_code=500, detail=f"爬取失败: {str(e)}")

@router.get("/api/crawler/status")
def get_crawl_status():
    """获取爬虫状态"""
    # 这里可以实现爬虫状态监控
    return {
        "success": True,
        "data": {
            "status": "idle",
            "last_crawl_time": None,
            "total_crawled": 0
        }
    }

@router.get("/api/crawler/forums")
def get_forum_list():
    """获取可用的论坛列表"""
    forums = [
        {"id": "2", "name": "亚洲无码区", "description": "亚洲无码影片"},
        {"id": "3", "name": "亚洲有码区", "description": "亚洲有码影片"},
        {"id": "4", "name": "欧美无码区", "description": "欧美无码影片"},
        {"id": "5", "name": "国产原创区", "description": "国产原创影片"},
        {"id": "6", "name": "动漫区", "description": "动漫资源"},
        {"id": "7", "name": "写真区", "description": "写真资源"},
        {"id": "8", "name": "其他资源区", "description": "其他资源"}
    ]
    
    return {
        "success": True,
        "data": forums
    }

async def crawl_and_process_posts(
    crawler: SehuatangCrawler,
    forum_id: str,
    start_page: int,
    end_page: int,
    save_to_db: bool,
    db: Session
):
    """后台爬虫任务"""
    try:
        logger.info(f"开始爬取论坛 {forum_id}，页面 {start_page}-{end_page}")
        
        # 爬取帖子
        posts = crawler.crawl_forum_pages(forum_id, start_page, end_page)
        
        if not posts:
            logger.warning("未获取到任何帖子")
            return
        
        # 保存到文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"crawled_posts_{forum_id}_{timestamp}.json"
        crawler.save_posts_to_file(posts, filename)
        
        # 如果启用了数据库保存
        if save_to_db:
            settings_manager = get_settings_manager(db)
            magnet_manager = get_magnet_manager(db, settings_manager)
            
            saved_count = 0
            for post in posts:
                try:
                    if post.get('code') and post.get('magnets'):
                        # 将爬取的数据转换为解析器格式
                        html_content = f"""
                        <html>
                        <head><title>{post['title']}</title></head>
                        <body>
                        <td class="t_f">{post['content']}</td>
                        </body>
                        </html>
                        """
                        
                        # 解析并保存到数据库
                        result = magnet_manager.parse_and_save_sehuatang_post(html_content, post['url'])
                        if result:
                            saved_count += 1
                            
                except Exception as e:
                    logger.error(f"保存帖子到数据库失败: {e}")
                    continue
            
            logger.info(f"爬取完成，共获取 {len(posts)} 个帖子，成功保存 {saved_count} 个到数据库")
        else:
            logger.info(f"爬取完成，共获取 {len(posts)} 个帖子")
            
    except Exception as e:
        logger.error(f"后台爬虫任务失败: {e}")

# 添加缺失的导入
from datetime import datetime
from fastapi import Depends
