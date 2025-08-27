#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置表数据库迁移脚本
"""

import os
from db import engine
from models_settings import Base, Setting, DEFAULT_SETTINGS

def create_settings_table():
    """创建设置表"""
    try:
        # 创建表
        Base.metadata.create_all(engine)
        print("✅ 设置表创建成功")
        
        # 插入默认设置
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # 检查是否已有设置
            existing_count = db.query(Setting).count()
            if existing_count == 0:
                # 插入默认设置
                for default_setting in DEFAULT_SETTINGS:
                    setting = Setting(**default_setting)
                    db.add(setting)
                
                db.commit()
                print("✅ 默认设置插入成功")
            else:
                print(f"⚠️  设置表已有 {existing_count} 条记录，跳过默认设置插入")
                
        except Exception as e:
            print(f"❌ 插入默认设置失败: {e}")
            db.rollback()
        finally:
            db.close()
        
        return True
        
    except Exception as e:
        print(f"❌ 创建设置表失败: {e}")
        return False

def check_table_exists():
    """检查表是否存在"""
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'"))
            return result.fetchone() is not None
    except Exception as e:
        print(f"❌ 检查表失败: {e}")
        return False

def get_table_info():
    """获取表结构信息"""
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(settings)"))
            columns = result.fetchall()
            
            print("📋 设置表结构:")
            for col in columns:
                print(f"  {col[1]} ({col[2]}) - {col[5]}")
            
            return columns
    except Exception as e:
        print(f"❌ 获取表结构失败: {e}")
        return []

def get_settings_data():
    """获取设置数据"""
    try:
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        settings = db.query(Setting).all()
        
        print("📋 当前设置:")
        for setting in settings:
            print(f"  {setting.key}: {setting.value} ({setting.category})")
        
        db.close()
        return settings
    except Exception as e:
        print(f"❌ 获取设置数据失败: {e}")
        return []

if __name__ == "__main__":
    print("🚀 开始创建设置表...")
    
    if check_table_exists():
        print("⚠️  设置表已存在")
        get_table_info()
        get_settings_data()
    else:
        if create_settings_table():
            print("✅ 设置表创建完成")
            get_table_info()
            get_settings_data()
        else:
            print("❌ 设置表创建失败")
