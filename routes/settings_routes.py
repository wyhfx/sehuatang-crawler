# routes/settings_routes.py
import json
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db import get_db
from settings_manager import get_settings_manager

router = APIRouter()

@router.get("/api/settings")
def get_all_settings(db: Session = Depends(get_db)):
    """获取所有设置"""
    try:
        manager = get_settings_manager(db)
        settings = manager.get_all_settings()
        
        return {
            "success": True,
            "data": settings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取设置失败: {str(e)}")

@router.get("/api/settings/{category}")
def get_settings_by_category(category: str, db: Session = Depends(get_db)):
    """按分类获取设置"""
    try:
        manager = get_settings_manager(db)
        settings = manager.get_settings_by_category(category)
        
        return {
            "success": True,
            "data": settings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取设置失败: {str(e)}")

@router.post("/api/settings")
def update_settings(settings_data: Dict[str, str], db: Session = Depends(get_db)):
    """更新设置"""
    try:
        manager = get_settings_manager(db)
        success = manager.update_settings(settings_data)
        
        if success:
            return {
                "success": True,
                "message": "设置更新成功"
            }
        else:
            raise HTTPException(status_code=500, detail="设置更新失败")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新设置失败: {str(e)}")

@router.post("/api/settings/reset")
def reset_settings(db: Session = Depends(get_db)):
    """重置为默认设置"""
    try:
        manager = get_settings_manager(db)
        success = manager.reset_to_defaults()
        
        if success:
            return {
                "success": True,
                "message": "设置已重置为默认值"
            }
        else:
            raise HTTPException(status_code=500, detail="重置设置失败")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重置设置失败: {str(e)}")

@router.get("/api/settings/datasource/config")
def get_datasource_config(db: Session = Depends(get_db)):
    """获取数据源配置"""
    try:
        manager = get_settings_manager(db)
        config = manager.get_datasource_config()
        
        return {
            "success": True,
            "data": config
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据源配置失败: {str(e)}")

@router.get("/api/settings/translate/config")
def get_translate_config(db: Session = Depends(get_db)):
    """获取翻译配置"""
    try:
        manager = get_settings_manager(db)
        config = manager.get_translate_config()
        
        return {
            "success": True,
            "data": config
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取翻译配置失败: {str(e)}")

@router.get("/api/settings/proxy/config")
def get_proxy_config(db: Session = Depends(get_db)):
    """获取代理配置"""
    try:
        manager = get_settings_manager(db)
        config = manager.get_proxy_config()
        
        return {
            "success": True,
            "data": config
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取代理配置失败: {str(e)}")

@router.post("/api/settings/datasource")
def update_datasource_config(config: Dict[str, str], db: Session = Depends(get_db)):
    """更新数据源配置"""
    try:
        manager = get_settings_manager(db)
        success = manager.update_settings(config)
        
        if success:
            return {
                "success": True,
                "message": "数据源配置更新成功"
            }
        else:
            raise HTTPException(status_code=500, detail="数据源配置更新失败")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新数据源配置失败: {str(e)}")

@router.post("/api/settings/translate")
def update_translate_config(config: Dict[str, str], db: Session = Depends(get_db)):
    """更新翻译配置"""
    try:
        manager = get_settings_manager(db)
        success = manager.update_settings(config)
        
        if success:
            return {
                "success": True,
                "message": "翻译配置更新成功"
            }
        else:
            raise HTTPException(status_code=500, detail="翻译配置更新失败")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新翻译配置失败: {str(e)}")

@router.post("/api/settings/proxy")
def update_proxy_config(config: Dict[str, str], db: Session = Depends(get_db)):
    """更新代理配置"""
    try:
        manager = get_settings_manager(db)
        success = manager.update_settings(config)
        
        if success:
            return {
                "success": True,
                "message": "代理配置更新成功"
            }
        else:
            raise HTTPException(status_code=500, detail="代理配置更新失败")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新代理配置失败: {str(e)}")

@router.get("/api/settings/options")
def get_setting_options():
    """获取设置选项"""
    try:
        options = {
            "datasource_options": [
                {"label": "MetaTube", "value": "metatube"},
                {"label": "TPDB", "value": "tpdb"},
                {"label": "混合", "value": "mixed"}
            ],
            "provider_options": [
                {"label": "自动", "value": ""},
                {"label": "JavBus", "value": "JavBus"},
                {"label": "DMM", "value": "Dmm"},
                {"label": "AvSOX", "value": "AvSOX"}
            ],
            "trans_provider_options": [
                {"label": "百度翻译", "value": "baidu"},
                {"label": "DeepL", "value": "deepl"},
                {"label": "Google Translate", "value": "google"}
            ],
            "categories": [
                {"label": "数据源配置", "value": "datasource"},
                {"label": "翻译配置", "value": "translate"},
                {"label": "代理配置", "value": "proxy"}
            ]
        }
        
        return {
            "success": True,
            "data": options
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取设置选项失败: {str(e)}")
