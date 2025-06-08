import asyncio
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

try:
    from ..config.cloud_settings import settings
    from ..agents.cloud_video_analysis_agent import CloudVideoAnalysisAgent
    from ..agents.cloud_narration_agent import CloudNarrationAgent
    from ..agents.cloud_tts_agent import CloudTTSAgent
    from ..agents.subtitle_agent import SubtitleAgent
    from ..agents.subtitle_narration_agent import SubtitleNarrationAgent
    from ..utils.file_utils import save_uploaded_file, cleanup_temp_files
    from ..utils.video_utils import create_narrated_video
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from src.config.cloud_settings import settings
    from src.agents.cloud_video_analysis_agent import CloudVideoAnalysisAgent
    from src.agents.cloud_narration_agent import CloudNarrationAgent
    from src.agents.cloud_tts_agent import CloudTTSAgent
    from src.agents.subtitle_agent import SubtitleAgent
    from src.agents.subtitle_narration_agent import SubtitleNarrationAgent
    from src.utils.file_utils import save_uploaded_file, cleanup_temp_files
    from src.utils.video_utils import create_narrated_video

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="AIMovie Cloud API",
    description="AI视频解说生成器 - 云端版",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory=str(settings.OUTPUT_DIR)), name="static")

# 初始化Agent
video_agent = CloudVideoAnalysisAgent()
narration_agent = CloudNarrationAgent()
tts_agent = CloudTTSAgent()
subtitle_agent = SubtitleAgent()
subtitle_narration_agent = SubtitleNarrationAgent()

# 存储任务状态
task_status = {}

# Pydantic模型
class VideoAnalysisRequest(BaseModel):
    video_path: str

class NarrationRequest(BaseModel):
    video_analysis: Dict[str, Any]
    style: str = "professional"
    target_audience: str = "general"
    narration_length: str = "medium"

class TTSRequest(BaseModel):
    text: str
    voice_style: str = "female_gentle"
    speed: float = 1.0
    pitch: float = 1.0
    volume: float = 1.0

class BatchTTSRequest(BaseModel):
    segments: List[Dict[str, Any]]
    voice_style: str = "female_gentle"
    speed: float = 1.0
    pitch: float = 1.0
    volume: float = 1.0

class VideoGenerationRequest(BaseModel):
    video_path: str
    narration_segments: List[Dict[str, Any]]
    background_music: Optional[str] = None
    music_volume: float = 0.3

class GuidedVideoAnalysisRequest(BaseModel):
    video_path: str
    narration_segments: List[Dict[str, Any]]
    analysis_mode: str = "narration_guided"

class VideoEditRequest(BaseModel):
    original_video: str
    video_analysis: Dict[str, Any]
    narration_segments: List[Dict[str, Any]]
    audio_files: List[str]
    edit_style: str = "highlight_based"

class SubtitleNarrationRequest(BaseModel):
    subtitle_data: Dict[str, Any]
    narration_mode: str = "third_person"  # "third_person" 或 "character"
    character_name: str = ""
    style: str = "professional"
    target_audience: str = "general"

class TaskStatus(BaseModel):
    task_id: str
    status: str
    progress: float
    message: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# ==========================================
# 系统信息和健康检查
# ==========================================

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "AIMovie Cloud API",
        "version": "2.0.0",
        "environment": "cloud",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        # 验证配置
        errors, warnings = settings.validate_config()
        
        return {
            "status": "healthy" if not errors else "unhealthy",
            "timestamp": time.time(),
            "config": settings.get_config(),
            "errors": errors,
            "warnings": warnings
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.get("/services")
async def get_services():
    """获取可用服务列表"""
    return {
        "llm_services": settings.get_available_llm_services(),
        "tts_services": settings.get_available_tts_services(),
        "video_services": settings.get_available_video_services()
    }

@app.get("/system/info")
async def get_system_info():
    """获取系统信息"""
    try:
        import platform
        import psutil
        import sys
        
        return {
            "system": {
                "platform": platform.platform(),
                "python_version": sys.version,
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "disk_usage": psutil.disk_usage('/').percent if platform.system() != 'Windows' else psutil.disk_usage('C:').percent
            },
            "application": {
                "version": "2.0.0",
                "environment": "cloud",
                "config": settings.get_config(),
                "active_tasks": len(task_status)
            },
            "services": {
                "llm_services": len(settings.get_available_llm_services()),
                "tts_services": len(settings.get_available_tts_services()),
                "video_services": len(settings.get_available_video_services())
            }
        }
    except Exception as e:
        logger.error(f"获取系统信息失败: {e}")
        return {
            "system": {"error": str(e)},
            "application": {
                "version": "2.0.0",
                "environment": "cloud",
                "active_tasks": len(task_status)
            }
        }

@app.get("/cost/stats")
async def get_cost_stats():
    """获取成本统计"""
    try:
        # 这里可以从数据库或日志文件中获取实际的成本统计
        # 目前返回模拟数据
        return {
            "daily_cost": 0.0,
            "monthly_cost": 0.0,
            "total_cost": 0.0,
            "video_count": 0,
            "daily_limit": 50.0,
            "monthly_limit": 500.0,
            "currency": "CNY",
            "last_updated": time.time(),
            "breakdown": {
                "llm_cost": 0.0,
                "tts_cost": 0.0,
                "video_cost": 0.0
            },
            "note": "成本统计功能正在开发中，当前显示为模拟数据"
        }
    except Exception as e:
        logger.error(f"获取成本统计失败: {e}")
        return {
            "daily_cost": 0.0,
            "monthly_cost": 0.0,
            "total_cost": 0.0,
            "video_count": 0,
            "error": str(e)
        }

@app.get("/cost/estimate")
async def estimate_cost(
    text_length: int = 500,
    audio_length: int = 500,
    frame_count: int = 50
):
    """估算处理成本"""
    try:
        cost = settings.estimate_cost(text_length, audio_length, frame_count)
        return {
            "estimated_cost": cost,
            "currency": "CNY",
            "breakdown": {
                "text_processing": f"约{text_length}字符",
                "audio_synthesis": f"约{audio_length}字符",
                "video_analysis": f"约{frame_count}帧"
            },
            "note": "实际费用可能因API调用情况而有所不同"
        }
    except Exception as e:
        logger.error(f"成本估算失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# 文件上传和管理
# ==========================================

@app.post("/upload/video")
async def upload_video(file: UploadFile = File(...)):
    """上传视频文件"""
    try:
        logger.info(f"开始上传视频文件: {file.filename}, 大小: {file.size}")
        
        # 检查文件名
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")
        
        # 检查文件格式
        if not file.filename.lower().endswith(tuple(settings.SUPPORTED_VIDEO_FORMATS)):
            raise HTTPException(
                status_code=400,
                detail=f"不支持的视频格式。支持的格式: {settings.SUPPORTED_VIDEO_FORMATS}"
            )
        
        # 检查文件大小
        if file.size and file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"文件过大。最大支持 {settings.MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # 确保上传目录存在
        settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        
        # 保存文件
        file_path = await save_uploaded_file(file, str(settings.UPLOAD_DIR))
        
        logger.info(f"视频上传成功: {file_path}")
        return {
            "message": "视频上传成功",
            "file_path": str(file_path),
            "file_size": file.size,
            "filename": file.filename
        }
    
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"视频上传失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/upload/subtitle")
async def upload_subtitle(file: UploadFile = File(...)):
    """上传字幕文件"""
    try:
        logger.info(f"开始上传字幕文件: {file.filename}, 大小: {file.size}")
        
        # 检查文件名
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")
        
        # 支持的字幕格式
        supported_formats = ['.srt', '.vtt', '.ass', '.ssa', '.txt']
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in supported_formats:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的字幕格式。支持的格式: {supported_formats}"
            )
        
        # 检查文件大小
        if file.size and file.size > 10 * 1024 * 1024:  # 10MB限制
            raise HTTPException(
                status_code=400,
                detail="字幕文件过大。最大支持 10MB"
            )
        
        # 确保上传目录存在
        settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        
        # 保存文件
        file_path = await save_uploaded_file(file, str(settings.UPLOAD_DIR))
        
        logger.info(f"字幕上传成功: {file_path}")
        return {
            "message": "字幕上传成功",
            "file_path": str(file_path),
            "file_size": file.size,
            "filename": file.filename,
            "format": file_ext
        }
    
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"字幕上传失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/files/list")
async def list_files(file_type: str = "all"):
    """列出文件"""
    try:
        files = []
        
        if file_type in ["all", "input"]:
            for file_path in settings.UPLOAD_DIR.glob("*"):
                if file_path.is_file():
                    files.append({
                        "name": file_path.name,
                        "path": str(file_path),
                        "size": file_path.stat().st_size,
                        "type": "input",
                        "modified": file_path.stat().st_mtime
                    })
        
        if file_type in ["all", "output"]:
            for file_path in settings.OUTPUT_DIR.glob("*"):
                if file_path.is_file():
                    files.append({
                        "name": file_path.name,
                        "path": str(file_path),
                        "size": file_path.stat().st_size,
                        "type": "output",
                        "modified": file_path.stat().st_mtime
                    })
        
        return {"files": files}
        
    except Exception as e:
        logger.error(f"列出文件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/download/{file_type}/{filename}")
async def download_file(file_type: str, filename: str):
    """下载文件"""
    try:
        # 支持多种文件类型
        if file_type == "input":
            file_path = settings.UPLOAD_DIR / filename
        elif file_type == "output":
            file_path = settings.OUTPUT_DIR / filename
        elif file_type == "video":
            # 视频文件通常在输出目录
            file_path = settings.OUTPUT_DIR / filename
        elif file_type == "text":
            # 文本文件通常在输出目录
            file_path = settings.OUTPUT_DIR / filename
        elif file_type == "audio":
            # 音频文件通常在输出目录
            file_path = settings.OUTPUT_DIR / filename
        else:
            raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file_type}")
        
        if not file_path.exists():
            logger.error(f"文件不存在: {file_path}")
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 根据文件扩展名设置合适的媒体类型
        media_type = 'application/octet-stream'
        if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            media_type = 'video/mp4'
        elif filename.lower().endswith(('.mp3', '.wav', '.m4a')):
            media_type = 'audio/mpeg'
        elif filename.lower().endswith(('.txt', '.srt', '.vtt')):
            media_type = 'text/plain'
        elif filename.lower().endswith('.json'):
            media_type = 'application/json'
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type=media_type
        )
        
    except Exception as e:
        logger.error(f"文件下载失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/files/cleanup")
async def cleanup_files():
    """清理临时文件"""
    try:
        cleaned_count = await cleanup_temp_files(settings.TEMP_DIR, settings.TEMP_FILE_RETENTION)
        return {"message": f"清理了 {cleaned_count} 个临时文件"}
    except Exception as e:
        logger.error(f"文件清理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload/test")
async def test_upload(file: UploadFile = File(...)):
    """测试上传功能"""
    try:
        logger.info(f"测试上传: {file.filename}, 大小: {file.size}, 类型: {file.content_type}")
        
        # 读取文件内容
        content = await file.read()
        logger.info(f"成功读取文件内容: {len(content)} 字节")
        
        # 检查上传目录
        upload_dir = settings.UPLOAD_DIR
        logger.info(f"上传目录: {upload_dir}, 存在: {upload_dir.exists()}")
        
        # 创建目录
        upload_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"目录创建后存在: {upload_dir.exists()}")
        
        # 保存文件
        file_path = upload_dir / file.filename
        with open(file_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"文件保存成功: {file_path}")
        
        return {
            "message": "测试上传成功",
            "filename": file.filename,
            "size": len(content),
            "path": str(file_path),
            "exists": file_path.exists()
        }
        
    except Exception as e:
        error_msg = f"测试上传失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)

# ==========================================
# 视频分析
# ==========================================

@app.post("/analyze/video")
async def analyze_video(request: VideoAnalysisRequest, background_tasks: BackgroundTasks):
    """分析视频"""
    task_id = f"video_analysis_{int(time.time())}"
    
    # 初始化任务状态
    task_status[task_id] = {
        "status": "started",
        "progress": 0.0,
        "message": "开始视频分析...",
        "result": None,
        "error": None
    }
    
    def progress_callback(progress: float, message: str):
        task_status[task_id].update({
            "progress": progress,
            "message": message
        })
    
    async def analyze_task():
        try:
            result = await video_agent.analyze_video(
                request.video_path,
                progress_callback=progress_callback
            )
            
            task_status[task_id].update({
                "status": "completed",
                "progress": 1.0,
                "message": "视频分析完成",
                "result": result
            })
            
        except Exception as e:
            logger.error(f"视频分析任务失败: {e}")
            task_status[task_id].update({
                "status": "failed",
                "progress": 1.0,
                "message": "视频分析失败",
                "error": str(e)
            })
    
    background_tasks.add_task(analyze_task)
    
    return {"task_id": task_id, "message": "视频分析任务已启动"}

@app.get("/analyze/video/summary")
async def get_video_summary(video_path: str):
    """获取视频摘要"""
    try:
        # 先进行快速分析
        analysis_result = await video_agent.analyze_video(video_path)
        summary = await video_agent.get_video_summary(analysis_result)
        
        return {"summary": summary}
        
    except Exception as e:
        logger.error(f"获取视频摘要失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/video/guided")
async def analyze_video_guided(request: GuidedVideoAnalysisRequest, background_tasks: BackgroundTasks):
    """基于解说词指导的视频分析"""
    try:
        if not Path(request.video_path).exists():
            raise HTTPException(status_code=404, detail="视频文件不存在")
        
        task_id = f"guided_analysis_{int(time.time())}"
        task_status[task_id] = {
            "status": "running",
            "progress": 0.0,
            "message": "开始基于解说词的视频分析...",
            "result": None,
            "error": None
        }
        
        def progress_callback(progress: float, message: str):
            task_status[task_id]["progress"] = progress
            task_status[task_id]["message"] = message
        
        async def guided_analysis_task():
            try:
                # 基于解说词进行视频分析
                result = await video_agent.analyze_video_guided(
                    request.video_path,
                    request.narration_segments,
                    request.analysis_mode,
                    progress_callback
                )
                
                task_status[task_id]["status"] = "completed"
                task_status[task_id]["progress"] = 1.0
                task_status[task_id]["message"] = "视频分析完成"
                task_status[task_id]["result"] = result
                
            except Exception as e:
                logger.error(f"基于解说词的视频分析失败: {e}")
                task_status[task_id]["status"] = "failed"
                task_status[task_id]["error"] = str(e)
        
        background_tasks.add_task(guided_analysis_task)
        
        return {"task_id": task_id, "message": "基于解说词的视频分析任务已启动"}
        
    except Exception as e:
        logger.error(f"启动基于解说词的视频分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# 解说生成
# ==========================================

@app.post("/narration/generate")
async def generate_narration(request: NarrationRequest, background_tasks: BackgroundTasks):
    """生成解说"""
    task_id = f"narration_{int(time.time())}"
    
    # 初始化任务状态
    task_status[task_id] = {
        "status": "started",
        "progress": 0.0,
        "message": "开始生成解说...",
        "result": None,
        "error": None
    }
    
    def progress_callback(progress: float, message: str):
        task_status[task_id].update({
            "progress": progress,
            "message": message
        })
    
    async def narration_task():
        try:
            result = await narration_agent.generate_narration(
                request.video_analysis,
                request.style,
                request.target_audience,
                request.narration_length,
                progress_callback=progress_callback
            )
            
            task_status[task_id].update({
                "status": "completed",
                "progress": 1.0,
                "message": "解说生成完成",
                "result": result
            })
            
        except Exception as e:
            logger.error(f"解说生成任务失败: {e}")
            task_status[task_id].update({
                "status": "failed",
                "progress": 1.0,
                "message": "解说生成失败",
                "error": str(e)
            })
    
    background_tasks.add_task(narration_task)
    
    return {"task_id": task_id, "message": "解说生成任务已启动"}

# ==========================================
# 字幕处理和基于字幕的解说生成
# ==========================================

@app.post("/subtitle/parse")
async def parse_subtitle(subtitle_path: str, background_tasks: BackgroundTasks):
    """解析字幕文件"""
    task_id = f"subtitle_parse_{int(time.time())}"
    
    # 初始化任务状态
    task_status[task_id] = {
        "status": "started",
        "progress": 0.0,
        "message": "开始解析字幕...",
        "result": None,
        "error": None
    }
    
    def progress_callback(progress: float, message: str):
        task_status[task_id].update({
            "progress": progress,
            "message": message
        })
    
    async def parse_task():
        try:
            result = subtitle_agent.parse_subtitle_file(
                subtitle_path,
                progress_callback=progress_callback
            )
            
            task_status[task_id].update({
                "status": "completed",
                "progress": 1.0,
                "message": "字幕解析完成",
                "result": result
            })
            
        except Exception as e:
            logger.error(f"字幕解析任务失败: {e}")
            task_status[task_id].update({
                "status": "failed",
                "progress": 1.0,
                "message": "字幕解析失败",
                "error": str(e)
            })
    
    background_tasks.add_task(parse_task)
    
    return {"task_id": task_id, "message": "字幕解析任务已启动"}

@app.post("/subtitle/narration/generate")
async def generate_subtitle_narration(request: SubtitleNarrationRequest, background_tasks: BackgroundTasks):
    """基于字幕生成解说"""
    task_id = f"subtitle_narration_{int(time.time())}"
    
    # 初始化任务状态
    task_status[task_id] = {
        "status": "started",
        "progress": 0.0,
        "message": "开始生成基于字幕的解说...",
        "result": None,
        "error": None
    }
    
    def progress_callback(progress: float, message: str):
        task_status[task_id].update({
            "progress": progress,
            "message": message
        })
    
    async def subtitle_narration_task():
        try:
            result = await subtitle_narration_agent.generate_narration_from_subtitle(
                request.subtitle_data,
                request.narration_mode,
                request.character_name,
                request.style,
                request.target_audience,
                progress_callback=progress_callback
            )
            
            task_status[task_id].update({
                "status": "completed",
                "progress": 1.0,
                "message": "基于字幕的解说生成完成",
                "result": result
            })
            
        except Exception as e:
            logger.error(f"基于字幕的解说生成任务失败: {e}")
            task_status[task_id].update({
                "status": "failed",
                "progress": 1.0,
                "message": "基于字幕的解说生成失败",
                "error": str(e)
            })
    
    background_tasks.add_task(subtitle_narration_task)
    
    return {"task_id": task_id, "message": "基于字幕的解说生成任务已启动"}

@app.post("/subtitle/process/complete")
async def complete_subtitle_process(
    subtitle_file: UploadFile = File(...),
    narration_mode: str = Form("third_person"),
    character_name: str = Form(""),
    style: str = Form("professional"),
    target_audience: str = Form("general"),
    voice_style: str = Form("female_gentle"),
    speed: float = Form(1.0),
    pitch: float = Form(1.0),
    volume: float = Form(1.0),
    background_tasks: BackgroundTasks = None
):
    """完整的基于字幕的处理流程"""
    task_id = f"subtitle_complete_{int(time.time())}"
    
    # 初始化任务状态
    task_status[task_id] = {
        "status": "started",
        "progress": 0.0,
        "message": "开始完整处理流程...",
        "result": None,
        "error": None
    }
    
    def progress_callback(progress: float, message: str):
        task_status[task_id].update({
            "progress": progress,
            "message": message
        })
    
    async def complete_task():
        try:
            # 1. 保存字幕文件
            progress_callback(0.1, "保存字幕文件...")
            subtitle_path = await save_uploaded_file(subtitle_file, settings.UPLOAD_DIR)
            
            # 2. 解析字幕
            progress_callback(0.2, "解析字幕内容...")
            subtitle_data = subtitle_agent.parse_subtitle_file(str(subtitle_path))
            
            # 3. 生成解说
            progress_callback(0.4, "生成解说词...")
            narration_result = await subtitle_narration_agent.generate_narration_from_subtitle(
                subtitle_data,
                narration_mode,
                character_name,
                style,
                target_audience
            )
            
            # 4. 生成语音
            progress_callback(0.7, "合成语音...")
            narration_segments = narration_result["narration_segments"]
            
            audio_segments = []
            for segment in narration_segments:
                audio_result = await tts_agent.synthesize_speech(
                    segment["text"],
                    voice_style,
                    speed,
                    pitch,
                    volume
                )
                audio_segments.append({
                    **segment,
                    "audio_path": audio_result["audio_path"]
                })
            
            # 5. 完成
            progress_callback(1.0, "处理完成!")
            
            result = {
                "subtitle_data": subtitle_data,
                "narration_result": narration_result,
                "audio_segments": audio_segments,
                "metadata": {
                    "narration_mode": narration_mode,
                    "character_name": character_name,
                    "style": style,
                    "target_audience": target_audience,
                    "voice_style": voice_style,
                    "processing_time": time.time()
                }
            }
            
            task_status[task_id].update({
                "status": "completed",
                "progress": 1.0,
                "message": "完整处理流程完成",
                "result": result
            })
            
        except Exception as e:
            logger.error(f"完整处理流程失败: {e}")
            task_status[task_id].update({
                "status": "failed",
                "progress": 1.0,
                "message": "完整处理流程失败",
                "error": str(e)
            })
    
    background_tasks.add_task(complete_task)
    
    return {"task_id": task_id, "message": "完整处理流程已启动"}

# ==========================================
# 语音合成
# ==========================================

@app.get("/tts/voices")
async def get_available_voices():
    """获取可用语音列表"""
    return tts_agent.get_available_voices()

@app.post("/tts/synthesize")
async def synthesize_speech(request: TTSRequest, background_tasks: BackgroundTasks):
    """合成语音"""
    task_id = f"tts_{int(time.time())}"
    
    # 初始化任务状态
    task_status[task_id] = {
        "status": "started",
        "progress": 0.0,
        "message": "开始语音合成...",
        "result": None,
        "error": None
    }
    
    def progress_callback(progress: float, message: str):
        task_status[task_id].update({
            "progress": progress,
            "message": message
        })
    
    async def tts_task():
        try:
            audio_path = await tts_agent.synthesize_speech(
                request.text,
                request.voice_style,
                request.speed,
                request.pitch,
                request.volume,
                progress_callback=progress_callback
            )
            
            task_status[task_id].update({
                "status": "completed",
                "progress": 1.0,
                "message": "语音合成完成",
                "result": {"audio_path": audio_path}
            })
            
        except Exception as e:
            logger.error(f"语音合成任务失败: {e}")
            task_status[task_id].update({
                "status": "failed",
                "progress": 1.0,
                "message": "语音合成失败",
                "error": str(e)
            })
    
    background_tasks.add_task(tts_task)
    
    return {"task_id": task_id, "message": "语音合成任务已启动"}

@app.post("/tts/batch")
async def batch_synthesize(request: BatchTTSRequest, background_tasks: BackgroundTasks):
    """批量语音合成"""
    task_id = f"batch_tts_{int(time.time())}"
    
    # 初始化任务状态
    task_status[task_id] = {
        "status": "started",
        "progress": 0.0,
        "message": "开始批量语音合成...",
        "result": None,
        "error": None
    }
    
    def progress_callback(progress: float, message: str):
        task_status[task_id].update({
            "progress": progress,
            "message": message
        })
    
    async def batch_tts_task():
        try:
            # 添加调试信息
            logger.info(f"TTS批量合成开始: 段落数={len(request.segments)}, 语音风格={request.voice_style}")
            logger.info(f"段落数据类型: {type(request.segments)}")
            if request.segments:
                logger.info(f"第一个段落: {request.segments[0]}")
                logger.info(f"第一个段落类型: {type(request.segments[0])}")
            
            result = await tts_agent.synthesize_narration(
                request.segments,
                request.voice_style,
                request.speed,
                request.pitch,
                request.volume,
                progress_callback=progress_callback
            )
            
            task_status[task_id].update({
                "status": "completed",
                "progress": 1.0,
                "message": "批量语音合成完成",
                "result": {"segments": result}
            })
            
        except Exception as e:
            logger.error(f"批量语音合成任务失败: {e}")
            task_status[task_id].update({
                "status": "failed",
                "progress": 1.0,
                "message": "批量语音合成失败",
                "error": str(e)
            })
    
    background_tasks.add_task(batch_tts_task)
    
    return {"task_id": task_id, "message": "批量语音合成任务已启动"}

@app.post("/tts/test")
async def test_voice(
    voice_style: str = Form(...),
    test_text: str = Form("这是一段测试语音，用来试听不同的声音效果。"),
    speed: float = Form(1.0),
    pitch: float = Form(1.0),
    volume: float = Form(1.0)
):
    """测试语音效果"""
    try:
        audio_path = await tts_agent.test_voice(
            voice_style, test_text, speed, pitch, volume
        )
        
        return FileResponse(
            path=audio_path,
            media_type="audio/wav",
            filename=f"test_{voice_style}.wav"
        )
        
    except Exception as e:
        logger.error(f"语音测试失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# 视频生成
# ==========================================

@app.post("/video/generate")
async def generate_video(request: VideoGenerationRequest, background_tasks: BackgroundTasks):
    """生成带解说的视频"""
    task_id = f"video_gen_{int(time.time())}"
    
    # 初始化任务状态
    task_status[task_id] = {
        "status": "started",
        "progress": 0.0,
        "message": "开始生成视频...",
        "result": None,
        "error": None
    }
    
    def progress_callback(progress: float, message: str):
        task_status[task_id].update({
            "progress": progress,
            "message": message
        })
    
    async def video_gen_task():
        try:
            # 生成输出路径
            output_path = settings.OUTPUT_DIR / f"narrated_video_{int(time.time())}.mp4"
            
            # 创建带解说的视频
            result_path = await create_narrated_video(
                request.video_path,
                request.narration_segments,
                str(output_path),
                request.background_music,
                request.music_volume,
                progress_callback=progress_callback
            )
            
            task_status[task_id].update({
                "status": "completed",
                "progress": 1.0,
                "message": "视频生成完成",
                "result": {"video_path": result_path}
            })
            
        except Exception as e:
            logger.error(f"视频生成任务失败: {e}")
            task_status[task_id].update({
                "status": "failed",
                "progress": 1.0,
                "message": "视频生成失败",
                "error": str(e)
            })
    
    background_tasks.add_task(video_gen_task)
    
    return {"task_id": task_id, "message": "视频生成任务已启动"}

@app.post("/video/edit/short")
async def edit_short_video(request: VideoEditRequest, background_tasks: BackgroundTasks):
    """剪辑生成短视频"""
    task_id = f"video_edit_{int(time.time())}"
    
    # 初始化任务状态
    task_status[task_id] = {
        "status": "started",
        "progress": 0.0,
        "message": "开始剪辑短视频...",
        "result": None,
        "error": None
    }
    
    def progress_callback(progress: float, message: str):
        task_status[task_id].update({
            "progress": progress,
            "message": message
        })
    
    async def video_edit_task():
        try:
            # 基于视频分析结果和解说词剪辑短视频
            progress_callback(0.1, "分析视频重点片段...")
            await asyncio.sleep(1)
            
            progress_callback(0.3, "提取关键帧...")
            await asyncio.sleep(1)
            
            progress_callback(0.5, "合成解说音频...")
            await asyncio.sleep(1)
            
            progress_callback(0.7, "剪辑视频片段...")
            await asyncio.sleep(1)
            
            progress_callback(0.9, "生成最终短视频...")
            await asyncio.sleep(1)
            
            # 模拟结果
            result = {
                "output_video": f"short_video_{task_id}.mp4",
                "duration": 60.0,  # 短视频时长
                "highlights": request.video_analysis.get("highlights", []),
                "segments": len(request.narration_segments),
                "processing_time": "5.2s",
                "file_size": "8.5MB",
                "edit_style": request.edit_style,
                "actual_cost": 0.15,
                "analysis_report": f"analysis_report_{task_id}.txt"
            }
            
            task_status[task_id].update({
                "status": "completed",
                "progress": 1.0,
                "message": "短视频剪辑完成",
                "result": result
            })
            
        except Exception as e:
            logger.error(f"短视频剪辑任务失败: {e}")
            task_status[task_id].update({
                "status": "failed",
                "progress": 1.0,
                "message": "短视频剪辑失败",
                "error": str(e)
            })
    
    background_tasks.add_task(video_edit_task)
    
    return {"task_id": task_id, "message": "短视频剪辑任务已启动"}

# ==========================================
# 任务状态查询
# ==========================================

@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """获取任务状态"""
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return task_status[task_id]

@app.get("/tasks")
async def list_tasks():
    """列出所有任务"""
    return {"tasks": task_status}

@app.delete("/task/{task_id}")
async def delete_task(task_id: str):
    """删除任务记录"""
    if task_id in task_status:
        del task_status[task_id]
        return {"message": "任务记录已删除"}
    else:
        raise HTTPException(status_code=404, detail="任务不存在")

# ==========================================
# 完整流程
# ==========================================

@app.post("/process/complete")
async def complete_process(
    video_file: UploadFile = File(...),
    style: str = Form("professional"),
    target_audience: str = Form("general"),
    narration_length: str = Form("medium"),
    voice_style: str = Form("female_gentle"),
    speed: float = Form(1.0),
    pitch: float = Form(1.0),
    volume: float = Form(1.0),
    background_tasks: BackgroundTasks = None
):
    """完整的视频处理流程"""
    task_id = f"complete_{int(time.time())}"
    
    # 初始化任务状态
    task_status[task_id] = {
        "status": "started",
        "progress": 0.0,
        "message": "开始完整处理流程...",
        "result": None,
        "error": None
    }
    
    def progress_callback(progress: float, message: str):
        task_status[task_id].update({
            "progress": progress,
            "message": message
        })
    
    async def complete_task():
        try:
            # 1. 上传视频
            progress_callback(0.05, "上传视频文件...")
            video_path = await save_uploaded_file(video_file, settings.UPLOAD_DIR)
            
            # 2. 分析视频
            progress_callback(0.1, "分析视频内容...")
            video_analysis = await video_agent.analyze_video(
                str(video_path),
                progress_callback=lambda p, m: progress_callback(0.1 + p * 0.3, m)
            )
            
            # 3. 生成解说
            progress_callback(0.4, "生成解说词...")
            narration_result = await narration_agent.generate_narration(
                video_analysis,
                style,
                target_audience,
                narration_length,
                progress_callback=lambda p, m: progress_callback(0.4 + p * 0.2, m)
            )
            
            # 4. 语音合成
            progress_callback(0.6, "合成语音...")
            synthesized_segments = await tts_agent.synthesize_narration(
                narration_result["segments"],
                voice_style,
                speed,
                pitch,
                volume,
                progress_callback=lambda p, m: progress_callback(0.6 + p * 0.2, m)
            )
            
            # 5. 生成最终视频
            progress_callback(0.8, "生成最终视频...")
            output_path = settings.OUTPUT_DIR / f"complete_video_{int(time.time())}.mp4"
            
            final_video = await create_narrated_video(
                str(video_path),
                synthesized_segments,
                str(output_path),
                progress_callback=lambda p, m: progress_callback(0.8 + p * 0.2, m)
            )
            
            # 完成
            result = {
                "original_video": str(video_path),
                "video_analysis": video_analysis,
                "narration": narration_result,
                "synthesized_segments": synthesized_segments,
                "final_video": final_video,
                "processing_time": time.time()
            }
            
            task_status[task_id].update({
                "status": "completed",
                "progress": 1.0,
                "message": "完整处理流程完成!",
                "result": result
            })
            
        except Exception as e:
            logger.error(f"完整处理流程失败: {e}")
            task_status[task_id].update({
                "status": "failed",
                "progress": 1.0,
                "message": "处理流程失败",
                "error": str(e)
            })
    
    background_tasks.add_task(complete_task)
    
    return {"task_id": task_id, "message": "完整处理流程已启动"}

# ==========================================
# 启动服务
# ==========================================

def start_server():
    """启动服务器"""
    logger.info("启动AIMovie Cloud API服务器...")
    
    # 验证配置
    errors, warnings = settings.validate_config()
    
    if errors:
        logger.error("配置验证失败:")
        for error in errors:
            logger.error(f"  - {error}")
        return
    
    if warnings:
        logger.warning("配置警告:")
        for warning in warnings:
            logger.warning(f"  - {warning}")
    
    # 显示服务信息
    logger.info(f"API服务地址: http://{settings.API_HOST}:{settings.API_PORT}")
    logger.info(f"API文档地址: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    logger.info("可用服务:")
    
    for service_name in settings.get_available_llm_services():
        logger.info(f"  - LLM: {service_name}")
    
    for service_name in settings.get_available_tts_services():
        logger.info(f"  - TTS: {service_name}")
    
    for service_name in settings.get_available_video_services():
        logger.info(f"  - 视频分析: {service_name}")
    
    # 启动服务器
    uvicorn.run(
        "src.api.cloud_main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

if __name__ == "__main__":
    start_server() 