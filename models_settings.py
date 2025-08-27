#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置管理数据模型
"""

import json
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Setting(Base):
    """设置表"""
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, comment="设置键")
    value = Column(Text, comment="设置值")
    description = Column(String(200), comment="设置描述")
    category = Column(String(50), comment="设置分类")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "key": self.key,
            "value": self.value,
            "description": self.description,
            "category": self.category,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

# 默认设置配置
DEFAULT_SETTINGS = [
    # 数据源配置
    {"key": "datasource", "value": "metatube", "description": "优先数据源", "category": "datasource"},
    {"key": "metatube_provider", "value": "", "description": "MetaTube Provider", "category": "datasource"},
    {"key": "metatube_fallback", "value": "true", "description": "是否启用 Fallback", "category": "datasource"},
    {"key": "metatube_url", "value": "http://192.168.31.102:8080", "description": "MetaTube 服务地址", "category": "datasource"},
    
    # 翻译配置
    {"key": "translate_enabled", "value": "false", "description": "启用翻译功能", "category": "translate"},
    {"key": "trans_provider", "value": "baidu", "description": "翻译服务提供商", "category": "translate"},
    {"key": "baidu_appid", "value": "", "description": "百度翻译 AppID", "category": "translate"},
    {"key": "baidu_key", "value": "", "description": "百度翻译密钥", "category": "translate"},
    
    # 代理配置
    {"key": "http_proxy", "value": "", "description": "HTTP 代理", "category": "proxy"},
    {"key": "https_proxy", "value": "", "description": "HTTPS 代理", "category": "proxy"},
    {"key": "no_proxy", "value": "localhost,127.0.0.1", "description": "不使用代理的地址", "category": "proxy"},
]
