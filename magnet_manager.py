#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
磁力链接管理器
负责解析、保存、查询磁力链接数据
"""

import json
import logging
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from models_magnet import MagnetLink
from sehuatang_parser import parse_sehuatang_post

class MagnetManager:
    def __init__(self, db_session: Session, settings_manager=None):
        self.db = db_session
        self.settings_manager = settings_manager
    
    def save_magnet_data(self, data: Dict) -> Optional[MagnetLink]:
        """保存磁力链接数据"""
        try:
            # 检查是否已存在
            existing = self.db.query(MagnetLink).filter(
                MagnetLink.code == data.get("code")
            ).first()
            
            if existing:
                # 更新现有记录
                self._update_magnet_link(existing, data)
            else:
                # 创建新记录
                existing = MagnetLink.from_dict(data)
                self.db.add(existing)
            
            self.db.commit()
            return existing
            
        except Exception as e:
            logging.error(f"保存磁力链接数据失败: {e}")
            self.db.rollback()
            return None
    
    def _update_magnet_link(self, magnet_link: MagnetLink, data: Dict):
        """更新磁力链接记录"""
        # 更新基础字段
        if data.get("title"):
            magnet_link.title = data["title"]
        if data.get("title_cn"):
            magnet_link.title_cn = data["title_cn"]
        if data.get("size"):
            magnet_link.size = data["size"]
        if "is_uncensored" in data:
            magnet_link.is_uncensored = data["is_uncensored"]
        if data.get("source_url"):
            magnet_link.source_url = data["source_url"]
        
        # 更新JSON字段
        for field in ["images", "magnets", "actresses", "actresses_cn", "tags", "tags_cn"]:
            if field in data and isinstance(data[field], list):
                setattr(magnet_link, field, json.dumps(data[field], ensure_ascii=False))
        
        # 更新元数据字段
        if data.get("studio"):
            magnet_link.studio = data["studio"]
        if data.get("studio_cn"):
            magnet_link.studio_cn = data["studio_cn"]
        if data.get("release_date"):
            magnet_link.release_date = data["release_date"]
        if data.get("cover_url"):
            magnet_link.cover_url = data["cover_url"]
        if data.get("source"):
            magnet_link.source = data["source"]
        if data.get("raw_text"):
            magnet_link.raw_text = data["raw_text"]
    
    def get_magnet_by_code(self, code: str) -> Optional[Dict]:
        """根据番号获取磁力链接数据"""
        try:
            magnet = self.db.query(MagnetLink).filter(
                MagnetLink.code == code.upper()
            ).first()
            
            return magnet.to_dict() if magnet else None
            
        except Exception as e:
            logging.error(f"获取磁力链接数据失败: {e}")
            return None
    
    def search_magnets(self, keyword: str, limit: int = 20) -> List[Dict]:
        """搜索磁力链接"""
        try:
            # 支持番号、标题、女优搜索
            query = self.db.query(MagnetLink).filter(
                (MagnetLink.code.contains(keyword)) |
                (MagnetLink.title.contains(keyword)) |
                (MagnetLink.title_cn.contains(keyword)) |
                (MagnetLink.actresses_cn.contains(keyword))
            ).limit(limit)
            
            results = []
            for magnet in query.all():
                results.append(magnet.to_dict())
            
            return results
            
        except Exception as e:
            logging.error(f"搜索磁力链接失败: {e}")
            return []
    
    def get_recent_magnets(self, limit: int = 20) -> List[Dict]:
        """获取最近的磁力链接"""
        try:
            magnets = self.db.query(MagnetLink).order_by(
                MagnetLink.created_at.desc()
            ).limit(limit).all()
            
            return [magnet.to_dict() for magnet in magnets]
            
        except Exception as e:
            logging.error(f"获取最近磁力链接失败: {e}")
            return []
    
    def parse_and_save_sehuatang_post(self, html: str, source_url: str = "") -> Optional[Dict]:
        """解析 Sehuatang 帖子并保存"""
        try:
            # 解析帖子
            parsed_data = parse_sehuatang_post(html, source_url, self.settings_manager)
            
            # 检查是否有有效数据
            if not parsed_data.get("code") or not parsed_data.get("magnets"):
                logging.warning(f"解析结果无效: {parsed_data.get('code')}")
                return None
            
            # 保存到数据库
            magnet_link = self.save_magnet_data(parsed_data)
            
            return magnet_link.to_dict() if magnet_link else None
            
        except Exception as e:
            logging.error(f"解析并保存 Sehuatang 帖子失败: {e}")
            return None
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        try:
            total = self.db.query(MagnetLink).count()
            uncensored = self.db.query(MagnetLink).filter(
                MagnetLink.is_uncensored == True
            ).count()
            
            return {
                "total": total,
                "uncensored": uncensored,
                "censored": total - uncensored
            }
            
        except Exception as e:
            logging.error(f"获取统计信息失败: {e}")
            return {"total": 0, "uncensored": 0, "censored": 0}

def get_magnet_manager(db_session: Session, settings_manager=None) -> MagnetManager:
    """便捷函数：获取磁力链接管理器"""
    return MagnetManager(db_session, settings_manager)
