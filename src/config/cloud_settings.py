import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class CloudSettings:
    """云端API配置"""
    
    # 基础配置
    ENVIRONMENT = "cloud"
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # 路径配置
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    UPLOAD_DIR = DATA_DIR / "input"
    OUTPUT_DIR = DATA_DIR / "output"
    TEMP_DIR = DATA_DIR / "temp"
    LOGS_DIR = BASE_DIR / "logs"
    
    # 确保目录存在
    for dir_path in [DATA_DIR, UPLOAD_DIR, OUTPUT_DIR, TEMP_DIR, LOGS_DIR]:
        dir_path.mkdir(exist_ok=True)
    
    # 服务配置
    API_HOST = os.getenv("API_HOST", "127.0.0.1")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))
    API_BASE_URL = os.getenv("API_BASE_URL", f"http://{API_HOST}:{API_PORT}")
    
    # ==========================================
    # 云端API配置 - 高性价比组合
    # ==========================================
    
    # 通义千问 (阿里云) - 解说生成主力
    QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
    QWEN_BASE_URL = "https://dashscope.aliyuncs.com/api/v1"
    QWEN_MODEL = "qwen-turbo"  # 性价比最高
    
    # 文心一言 (百度) - 解说生成备用
    ERNIE_API_KEY = os.getenv("ERNIE_API_KEY", "")
    ERNIE_SECRET_KEY = os.getenv("ERNIE_SECRET_KEY", "")
    ERNIE_MODEL = "ernie-3.5-8k"  # 性价比版本
    
    # 阿里云语音合成 - TTS主力
    ALIYUN_ACCESS_KEY_ID = os.getenv("ALIYUN_ACCESS_KEY_ID", "")
    ALIYUN_ACCESS_KEY_SECRET = os.getenv("ALIYUN_ACCESS_KEY_SECRET", "")
    ALIYUN_TTS_REGION = os.getenv("ALIYUN_TTS_REGION", "cn-shanghai")
    
    # 腾讯云TTS - TTS备用
    TENCENT_SECRET_ID = os.getenv("TENCENT_SECRET_ID", "")
    TENCENT_SECRET_KEY = os.getenv("TENCENT_SECRET_KEY", "")
    TENCENT_TTS_REGION = os.getenv("TENCENT_TTS_REGION", "ap-beijing")
    
    # 百度AI - 视频分析
    BAIDU_API_KEY = os.getenv("BAIDU_API_KEY", "")
    BAIDU_SECRET_KEY = os.getenv("BAIDU_SECRET_KEY", "")
    
    # 通义千问-VL - 图像理解
    QWEN_VL_API_KEY = os.getenv("QWEN_VL_API_KEY", "")  # 可与QWEN_API_KEY相同
    
    # OpenAI - 高端备用方案
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    # ==========================================
    # 服务优先级配置
    # ==========================================
    
    # 解说生成服务优先级 (按性价比排序)
    LLM_SERVICES = [
        {
            "name": "qwen",
            "display_name": "通义千问",
            "cost_per_1k": 0.0008,  # 元/1K tokens
            "enabled": bool(QWEN_API_KEY)
        },
        {
            "name": "ernie",
            "display_name": "文心一言", 
            "cost_per_1k": 0.0012,
            "enabled": bool(ERNIE_API_KEY and ERNIE_SECRET_KEY)
        },
        {
            "name": "openai",
            "display_name": "GPT-3.5",
            "cost_per_1k": 0.002,
            "enabled": bool(OPENAI_API_KEY)
        }
    ]
    
    # TTS服务优先级
    TTS_SERVICES = [
        {
            "name": "aliyun",
            "display_name": "阿里云TTS",
            "cost_per_char": 0.00002,  # 元/字符
            "enabled": bool(ALIYUN_ACCESS_KEY_ID and ALIYUN_ACCESS_KEY_SECRET)
        },
        {
            "name": "tencent", 
            "display_name": "腾讯云TTS",
            "cost_per_char": 0.00003,
            "enabled": bool(TENCENT_SECRET_ID and TENCENT_SECRET_KEY)
        },
        {
            "name": "edge",
            "display_name": "Edge-TTS",
            "cost_per_char": 0,  # 免费
            "enabled": True
        }
    ]
    
    # 视频分析服务
    VIDEO_ANALYSIS_SERVICES = [
        {
            "name": "baidu",
            "display_name": "百度AI",
            "cost_per_image": 0.002,
            "enabled": bool(BAIDU_API_KEY and BAIDU_SECRET_KEY)
        },
        {
            "name": "qwen_vl",
            "display_name": "通义千问-VL", 
            "cost_per_image": 0.001,
            "enabled": bool(QWEN_VL_API_KEY)
        }
    ]
    
    # ==========================================
    # 处理配置
    # ==========================================
    
    # 文件配置
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "500")) * 1024 * 1024
    TEMP_FILE_RETENTION = int(os.getenv("TEMP_FILE_RETENTION", "24"))
    OUTPUT_QUALITY = os.getenv("OUTPUT_QUALITY", "medium")
    
    # 视频处理配置
    DEFAULT_FPS = 24
    DEFAULT_RESOLUTION = (854, 480)
    MAX_VIDEO_DURATION = 600
    
    # 采样配置 (云端优化)
    FRAME_SAMPLE_INTERVAL = 3  # 每3秒采样一帧
    MAX_FRAMES_PER_VIDEO = 50  # 最多分析50帧
    
    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = LOGS_DIR / "aimovie_cloud.log"
    
    # CORS配置
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # 支持的文件格式
    SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
    SUPPORTED_AUDIO_FORMATS = ['.wav', '.mp3', '.aac', '.m4a']
    
    @classmethod
    def get_available_llm_services(cls):
        """获取可用的LLM服务"""
        return [service for service in cls.LLM_SERVICES if service["enabled"]]
    
    @classmethod
    def get_available_tts_services(cls):
        """获取可用的TTS服务"""
        return [service for service in cls.TTS_SERVICES if service["enabled"]]
    
    @classmethod
    def get_available_video_services(cls):
        """获取可用的视频分析服务"""
        return [service for service in cls.VIDEO_ANALYSIS_SERVICES if service["enabled"]]
    
    @classmethod
    def get_primary_llm_service(cls):
        """获取主要LLM服务"""
        available = cls.get_available_llm_services()
        return available[0] if available else None
    
    @classmethod
    def get_primary_tts_service(cls):
        """获取主要TTS服务"""
        available = cls.get_available_tts_services()
        return available[0] if available else None
    
    @classmethod
    def get_primary_video_service(cls):
        """获取主要视频分析服务"""
        available = cls.get_available_video_services()
        return available[0] if available else None
    
    @classmethod
    def estimate_cost(cls, text_length: int, audio_length: int, frame_count: int):
        """估算处理成本"""
        cost = 0
        
        # LLM成本 (按token估算，中文约1.5字符/token)
        llm_service = cls.get_primary_llm_service()
        if llm_service:
            tokens = text_length / 1.5
            cost += (tokens / 1000) * llm_service["cost_per_1k"]
        
        # TTS成本
        tts_service = cls.get_primary_tts_service()
        if tts_service:
            cost += audio_length * tts_service["cost_per_char"]
        
        # 视频分析成本
        video_service = cls.get_primary_video_service()
        if video_service:
            cost += frame_count * video_service["cost_per_image"]
        
        return round(cost, 4)
    
    @classmethod
    def validate_config(cls):
        """验证配置"""
        errors = []
        warnings = []
        
        # 检查至少有一个LLM服务可用
        if not cls.get_available_llm_services():
            errors.append("没有可用的LLM服务，请配置至少一个API密钥")
        
        # 检查至少有一个TTS服务可用
        if not cls.get_available_tts_services():
            warnings.append("没有配置云端TTS服务，将使用Edge-TTS")
        
        # 检查视频分析服务
        if not cls.get_available_video_services():
            warnings.append("没有配置云端视频分析服务，将使用基础分析")
        
        # 检查目录权限
        for dir_name, dir_path in [
            ("数据目录", cls.DATA_DIR),
            ("上传目录", cls.UPLOAD_DIR),
            ("输出目录", cls.OUTPUT_DIR),
            ("临时目录", cls.TEMP_DIR),
            ("日志目录", cls.LOGS_DIR)
        ]:
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    errors.append(f"无法创建{dir_name}: {e}")
            elif not os.access(dir_path, os.W_OK):
                errors.append(f"{dir_name}无写入权限: {dir_path}")
        
        return errors, warnings
    
    @classmethod
    def get_config(cls):
        """获取配置字典"""
        return {
            "environment": cls.ENVIRONMENT,
            "debug": cls.DEBUG,
            "api_host": cls.API_HOST,
            "api_port": cls.API_PORT,
            "streamlit_port": cls.STREAMLIT_PORT,
            "services": {
                "llm": cls.get_available_llm_services(),
                "tts": cls.get_available_tts_services(),
                "video": cls.get_available_video_services()
            },
            "limits": {
                "max_file_size_mb": cls.MAX_FILE_SIZE // (1024 * 1024),
                "max_video_duration": cls.MAX_VIDEO_DURATION,
                "temp_retention_hours": cls.TEMP_FILE_RETENTION,
                "max_frames": cls.MAX_FRAMES_PER_VIDEO
            },
            "processing": {
                "frame_interval": cls.FRAME_SAMPLE_INTERVAL,
                "default_fps": cls.DEFAULT_FPS,
                "default_resolution": cls.DEFAULT_RESOLUTION
            }
        }

settings = CloudSettings()