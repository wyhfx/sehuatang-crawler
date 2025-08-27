#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
磁力链接数据库模型
"""

import json
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MagnetLink(Base):
    """磁力链接表"""
    __tablename__ = "magnet_links_v2"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), index=True, nullable=False, comment="番号")
    title = Column(String(500), comment="原始标题")
    title_cn = Column(String(500), comment="中文标题")
    size = Column(String(20), comment="文件大小")
    is_uncensored = Column(Boolean, default=False, comment="是否无码")
    images = Column(Text, comment="图片链接JSON数组")
    magnets = Column(Text, comment="磁力链接JSON数组")
    source_url = Column(String(500), comment="来源URL")
    
    # 元数据字段
    studio = Column(String(100), comment="厂牌")
    studio_cn = Column(String(100), comment="中文厂牌")
    actresses = Column(Text, comment="女优列表JSON数组")
    actresses_cn = Column(Text, comment="中文女优列表JSON数组")
    tags = Column(Text, comment="标签列表JSON数组")
    tags_cn = Column(Text, comment="中文标签列表JSON数组")
    release_date = Column(String(20), comment="发布日期")
    cover_url = Column(String(500), comment="封面图片")
    source = Column(String(50), comment="数据来源")
    
    # 系统字段
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    raw_text = Column(Text, comment="原始文本（用于调试）")
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "code": self.code,
            "title": self.title,
            "title_cn": self.title_cn,
            "size": self.size,
            "is_uncensored": self.is_uncensored,
            "images": json.loads(self.images) if self.images else [],
            "magnets": json.loads(self.magnets) if self.magnets else [],
            "source_url": self.source_url,
            "studio": self.studio,
            "studio_cn": self.studio_cn,
            "actresses": json.loads(self.actresses) if self.actresses else [],
            "actresses_cn": json.loads(self.actresses_cn) if self.actresses_cn else [],
            "tags": json.loads(self.tags) if self.tags else [],
            "tags_cn": json.loads(self.tags_cn) if self.tags_cn else [],
            "release_date": self.release_date,
            "cover_url": self.cover_url,
            "source": self.source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """从字典创建实例"""
        # 处理JSON字段
        for field in ["images", "magnets", "actresses", "actresses_cn", "tags", "tags_cn"]:
            if field in data and isinstance(data[field], list):
                data[field] = json.dumps(data[field], ensure_ascii=False)
        
        return cls(**data)
