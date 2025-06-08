"""
云端服务配置管理
支持多种大模型组合和预设配置
"""

import os
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from .preset_configs import preset_manager, PresetType, PresetConfig


logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """服务状态"""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"


@dataclass
class ServiceInfo:
    """服务信息"""
    name: str
    status: ServiceStatus
    cost_per_unit: float
    unit: str
    priority: int
    last_used: Optional[str] = None
    error_count: int = 0
    rate_limit_reset: Optional[str] = None


@dataclass
class CostTracker:
    """成本跟踪器"""
    daily_cost: float = 0.0
    monthly_cost: float = 0.0
    total_cost: float = 0.0
    daily_limit: float = 50.0
    monthly_limit: float = 500.0
    single_video_limit: float = 5.0
    warning_threshold: float = 0.8


class CloudSettings:
    """云端服务配置管理器"""
    
    def __init__(self):
        self.preset_type = self._get_preset_type()
        self.preset_config = preset_manager.get_preset(self.preset_type)
        self.cost_tracker = CostTracker()
        self.service_status = {}
        self._load_settings()
        # 不在初始化时验证配置，避免在环境变量加载前输出错误信息
    
    def _parse_int_env(self, key: str, default: str) -> int:
        """解析整数环境变量，自动清理注释"""
        value = os.getenv(key, default)
        # 清理注释（# 后面的内容）
        if '#' in value:
            value = value.split('#')[0].strip()
        return int(value)
    
    def _parse_float_env(self, key: str, default: str) -> float:
        """解析浮点数环境变量，自动清理注释"""
        value = os.getenv(key, default)
        # 清理注释（# 后面的内容）
        if '#' in value:
            value = value.split('#')[0].strip()
        return float(value)
    
    def _get_preset_type(self) -> PresetType:
        """获取预设类型"""
        preset_name = os.getenv("PRESET_CONFIG", "cost_effective")
        try:
            return PresetType(preset_name)
        except ValueError:
            logger.warning(f"未知的预设配置: {preset_name}，使用默认配置")
            return PresetType.COST_EFFECTIVE
    
    def _load_settings(self):
        """加载配置"""
        # 基础配置
        self.api_host = os.getenv("API_HOST", "127.0.0.1")
        self.api_port = self._parse_int_env("API_PORT", "8000")
        self.streamlit_port = self._parse_int_env("STREAMLIT_PORT", "8501")
        
        # 处理配置（清理注释）
        self.max_file_size = self._parse_int_env("MAX_FILE_SIZE", "500")
        self.frame_sample_interval = self._parse_int_env("FRAME_SAMPLE_INTERVAL", "3")
        self.max_frames_per_video = self._parse_int_env("MAX_FRAMES_PER_VIDEO", "50")
        self.max_concurrent_tasks = self._parse_int_env("MAX_CONCURRENT_TASKS", "3")
        
        # 质量配置
        self.video_quality = os.getenv("VIDEO_QUALITY", "medium")
        self.audio_quality = os.getenv("AUDIO_QUALITY", "medium")
        self.output_format = os.getenv("OUTPUT_FORMAT", "mp4")
        
        # 超时配置
        self.api_timeout = self._parse_int_env("API_TIMEOUT", "60")
        self.llm_timeout = self._parse_int_env("LLM_TIMEOUT", "120")
        self.tts_timeout = self._parse_int_env("TTS_TIMEOUT", "180")
        self.vision_timeout = self._parse_int_env("VISION_TIMEOUT", "90")
        
        # 重试配置
        self.api_retry_times = self._parse_int_env("API_RETRY_TIMES", "3")
        self.retry_delay = self._parse_int_env("RETRY_DELAY", "1")
        
        # 并发控制
        self.max_concurrent_llm_requests = self._parse_int_env("MAX_CONCURRENT_LLM_REQUESTS", "5")
        self.max_concurrent_tts_requests = self._parse_int_env("MAX_CONCURRENT_TTS_REQUESTS", "3")
        self.max_concurrent_vision_requests = self._parse_int_env("MAX_CONCURRENT_VISION_REQUESTS", "2")
        
        # 成本控制
        self.cost_tracker.daily_limit = self._parse_float_env("DAILY_COST_LIMIT", "50.0")
        self.cost_tracker.monthly_limit = self._parse_float_env("MONTHLY_COST_LIMIT", "500.0")
        self.cost_tracker.single_video_limit = self._parse_float_env("SINGLE_VIDEO_COST_LIMIT", "5.0")
        self.cost_tracker.warning_threshold = self._parse_float_env("COST_WARNING_THRESHOLD", "0.8")
        
        # 日志配置
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_LEVEL = self.log_level  # 兼容大写访问
        self.log_file = os.getenv("LOG_FILE", "logs/aimovie_cloud.log")
        self.LOG_FILE = self.log_file  # 兼容大写访问
        
        # 缓存配置
        self.enable_cache = os.getenv("ENABLE_CACHE", "true").lower() == "true"
        self.cache_ttl = self._parse_int_env("CACHE_TTL", "3600")
        
        # 安全配置
        self.api_rate_limit = self._parse_int_env("API_RATE_LIMIT", "100")
        self.cors_origins = self._parse_cors_origins()
        
        # 监控配置
        self.enable_metrics = os.getenv("ENABLE_METRICS", "true").lower() == "true"
        self.metrics_port = self._parse_int_env("METRICS_PORT", "9090")
        self.health_check_interval = self._parse_int_env("HEALTH_CHECK_INTERVAL", "30")
        
        # 调试配置
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.enable_profiling = os.getenv("ENABLE_PROFILING", "false").lower() == "true"
        self.save_intermediate_files = os.getenv("SAVE_INTERMEDIATE_FILES", "false").lower() == "true"
        
        # API密钥配置
        self.QWEN_API_KEY = os.getenv("QWEN_API_KEY")
        self.QWEN_VL_API_KEY = os.getenv("QWEN_VL_API_KEY")
        self.QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-plus")
        self.BAIDU_API_KEY = os.getenv("BAIDU_API_KEY")
        self.BAIDU_SECRET_KEY = os.getenv("BAIDU_SECRET_KEY")
        self.ERNIE_API_KEY = os.getenv("ERNIE_API_KEY")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
        
        # 阿里云TTS配置
        self.ALIYUN_ACCESS_KEY_ID = os.getenv("ALIYUN_ACCESS_KEY_ID")
        self.ALIYUN_ACCESS_KEY_SECRET = os.getenv("ALIYUN_ACCESS_KEY_SECRET")
        self.ALIYUN_TTS_REGION = os.getenv("ALIYUN_TTS_REGION", "cn-shanghai")
        
        # 腾讯云TTS配置
        self.TENCENT_SECRET_ID = os.getenv("TENCENT_SECRET_ID")
        self.TENCENT_SECRET_KEY = os.getenv("TENCENT_SECRET_KEY")
        self.TENCENT_TTS_REGION = os.getenv("TENCENT_TTS_REGION", "ap-beijing")
        
        # 应用预设配置的推荐设置
        self._apply_preset_settings()
        
        # 添加缺失的目录配置
        self.UPLOAD_DIR = Path("uploads")
        self.OUTPUT_DIR = Path("outputs")
        self.TEMP_DIR = Path("temp")
        
        # 添加其他缺失的配置
        self.SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
        self.MAX_FILE_SIZE = self.max_file_size * 1024 * 1024  # 转换为字节
        self.TEMP_FILE_RETENTION = self._parse_int_env("TEMP_FILE_RETENTION", "24")
        self.CORS_ORIGINS = self.cors_origins
        self.API_HOST = self.api_host
        self.API_PORT = self.api_port
        self.DEBUG = self.debug
    
    def _parse_cors_origins(self) -> List[str]:
        """解析CORS源"""
        origins_str = os.getenv("CORS_ORIGINS", '["http://localhost:8501", "http://127.0.0.1:8501"]')
        try:
            import json
            return json.loads(origins_str)
        except:
            return ["http://localhost:8501", "http://127.0.0.1:8501"]
    
    def _apply_preset_settings(self):
        """应用预设配置的推荐设置"""
        for key, value in self.preset_config.recommended_settings.items():
            env_key = key.upper()
            if not os.getenv(env_key):  # 只在环境变量未设置时应用
                setattr(self, key.lower(), value)
    
    def _validate_configuration(self):
        """验证配置"""
        env_vars = dict(os.environ)
        validation_result = preset_manager.validate_preset_config(self.preset_type, env_vars)
        
        if not validation_result["valid"]:
            logger.error("配置验证失败")
            for recommendation in validation_result["recommendations"]:
                logger.error(f"  - {recommendation}")
        
        if validation_result["missing_keys"]:
            logger.warning("缺失的配置项:")
            for key in validation_result["missing_keys"]:
                logger.warning(f"  - {key}")
        
        # 记录可用服务
        for service_type, services in validation_result["available_services"].items():
            if services:
                logger.info(f"可用的{service_type}服务: {', '.join(services)}")
            else:
                logger.warning(f"没有可用的{service_type}服务")
    
    def get_llm_services(self) -> List[Dict[str, Any]]:
        """获取LLM服务配置"""
        services = []
        for service_config in self.preset_config.llm_services:
            if self._is_service_available(service_config.required_keys):
                service_info = {
                    "name": service_config.name,
                    "priority": service_config.priority,
                    "cost_per_unit": service_config.cost_per_unit,
                    "unit": service_config.unit,
                    "description": service_config.description,
                    "config": self._get_service_config(service_config.name)
                }
                services.append(service_info)
        
        return sorted(services, key=lambda x: x["priority"])
    
    def get_tts_services(self) -> List[Dict[str, Any]]:
        """获取TTS服务配置"""
        services = []
        for service_config in self.preset_config.tts_services:
            if self._is_service_available(service_config.required_keys):
                service_info = {
                    "name": service_config.name,
                    "priority": service_config.priority,
                    "cost_per_unit": service_config.cost_per_unit,
                    "unit": service_config.unit,
                    "description": service_config.description,
                    "config": self._get_service_config(service_config.name)
                }
                services.append(service_info)
        
        return sorted(services, key=lambda x: x["priority"])
    
    def get_vision_services(self) -> List[Dict[str, Any]]:
        """获取视觉服务配置"""
        services = []
        for service_config in self.preset_config.vision_services:
            if self._is_service_available(service_config.required_keys):
                service_info = {
                    "name": service_config.name,
                    "priority": service_config.priority,
                    "cost_per_unit": service_config.cost_per_unit,
                    "unit": service_config.unit,
                    "description": service_config.description,
                    "config": self._get_service_config(service_config.name)
                }
                services.append(service_info)
        
        return sorted(services, key=lambda x: x["priority"])
    
    def _is_service_available(self, required_keys: List[str]) -> bool:
        """检查服务是否可用"""
        if not required_keys:  # 无需配置的服务（如Edge-TTS）
            return True
        return all(os.getenv(key) for key in required_keys)
    
    def _get_service_config(self, service_name: str) -> Dict[str, Any]:
        """获取特定服务的配置"""
        configs = {
            "通义千问": {
                "api_key": os.getenv("QWEN_API_KEY"),
                "model": os.getenv("QWEN_MODEL", "qwen-plus"),
                "base_url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
            },
            "文心一言": {
                "api_key": os.getenv("ERNIE_API_KEY"),
                "secret_key": os.getenv("ERNIE_SECRET_KEY"),
                "model": os.getenv("ERNIE_MODEL", "ernie-3.5-8k")
            },
            "GPT-4": {
                "api_key": os.getenv("OPENAI_API_KEY"),
                "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                "model": os.getenv("OPENAI_MODEL", "gpt-4")
            },
            "Claude-3 Opus": {
                "api_key": os.getenv("CLAUDE_API_KEY"),
                "model": os.getenv("CLAUDE_MODEL", "claude-3-opus-20240229")
            },
            "智谱AI GLM-3": {
                "api_key": os.getenv("ZHIPU_API_KEY"),
                "model": os.getenv("ZHIPU_MODEL", "glm-3-turbo")
            },
            "月之暗面": {
                "api_key": os.getenv("MOONSHOT_API_KEY"),
                "model": os.getenv("MOONSHOT_MODEL", "moonshot-v1-8k")
            },
            "阿里云TTS": {
                "access_key_id": os.getenv("ALIYUN_ACCESS_KEY_ID"),
                "access_key_secret": os.getenv("ALIYUN_ACCESS_KEY_SECRET"),
                "region": os.getenv("ALIYUN_TTS_REGION", "cn-shanghai"),
                "voice": os.getenv("ALIYUN_TTS_VOICE", "xiaoyun")
            },
            "腾讯云TTS": {
                "secret_id": os.getenv("TENCENT_SECRET_ID"),
                "secret_key": os.getenv("TENCENT_SECRET_KEY"),
                "region": os.getenv("TENCENT_TTS_REGION", "ap-beijing"),
                "voice": os.getenv("TENCENT_TTS_VOICE", "101001")
            },
            "Azure TTS": {
                "api_key": os.getenv("AZURE_TTS_KEY"),
                "region": os.getenv("AZURE_TTS_REGION", "eastus"),
                "voice": os.getenv("AZURE_TTS_VOICE", "zh-CN-XiaoxiaoNeural")
            },
            "百度TTS": {
                "api_key": os.getenv("BAIDU_TTS_API_KEY"),
                "secret_key": os.getenv("BAIDU_TTS_SECRET_KEY"),
                "voice": os.getenv("BAIDU_TTS_VOICE", "0")
            },
            "Edge-TTS": {
                "voice": os.getenv("EDGE_TTS_VOICE", "zh-CN-XiaoxiaoNeural")
            },
            "百度AI": {
                "api_key": os.getenv("BAIDU_API_KEY"),
                "secret_key": os.getenv("BAIDU_SECRET_KEY")
            },
            "通义千问-VL": {
                "api_key": os.getenv("QWEN_VL_API_KEY"),
                "model": os.getenv("QWEN_VL_MODEL", "qwen-vl-plus")
            },
            "GPT-4V": {
                "api_key": os.getenv("OPENAI_VISION_API_KEY"),
                "model": os.getenv("OPENAI_VISION_MODEL", "gpt-4-vision-preview")
            },
            "腾讯云视觉AI": {
                "secret_id": os.getenv("TENCENT_VISION_SECRET_ID"),
                "secret_key": os.getenv("TENCENT_VISION_SECRET_KEY")
            },
            "阿里云视觉智能": {
                "access_key_id": os.getenv("ALIYUN_VISION_ACCESS_KEY_ID"),
                "access_key_secret": os.getenv("ALIYUN_VISION_ACCESS_KEY_SECRET")
            }
        }
        
        return configs.get(service_name, {})
    
    def get_preset_info(self) -> Dict[str, Any]:
        """获取当前预设配置信息"""
        return {
            "type": self.preset_type.value,
            "name": self.preset_config.name,
            "description": self.preset_config.description,
            "estimated_cost": self.preset_config.estimated_cost_per_5min,
            "llm_services": len(self.preset_config.llm_services),
            "tts_services": len(self.preset_config.tts_services),
            "vision_services": len(self.preset_config.vision_services),
            "available_llm": len(self.get_llm_services()),
            "available_tts": len(self.get_tts_services()),
            "available_vision": len(self.get_vision_services()),
        }
    
    def estimate_cost(self, text_length: int = 500, audio_length: int = 500, frame_count: int = 50) -> Dict[str, Any]:
        """估算处理成本"""
        llm_services = self.get_llm_services()
        tts_services = self.get_tts_services()
        vision_services = self.get_vision_services()
        
        # 计算LLM成本（假设输入输出各占一半）
        llm_cost = 0
        if llm_services:
            primary_llm = llm_services[0]
            tokens = text_length * 2 / 1000  # 估算token数
            llm_cost = tokens * primary_llm["cost_per_unit"]
        
        # 计算TTS成本
        tts_cost = 0
        if tts_services:
            primary_tts = tts_services[0]
            if primary_tts["unit"] == "字符":
                tts_cost = audio_length * primary_tts["cost_per_unit"]
            elif primary_tts["unit"] == "1K字符":
                tts_cost = (audio_length / 1000) * primary_tts["cost_per_unit"]
        
        # 计算视觉分析成本
        vision_cost = 0
        if vision_services:
            primary_vision = vision_services[0]
            vision_cost = frame_count * primary_vision["cost_per_unit"]
        
        total_cost = llm_cost + tts_cost + vision_cost
        
        return {
            "llm_cost": round(llm_cost, 4),
            "tts_cost": round(tts_cost, 4),
            "vision_cost": round(vision_cost, 4),
            "total_cost": round(total_cost, 4),
            "currency": "CNY",
            "breakdown": {
                "llm": f"{primary_llm['name'] if llm_services else '无'}: ¥{llm_cost:.4f}",
                "tts": f"{primary_tts['name'] if tts_services else '无'}: ¥{tts_cost:.4f}",
                "vision": f"{primary_vision['name'] if vision_services else '无'}: ¥{vision_cost:.4f}"
            }
        }
    
    def check_cost_limits(self, estimated_cost: float) -> Dict[str, Any]:
        """检查成本限制"""
        result = {
            "within_limits": True,
            "warnings": [],
            "blocks": []
        }
        
        # 检查单视频成本限制
        if estimated_cost > self.cost_tracker.single_video_limit:
            result["within_limits"] = False
            result["blocks"].append(f"单视频成本¥{estimated_cost:.4f}超过限制¥{self.cost_tracker.single_video_limit}")
        
        # 检查日度成本限制
        projected_daily = self.cost_tracker.daily_cost + estimated_cost
        if projected_daily > self.cost_tracker.daily_limit:
            result["within_limits"] = False
            result["blocks"].append(f"日度成本将达到¥{projected_daily:.4f}，超过限制¥{self.cost_tracker.daily_limit}")
        elif projected_daily > self.cost_tracker.daily_limit * self.cost_tracker.warning_threshold:
            result["warnings"].append(f"日度成本将达到¥{projected_daily:.4f}，接近限制¥{self.cost_tracker.daily_limit}")
        
        # 检查月度成本限制
        projected_monthly = self.cost_tracker.monthly_cost + estimated_cost
        if projected_monthly > self.cost_tracker.monthly_limit:
            result["within_limits"] = False
            result["blocks"].append(f"月度成本将达到¥{projected_monthly:.4f}，超过限制¥{self.cost_tracker.monthly_limit}")
        elif projected_monthly > self.cost_tracker.monthly_limit * self.cost_tracker.warning_threshold:
            result["warnings"].append(f"月度成本将达到¥{projected_monthly:.4f}，接近限制¥{self.cost_tracker.monthly_limit}")
        
        return result
    
    def update_cost(self, actual_cost: float):
        """更新实际成本"""
        self.cost_tracker.daily_cost += actual_cost
        self.cost_tracker.monthly_cost += actual_cost
        self.cost_tracker.total_cost += actual_cost
        
        logger.info(f"成本更新: +¥{actual_cost:.4f}, 日度总计: ¥{self.cost_tracker.daily_cost:.4f}, 月度总计: ¥{self.cost_tracker.monthly_cost:.4f}")
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        return {
            "preset": self.get_preset_info(),
            "services": {
                "llm": self.get_llm_services(),
                "tts": self.get_tts_services(),
                "vision": self.get_vision_services()
            },
            "cost_tracker": {
                "daily_cost": self.cost_tracker.daily_cost,
                "monthly_cost": self.cost_tracker.monthly_cost,
                "total_cost": self.cost_tracker.total_cost,
                "daily_limit": self.cost_tracker.daily_limit,
                "monthly_limit": self.cost_tracker.monthly_limit,
                "single_video_limit": self.cost_tracker.single_video_limit
            },
            "settings": {
                "max_file_size": self.max_file_size,
                "frame_sample_interval": self.frame_sample_interval,
                "max_frames_per_video": self.max_frames_per_video,
                "video_quality": self.video_quality,
                "audio_quality": self.audio_quality,
                "max_concurrent_tasks": self.max_concurrent_tasks
            }
        }
    
    def validate_config(self):
        """验证配置并返回错误和警告"""
        errors = []
        warnings = []
        
        # 检查必要的目录
        for dir_path in [self.UPLOAD_DIR, self.OUTPUT_DIR, self.TEMP_DIR]:
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    errors.append(f"无法创建目录 {dir_path}: {e}")
        
        # 检查服务配置
        if not self.get_llm_services():
            warnings.append("没有可用的LLM服务")
        
        if not self.get_tts_services():
            warnings.append("没有可用的TTS服务")
        
        if not self.get_vision_services():
            warnings.append("没有可用的视觉分析服务")
        
        return errors, warnings
    
    def get_config(self):
        """获取配置信息"""
        return {
            "api_host": self.api_host,
            "api_port": self.api_port,
            "debug": self.debug,
            "log_level": self.log_level,
            "preset_type": self.preset_type.value
        }
    
    def get_available_llm_services(self):
        """获取可用的LLM服务列表"""
        return [service["name"] for service in self.get_llm_services()]
    
    def get_available_tts_services(self):
        """获取可用的TTS服务列表"""
        return [service["name"] for service in self.get_tts_services()]
    
    def get_available_video_services(self):
        """获取可用的视觉服务列表"""
        return [service["name"] for service in self.get_vision_services()]


# 全局配置实例
settings = CloudSettings()
cloud_settings = settings  # 保持向后兼容


def get_cloud_settings() -> CloudSettings:
    """获取云端配置的便捷函数"""
    return settings


if __name__ == "__main__":
    # 测试代码
    settings = CloudSettings()
    
    print("=== 当前预设配置 ===")
    preset_info = settings.get_preset_info()
    print(f"配置: {preset_info['name']}")
    print(f"描述: {preset_info['description']}")
    print(f"预估成本: {preset_info['estimated_cost']}")
    print()
    
    print("=== 可用服务 ===")
    print(f"LLM服务: {len(settings.get_llm_services())}个")
    for service in settings.get_llm_services():
        print(f"  - {service['name']}: {service['cost_per_unit']}{service['unit']}")
    
    print(f"TTS服务: {len(settings.get_tts_services())}个")
    for service in settings.get_tts_services():
        print(f"  - {service['name']}: {service['cost_per_unit']}{service['unit']}")
    
    print(f"视觉服务: {len(settings.get_vision_services())}个")
    for service in settings.get_vision_services():
        print(f"  - {service['name']}: {service['cost_per_unit']}{service['unit']}")
    
    print("\n=== 成本估算 ===")
    cost_estimate = settings.estimate_cost()
    print(f"总成本: ¥{cost_estimate['total_cost']}")
    for service_type, cost_info in cost_estimate['breakdown'].items():
        print(f"  {service_type}: {cost_info}")