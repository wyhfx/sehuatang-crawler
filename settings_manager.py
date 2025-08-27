#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置管理器
负责管理应用配置，支持数据库存储和环境变量同步
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from models_settings import Setting, DEFAULT_SETTINGS

class SettingsManager:
    def __init__(self, db_session: Session):
        self.db = db_session
        self._cache = {}  # 内存缓存
    
    def get_setting(self, key: str, default: str = "") -> str:
        """获取设置值"""
        # 先从缓存获取
        if key in self._cache:
            return self._cache[key]
        
        # 从数据库获取
        setting = self.db.query(Setting).filter(Setting.key == key).first()
        if setting:
            value = setting.value or default
            self._cache[key] = value
            return value
        
        # 从环境变量获取
        env_value = os.getenv(key.upper())
        if env_value is not None:
            self._cache[key] = env_value
            return env_value
        
        return default
    
    def set_setting(self, key: str, value: str, description: str = "", category: str = "general") -> bool:
        """设置值"""
        try:
            setting = self.db.query(Setting).filter(Setting.key == key).first()
            
            if setting:
                # 更新现有设置
                setting.value = value
                if description:
                    setting.description = description
                if category:
                    setting.category = category
            else:
                # 创建新设置
                setting = Setting(
                    key=key,
                    value=value,
                    description=description,
                    category=category
                )
                self.db.add(setting)
            
            self.db.commit()
            
            # 更新缓存
            self._cache[key] = value
            
            # 同步到环境变量（某些关键设置）
            self._sync_to_env(key, value)
            
            return True
            
        except Exception as e:
            logging.error(f"设置值失败: {e}")
            self.db.rollback()
            return False
    
    def get_all_settings(self) -> Dict[str, Any]:
        """获取所有设置"""
        settings = {}
        
        # 从数据库获取
        db_settings = self.db.query(Setting).all()
        for setting in db_settings:
            settings[setting.key] = {
                "value": setting.value,
                "description": setting.description,
                "category": setting.category
            }
        
        # 补充默认设置
        for default_setting in DEFAULT_SETTINGS:
            key = default_setting["key"]
            if key not in settings:
                settings[key] = {
                    "value": default_setting["value"],
                    "description": default_setting["description"],
                    "category": default_setting["category"]
                }
        
        return settings
    
    def get_settings_by_category(self, category: str) -> Dict[str, Any]:
        """按分类获取设置"""
        settings = {}
        db_settings = self.db.query(Setting).filter(Setting.category == category).all()
        
        for setting in db_settings:
            settings[setting.key] = {
                "value": setting.value,
                "description": setting.description,
                "category": setting.category
            }
        
        # 补充默认设置
        for default_setting in DEFAULT_SETTINGS:
            if default_setting["category"] == category:
                key = default_setting["key"]
                if key not in settings:
                    settings[key] = {
                        "value": default_setting["value"],
                        "description": default_setting["description"],
                        "category": default_setting["category"]
                    }
        
        return settings
    
    def update_settings(self, settings_data: Dict[str, str]) -> bool:
        """批量更新设置"""
        try:
            for key, value in settings_data.items():
                self.set_setting(key, value)
            return True
        except Exception as e:
            logging.error(f"批量更新设置失败: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """重置为默认设置"""
        try:
            # 清空现有设置
            self.db.query(Setting).delete()
            
            # 插入默认设置
            for default_setting in DEFAULT_SETTINGS:
                setting = Setting(**default_setting)
                self.db.add(setting)
            
            self.db.commit()
            
            # 清空缓存
            self._cache.clear()
            
            return True
            
        except Exception as e:
            logging.error(f"重置默认设置失败: {e}")
            self.db.rollback()
            return False
    
    def _sync_to_env(self, key: str, value: str):
        """同步设置到环境变量"""
        # 只同步关键设置
        env_mapping = {
            "metatube_url": "METATUBE_URL",
            "metatube_provider": "METATUBE_PROVIDER",
            "metatube_fallback": "METATUBE_FALLBACK",
            "trans_provider": "TRANS_PROVIDER",
            "baidu_appid": "BAIDU_APPID",
            "baidu_key": "BAIDU_KEY",
            "http_proxy": "HTTP_PROXY",
            "https_proxy": "HTTPS_PROXY",
            "no_proxy": "NO_PROXY",
        }
        
        if key in env_mapping:
            env_key = env_mapping[key]
            os.environ[env_key] = value
    
    def get_datasource_config(self) -> Dict[str, str]:
        """获取数据源配置"""
        return {
            "datasource": self.get_setting("datasource", "metatube"),
            "metatube_provider": self.get_setting("metatube_provider", ""),
            "metatube_fallback": self.get_setting("metatube_fallback", "true"),
            "metatube_url": self.get_setting("metatube_url", "http://192.168.31.102:8080"),
        }
    
    def get_translate_config(self) -> Dict[str, str]:
        """获取翻译配置"""
        return {
            "translate_enabled": self.get_setting("translate_enabled", "false"),
            "trans_provider": self.get_setting("trans_provider", "baidu"),
            "baidu_appid": self.get_setting("baidu_appid", ""),
            "baidu_key": self.get_setting("baidu_key", ""),
        }
    
    def get_proxy_config(self) -> Dict[str, str]:
        """获取代理配置"""
        return {
            "http_proxy": self.get_setting("http_proxy", ""),
            "https_proxy": self.get_setting("https_proxy", ""),
            "no_proxy": self.get_setting("no_proxy", "localhost,127.0.0.1"),
        }

def get_settings_manager(db_session: Session) -> SettingsManager:
    """便捷函数：获取设置管理器"""
    return SettingsManager(db_session)
