# routes/magnet_routes.py
import json
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db import get_db
from magnet_manager import get_magnet_manager
from sehuatang_parser import parse_sehuatang_post

router = APIRouter()

@router.post("/api/magnets/parse-sehuatang")
def parse_sehuatang_post_api(html: str, source_url: str = "", db: Session = Depends(get_db)):
    """解析 Sehuatang 帖子并保存"""
    try:
        settings_manager = get_settings_manager(db)
        manager = get_magnet_manager(db, settings_manager)
        result = manager.parse_and_save_sehuatang_post(html, source_url)
        
        if not result:
            raise HTTPException(status_code=400, detail="解析失败或无有效数据")
        
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")

@router.get("/api/magnets/{code}")
def get_magnet_by_code(code: str, db: Session = Depends(get_db)):
    """根据番号获取磁力链接"""
    try:
        settings_manager = get_settings_manager(db)
        manager = get_magnet_manager(db, settings_manager)
        result = manager.get_magnet_by_code(code)
        
        if not result:
            raise HTTPException(status_code=404, detail="未找到该番号的磁力链接")
        
        return {"success": True, "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")

@router.get("/api/magnets/search/{keyword}")
def search_magnets(keyword: str, limit: int = 20, db: Session = Depends(get_db)):
    """搜索磁力链接"""
    try:
        settings_manager = get_settings_manager(db)
        manager = get_magnet_manager(db, settings_manager)
        results = manager.search_magnets(keyword, limit)
        
        return {
            "success": True, 
            "data": results,
            "total": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")

@router.get("/api/magnets/recent")
def get_recent_magnets(limit: int = 20, db: Session = Depends(get_db)):
    """获取最近的磁力链接"""
    try:
        settings_manager = get_settings_manager(db)
        manager = get_magnet_manager(db, settings_manager)
        results = manager.get_recent_magnets(limit)
        
        return {
            "success": True, 
            "data": results,
            "total": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")

@router.get("/api/magnets/statistics")
def get_magnet_statistics(db: Session = Depends(get_db)):
    """获取磁力链接统计信息"""
    try:
        settings_manager = get_settings_manager(db)
        manager = get_magnet_manager(db, settings_manager)
        stats = manager.get_statistics()
        
        return {"success": True, "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")

@router.post("/api/magnets/batch-parse")
def batch_parse_sehuatang_posts(posts: List[dict], db: Session = Depends(get_db)):
    """批量解析 Sehuatang 帖子"""
    try:
        settings_manager = get_settings_manager(db)
        manager = get_magnet_manager(db, settings_manager)
        results = []
        
        for post in posts:
            html = post.get("html", "")
            source_url = post.get("source_url", "")
            
            if html:
                result = manager.parse_and_save_sehuatang_post(html, source_url)
                if result:
                    results.append(result)
        
        return {
            "success": True,
            "data": results,
            "total": len(results),
            "processed": len(posts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量解析失败: {str(e)}")
