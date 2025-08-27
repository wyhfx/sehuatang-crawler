from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
from datetime import datetime, timedelta
import json
import os
from pydantic import BaseModel

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

# 数据模型
class JobCreate(BaseModel):
    name: str
    forum_id: str
    start_page: int = 1
    end_page: int = 1
    schedule: Optional[str] = None  # cron表达式
    enabled: bool = True

class JobUpdate(BaseModel):
    name: Optional[str] = None
    forum_id: Optional[str] = None
    start_page: Optional[int] = None
    end_page: Optional[int] = None
    schedule: Optional[str] = None
    enabled: Optional[bool] = None

class Job(BaseModel):
    id: str
    name: str
    forum_id: str
    forum_name: str
    start_page: int
    end_page: int
    schedule: Optional[str]
    enabled: bool
    last_run: Optional[datetime]
    next_run: Optional[datetime]
    status: str  # pending, running, completed, failed
    created_at: datetime
    updated_at: datetime

class JobExecution(BaseModel):
    id: str
    job_id: str
    status: str
    start_time: datetime
    end_time: Optional[datetime]
    progress: int = 0
    total_pages: int
    current_page: int
    results_count: int = 0
    error_message: Optional[str] = None

# 模拟数据存储
JOBS_FILE = "data/jobs.json"
EXECUTIONS_FILE = "data/job_executions.json"

def ensure_data_dir():
    """确保数据目录存在"""
    os.makedirs("data", exist_ok=True)

def load_jobs():
    """加载任务数据"""
    ensure_data_dir()
    if os.path.exists(JOBS_FILE):
        with open(JOBS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_jobs(jobs):
    """保存任务数据"""
    ensure_data_dir()
    with open(JOBS_FILE, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2, default=str)

def load_executions():
    """加载执行记录"""
    ensure_data_dir()
    if os.path.exists(EXECUTIONS_FILE):
        with open(EXECUTIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_executions(executions):
    """保存执行记录"""
    ensure_data_dir()
    with open(EXECUTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(executions, f, ensure_ascii=False, indent=2, default=str)

# 论坛配置
FORUMS = {
    "36": "亚洲无码",
    "37": "亚洲有码", 
    "2": "国产原创",
    "103": "高清中文字幕",
    "104": "素人原创",
    "39": "动漫原创",
    "152": "韩国主播"
}

@router.get("/", response_model=List[Job])
async def get_jobs():
    """获取所有任务"""
    jobs = load_jobs()
    return jobs

@router.get("/{job_id}", response_model=Job)
async def get_job(job_id: str):
    """获取单个任务"""
    jobs = load_jobs()
    for job in jobs:
        if job["id"] == job_id:
            return job
    raise HTTPException(status_code=404, detail="任务不存在")

@router.post("/", response_model=Job)
async def create_job(job_data: JobCreate):
    """创建新任务"""
    jobs = load_jobs()
    
    # 生成任务ID
    job_id = f"job_{len(jobs) + 1}_{int(datetime.now().timestamp())}"
    
    # 创建任务
    job = {
        "id": job_id,
        "name": job_data.name,
        "forum_id": job_data.forum_id,
        "forum_name": FORUMS.get(job_data.forum_id, "未知论坛"),
        "start_page": job_data.start_page,
        "end_page": job_data.end_page,
        "schedule": job_data.schedule,
        "enabled": job_data.enabled,
        "last_run": None,
        "next_run": None,
        "status": "pending",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    jobs.append(job)
    save_jobs(jobs)
    
    return job

@router.put("/{job_id}", response_model=Job)
async def update_job(job_id: str, job_data: JobUpdate):
    """更新任务"""
    jobs = load_jobs()
    
    for job in jobs:
        if job["id"] == job_id:
            # 更新字段
            if job_data.name is not None:
                job["name"] = job_data.name
            if job_data.forum_id is not None:
                job["forum_id"] = job_data.forum_id
                job["forum_name"] = FORUMS.get(job_data.forum_id, "未知论坛")
            if job_data.start_page is not None:
                job["start_page"] = job_data.start_page
            if job_data.end_page is not None:
                job["end_page"] = job_data.end_page
            if job_data.schedule is not None:
                job["schedule"] = job_data.schedule
            if job_data.enabled is not None:
                job["enabled"] = job_data.enabled
            
            job["updated_at"] = datetime.now()
            save_jobs(jobs)
            return job
    
    raise HTTPException(status_code=404, detail="任务不存在")

@router.delete("/{job_id}")
async def delete_job(job_id: str):
    """删除任务"""
    jobs = load_jobs()
    
    for i, job in enumerate(jobs):
        if job["id"] == job_id:
            jobs.pop(i)
            save_jobs(jobs)
            return {"message": "任务删除成功"}
    
    raise HTTPException(status_code=404, detail="任务不存在")

@router.post("/{job_id}/run")
async def run_job(job_id: str, background_tasks: BackgroundTasks):
    """立即运行任务"""
    jobs = load_jobs()
    
    for job in jobs:
        if job["id"] == job_id:
            if job["status"] == "running":
                raise HTTPException(status_code=400, detail="任务正在运行中")
            
            # 更新任务状态
            job["status"] = "running"
            job["last_run"] = datetime.now()
            job["updated_at"] = datetime.now()
            save_jobs(jobs)
            
            # 创建执行记录
            executions = load_executions()
            execution_id = f"exec_{len(executions) + 1}_{int(datetime.now().timestamp())}"
            execution = {
                "id": execution_id,
                "job_id": job_id,
                "status": "running",
                "start_time": datetime.now(),
                "end_time": None,
                "progress": 0,
                "total_pages": job["end_page"] - job["start_page"] + 1,
                "current_page": job["start_page"],
                "results_count": 0,
                "error_message": None
            }
            executions.append(execution)
            save_executions(executions)
            
            # 在后台运行任务（这里只是模拟）
            background_tasks.add_task(simulate_job_execution, job_id, execution_id)
            
            return {"message": "任务已启动", "execution_id": execution_id}
    
    raise HTTPException(status_code=404, detail="任务不存在")

@router.get("/{job_id}/executions", response_model=List[JobExecution])
async def get_job_executions(job_id: str):
    """获取任务执行记录"""
    executions = load_executions()
    job_executions = [execution for execution in executions if execution["job_id"] == job_id]
    return job_executions

@router.get("/executions/{execution_id}", response_model=JobExecution)
async def get_execution(execution_id: str):
    """获取执行记录详情"""
    executions = load_executions()
    for execution in executions:
        if execution["id"] == execution_id:
            return execution
    raise HTTPException(status_code=404, detail="执行记录不存在")

async def simulate_job_execution(job_id: str, execution_id: str):
    """模拟任务执行（实际应该调用爬虫）"""
    import asyncio
    
    # 模拟执行过程
    for i in range(10):
        await asyncio.sleep(1)  # 模拟工作
        
        # 更新执行进度
        executions = load_executions()
        for execution in executions:
            if execution["id"] == execution_id:
                execution["progress"] = (i + 1) * 10
                execution["current_page"] += 1
                execution["results_count"] += 5
                save_executions(executions)
                break
    
    # 完成执行
    executions = load_executions()
    for execution in executions:
        if execution["id"] == execution_id:
            execution["status"] = "completed"
            execution["end_time"] = datetime.now()
            execution["progress"] = 100
            save_executions(executions)
            break
    
    # 更新任务状态
    jobs = load_jobs()
    for job in jobs:
        if job["id"] == job_id:
            job["status"] = "completed"
            job["updated_at"] = datetime.now()
            save_jobs(jobs)
            break

@router.get("/forums")
async def get_forums():
    """获取可用论坛列表"""
    return [{"id": k, "name": v} for k, v in FORUMS.items()]
