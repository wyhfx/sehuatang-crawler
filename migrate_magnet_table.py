#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
磁力链接表数据库迁移脚本
"""

import sqlite3
import os
from db import engine
from models_magnet import Base

def create_magnet_table():
    """创建磁力链接表"""
    try:
        # 创建表
        Base.metadata.create_all(engine)
        print("✅ 磁力链接表创建成功")
        
        # 创建索引
        from sqlalchemy import text
        with engine.connect() as conn:
            # 番号索引
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_magnet_links_v2_code ON magnet_links_v2(code)"))
            # 创建时间索引
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_magnet_links_v2_created_at ON magnet_links_v2(created_at)"))
            # 无码索引
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_magnet_links_v2_uncensored ON magnet_links_v2(is_uncensored)"))
            conn.commit()
            print("✅ 索引创建成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建磁力链接表失败: {e}")
        return False

def check_table_exists():
    """检查表是否存在"""
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='magnet_links_v2'"))
            return result.fetchone() is not None
    except Exception as e:
        print(f"❌ 检查表失败: {e}")
        return False

def get_table_info():
    """获取表结构信息"""
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(magnet_links_v2)"))
            columns = result.fetchall()
            
            print("📋 磁力链接表结构:")
            for col in columns:
                print(f"  {col[1]} ({col[2]}) - {col[5]}")
            
            return columns
    except Exception as e:
        print(f"❌ 获取表结构失败: {e}")
        return []

if __name__ == "__main__":
    print("🚀 开始创建磁力链接表...")
    
    if check_table_exists():
        print("⚠️  磁力链接表已存在")
        get_table_info()
    else:
        if create_magnet_table():
            print("✅ 磁力链接表创建完成")
            get_table_info()
        else:
            print("❌ 磁力链接表创建失败")
