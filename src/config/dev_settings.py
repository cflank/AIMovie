"""
开发环境配置
云端版本 - 基于API服务
"""

import os
import warnings
from pathlib import Path
from typing import List, Tuple, Dict, Any

# 基础路径配置
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
TEMP_DIR = DATA_DIR / "temp"
LOGS_DIR = BASE_DIR / "logs"

# 确保目录存在
for dir_path in [DATA_DIR, UPLOAD_DIR, OUTPUT_DIR, TEMP_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

class CloudSettings:
    """云端配置类"""
    
    # 基础配置
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # API服务配置
    API_HOST = os.getenv("API_HOST", "127.0.0.1")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    
    # 文件配置
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "500"))  # MB
    ALLOWED_VIDEO_FORMATS = [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv"]
    TEMP_FILE_RETENTION = int(os.getenv("TEMP_FILE_RETENTION", "24"))  # 小时
    
    # 云端API配置
    # 通义千问 (主要LLM)
    QWEN_API_KEY = os.getenv("QWEN_API_KEY")
    QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-turbo")
    
    # 文心一言 (备用LLM)
    ERNIE_API_KEY = os.getenv("ERNIE_API_KEY")
    ERNIE_SECRET_KEY = os.getenv("ERNIE_SECRET_KEY")
    ERNIE_MODEL = os.getenv("ERNIE_MODEL", "ernie-3.5-8k")
    
    # OpenAI (高端备用)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # 阿里云TTS
    ALIYUN_ACCESS_KEY_ID = os.getenv("ALIYUN_ACCESS_KEY_ID")
    ALIYUN_ACCESS_KEY_SECRET = os.getenv("ALIYUN_ACCESS_KEY_SECRET")
    ALIYUN_TTS_REGION = os.getenv("ALIYUN_TTS_REGION", "cn-shanghai")
    
    # 腾讯云TTS (备用)
    TENCENT_SECRET_ID = os.getenv("TENCENT_SECRET_ID")
    TENCENT_SECRET_KEY = os.getenv("TENCENT_SECRET_KEY")
    TENCENT_TTS_REGION = os.getenv("TENCENT_TTS_REGION", "ap-beijing")
    
    # 百度AI
    BAIDU_API_KEY = os.getenv("BAIDU_API_KEY")
    BAIDU_SECRET_KEY = os.getenv("BAIDU_SECRET_KEY")
    
    # 通义千问-VL (图像理解)
    QWEN_VL_API_KEY = os.getenv("QWEN_VL_API_KEY")
    
    # TTS配置
    TTS_ENGINE = os.getenv("TTS_ENGINE", "edge-tts")  # edge-tts, aliyun, tencent
    TTS_VOICE = os.getenv("TTS_VOICE", "zh-CN-XiaoxiaoNeural")
    TTS_SPEED = float(os.getenv("TTS_SPEED", "1.0"))
    TTS_PITCH = float(os.getenv("TTS_PITCH", "1.0"))
    TTS_VOLUME = float(os.getenv("TTS_VOLUME", "1.0"))
    
    # 视频处理配置
    VIDEO_SAMPLE_INTERVAL = int(os.getenv("VIDEO_SAMPLE_INTERVAL", "3"))  # 秒
    MAX_FRAMES_PER_VIDEO = int(os.getenv("MAX_FRAMES_PER_VIDEO", "50"))
    OUTPUT_QUALITY = os.getenv("OUTPUT_QUALITY", "medium")  # low, medium, high
    
    # API调用配置
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "60"))  # 秒
    API_RETRY_TIMES = int(os.getenv("API_RETRY_TIMES", "3"))
    API_RATE_LIMIT = int(os.getenv("API_RATE_LIMIT", "10"))  # 每秒请求数
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        """获取配置字典"""
        return {
            "debug": cls.DEBUG,
            "log_level": cls.LOG_LEVEL,
            "api": {
                "host": cls.API_HOST,
                "port": cls.API_PORT,
                "timeout": cls.API_TIMEOUT,
                "retry_times": cls.API_RETRY_TIMES,
                "rate_limit": cls.API_RATE_LIMIT
            },
            "file": {
                "max_size_mb": cls.MAX_FILE_SIZE,
                "allowed_formats": cls.ALLOWED_VIDEO_FORMATS,
                "temp_retention_hours": cls.TEMP_FILE_RETENTION
            },
            "llm": {
                "qwen_configured": bool(cls.QWEN_API_KEY),
                "ernie_configured": bool(cls.ERNIE_API_KEY and cls.ERNIE_SECRET_KEY),
                "openai_configured": bool(cls.OPENAI_API_KEY)
            },
            "tts": {
                "engine": cls.TTS_ENGINE,
                "voice": cls.TTS_VOICE,
                "speed": cls.TTS_SPEED,
                "pitch": cls.TTS_PITCH,
                "volume": cls.TTS_VOLUME,
                "aliyun_configured": bool(cls.ALIYUN_ACCESS_KEY_ID and cls.ALIYUN_ACCESS_KEY_SECRET),
                "tencent_configured": bool(cls.TENCENT_SECRET_ID and cls.TENCENT_SECRET_KEY)
            },
            "video": {
                "sample_interval": cls.VIDEO_SAMPLE_INTERVAL,
                "max_frames": cls.MAX_FRAMES_PER_VIDEO,
                "output_quality": cls.OUTPUT_QUALITY
            },
            "ai_services": {
                "baidu_configured": bool(cls.BAIDU_API_KEY and cls.BAIDU_SECRET_KEY),
                "qwen_vl_configured": bool(cls.QWEN_VL_API_KEY)
            }
        }
    
    @classmethod
    def validate_config(cls) -> Tuple[List[str], List[str]]:
        """验证配置"""
        errors = []
        warnings = []
        
        # 检查LLM配置
        llm_services = [
            (cls.QWEN_API_KEY, "通义千问"),
            (cls.ERNIE_API_KEY and cls.ERNIE_SECRET_KEY, "文心一言"),
            (cls.OPENAI_API_KEY, "OpenAI")
        ]
        
        if not any(configured for configured, _ in llm_services):
            errors.append("未配置任何LLM服务API密钥")
        
        # 检查TTS配置
        if cls.TTS_ENGINE == "aliyun":
            if not (cls.ALIYUN_ACCESS_KEY_ID and cls.ALIYUN_ACCESS_KEY_SECRET):
                warnings.append("选择阿里云TTS但未配置密钥，将使用Edge-TTS")
        elif cls.TTS_ENGINE == "tencent":
            if not (cls.TENCENT_SECRET_ID and cls.TENCENT_SECRET_KEY):
                warnings.append("选择腾讯云TTS但未配置密钥，将使用Edge-TTS")
        
        # 检查文件大小限制
        if cls.MAX_FILE_SIZE > 1000:
            warnings.append(f"文件大小限制过大: {cls.MAX_FILE_SIZE}MB")
        
        # 检查视频处理参数
        if cls.MAX_FRAMES_PER_VIDEO > 100:
            warnings.append(f"最大帧数过多: {cls.MAX_FRAMES_PER_VIDEO}，可能增加处理成本")
        
        return errors, warnings
    
    @classmethod
    def get_available_services(cls) -> Dict[str, bool]:
        """获取可用服务列表"""
        return {
            "llm": {
                "qwen": bool(cls.QWEN_API_KEY),
                "ernie": bool(cls.ERNIE_API_KEY and cls.ERNIE_SECRET_KEY),
                "openai": bool(cls.OPENAI_API_KEY)
            },
            "tts": {
                "edge_tts": True,  # 总是可用
                "aliyun": bool(cls.ALIYUN_ACCESS_KEY_ID and cls.ALIYUN_ACCESS_KEY_SECRET),
                "tencent": bool(cls.TENCENT_SECRET_ID and cls.TENCENT_SECRET_KEY)
            },
            "vision": {
                "baidu": bool(cls.BAIDU_API_KEY and cls.BAIDU_SECRET_KEY),
                "qwen_vl": bool(cls.QWEN_VL_API_KEY)
            }
        }

# 创建全局设置实例
settings = CloudSettings()
