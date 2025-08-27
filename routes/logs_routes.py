from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
import json
import os
from pydantic import BaseModel

router = APIRouter(prefix="/api/logs", tags=["logs"])

# 数据模型
class LogEntry(BaseModel):
    id: str
    timestamp: datetime
    level: str  # INFO, WARNING, ERROR, DEBUG
    message: str
    source: str  # crawler, system, api, etc.
    details: Optional[dict] = None

class LogFilter(BaseModel):
    level: Optional[str] = None
    source: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    search: Optional[str] = None

# 模拟数据存储
LOGS_FILE = "data/logs.json"

def ensure_data_dir():
    """确保数据目录存在"""
    os.makedirs("data", exist_ok=True)

def load_logs():
    """加载日志数据"""
    ensure_data_dir()
    if os.path.exists(LOGS_FILE):
        with open(LOGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_logs(logs):
    """保存日志数据"""
    ensure_data_dir()
    with open(LOGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2, default=str)

def add_log_entry(level: str, message: str, source: str = "system", details: Optional[dict] = None):
    """添加日志条目"""
    logs = load_logs()
    
    log_entry = {
        "id": f"log_{len(logs) + 1}_{int(datetime.now().timestamp())}",
        "timestamp": datetime.now(),
        "level": level,
        "message": message,
        "source": source,
        "details": details or {}
    }
    
    logs.append(log_entry)
    
    # 保持最多1000条日志
    if len(logs) > 1000:
        logs = logs[-1000:]
    
    save_logs(logs)
    return log_entry

@router.get("/", response_model=List[LogEntry])
async def get_logs(
    level: Optional[str] = Query(None, description="日志级别过滤"),
    source: Optional[str] = Query(None, description="来源过滤"),
    start_time: Optional[str] = Query(None, description="开始时间 (YYYY-MM-DD HH:MM:SS)"),
    end_time: Optional[str] = Query(None, description="结束时间 (YYYY-MM-DD HH:MM:SS)"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    limit: int = Query(100, description="返回条数限制"),
    offset: int = Query(0, description="偏移量")
):
    """获取日志列表"""
    logs = load_logs()
    
    # 过滤日志
    filtered_logs = []
    for log in logs:
        # 级别过滤
        if level and log["level"] != level:
            continue
        
        # 来源过滤
        if source and log["source"] != source:
            continue
        
        # 时间过滤
        if start_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                if log["timestamp"] < start_dt:
                    continue
            except:
                pass
        
        if end_time:
            try:
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                if log["timestamp"] > end_dt:
                    continue
            except:
                pass
        
        # 搜索过滤
        if search and search.lower() not in log["message"].lower():
            continue
        
        filtered_logs.append(log)
    
    # 按时间倒序排序
    filtered_logs.sort(key=lambda x: x["timestamp"], reverse=True)
    
    # 分页
    paginated_logs = filtered_logs[offset:offset + limit]
    
    return paginated_logs

@router.get("/{log_id}", response_model=LogEntry)
async def get_log(log_id: str):
    """获取单个日志条目"""
    logs = load_logs()
    for log in logs:
        if log["id"] == log_id:
            return log
    raise HTTPException(status_code=404, detail="日志条目不存在")

@router.delete("/")
async def clear_logs(
    level: Optional[str] = Query(None, description="只清除指定级别的日志"),
    source: Optional[str] = Query(None, description="只清除指定来源的日志"),
    before: Optional[str] = Query(None, description="清除指定时间之前的日志 (YYYY-MM-DD HH:MM:SS)")
):
    """清除日志"""
    logs = load_logs()
    original_count = len(logs)
    
    if level or source or before:
        # 条件清除
        filtered_logs = []
        for log in logs:
            # 级别过滤
            if level and log["level"] == level:
                continue
            
            # 来源过滤
            if source and log["source"] == source:
                continue
            
            # 时间过滤
            if before:
                try:
                    before_dt = datetime.fromisoformat(before.replace('Z', '+00:00'))
                    if log["timestamp"] < before_dt:
                        continue
                except:
                    pass
            
            filtered_logs.append(log)
        
        logs = filtered_logs
    else:
        # 清除所有日志
        logs = []
    
    save_logs(logs)
    
    return {
        "message": "日志清除成功",
        "cleared_count": original_count - len(logs),
        "remaining_count": len(logs)
    }

@router.get("/stats/summary")
async def get_log_stats():
    """获取日志统计信息"""
    logs = load_logs()
    
    # 按级别统计
    level_stats = {}
    source_stats = {}
    hourly_stats = {}
    
    for log in logs:
        # 级别统计
        level = log["level"]
        level_stats[level] = level_stats.get(level, 0) + 1
        
        # 来源统计
        source = log["source"]
        source_stats[source] = source_stats.get(source, 0) + 1
        
        # 小时统计（最近24小时）
        timestamp = log["timestamp"]
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        
        if timestamp > datetime.now() - timedelta(hours=24):
            hour = timestamp.strftime("%Y-%m-%d %H:00")
            hourly_stats[hour] = hourly_stats.get(hour, 0) + 1
    
    return {
        "total_logs": len(logs),
        "level_stats": level_stats,
        "source_stats": source_stats,
        "hourly_stats": hourly_stats,
        "recent_errors": len([log for log in logs if log["level"] == "ERROR" and 
                            (datetime.now() - (log["timestamp"] if isinstance(log["timestamp"], datetime) 
                             else datetime.fromisoformat(log["timestamp"].replace('Z', '+00:00')))).days < 1])
    }

@router.get("/levels")
async def get_log_levels():
    """获取可用的日志级别"""
    return ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

@router.get("/sources")
async def get_log_sources():
    """获取可用的日志来源"""
    logs = load_logs()
    sources = set(log["source"] for log in logs)
    return list(sources)

# 初始化一些示例日志
def init_sample_logs():
    """初始化示例日志数据"""
    logs = load_logs()
    if not logs:
        sample_logs = [
            {
                "id": "log_1_1",
                "timestamp": datetime.now() - timedelta(hours=2),
                "level": "INFO",
                "message": "系统启动成功",
                "source": "system",
                "details": {"version": "1.0.0"}
            },
            {
                "id": "log_2_1", 
                "timestamp": datetime.now() - timedelta(hours=1, minutes=30),
                "level": "INFO",
                "message": "开始爬取亚洲无码论坛",
                "source": "crawler",
                "details": {"forum_id": "36", "pages": "1-5"}
            },
            {
                "id": "log_3_1",
                "timestamp": datetime.now() - timedelta(hours=1, minutes=15),
                "level": "WARNING",
                "message": "网络连接超时，重试中...",
                "source": "crawler",
                "details": {"retry_count": 1, "url": "https://sehuatang.org/forum-36-1.html"}
            },
            {
                "id": "log_4_1",
                "timestamp": datetime.now() - timedelta(hours=1),
                "level": "INFO",
                "message": "爬取完成，共获取150条记录",
                "source": "crawler",
                "details": {"forum_id": "36", "total_records": 150, "duration": "15m30s"}
            },
            {
                "id": "log_5_1",
                "timestamp": datetime.now() - timedelta(minutes=30),
                "level": "ERROR",
                "message": "数据库连接失败",
                "source": "database",
                "details": {"error": "Connection refused", "retry_count": 3}
            },
            {
                "id": "log_6_1",
                "timestamp": datetime.now() - timedelta(minutes=15),
                "level": "INFO",
                "message": "数据库连接恢复",
                "source": "database",
                "details": {"recovery_time": "2m15s"}
            }
        ]
        
        for log in sample_logs:
            logs.append(log)
        
        save_logs(logs)

# 在模块加载时初始化示例日志
init_sample_logs()
