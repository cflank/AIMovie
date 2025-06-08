"""
预设配置管理器
定义不同的大模型组合方案，用户可根据需求选择
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class PresetType(Enum):
    """预设配置类型"""
    COST_EFFECTIVE = "cost_effective"  # 最高性价比
    PREMIUM = "premium"                # 质量最高
    BUDGET = "budget"                  # 最经济


@dataclass
class ServiceConfig:
    """服务配置"""
    name: str
    priority: int  # 优先级，数字越小优先级越高
    cost_per_unit: float  # 单位成本
    unit: str  # 计费单位
    description: str
    required_keys: List[str]  # 必需的环境变量


@dataclass
class PresetConfig:
    """预设配置"""
    name: str
    description: str
    estimated_cost_per_5min: str  # 5分钟视频预估成本
    llm_services: List[ServiceConfig]
    tts_services: List[ServiceConfig]
    vision_services: List[ServiceConfig]
    recommended_settings: Dict[str, any]


class PresetConfigManager:
    """预设配置管理器"""
    
    def __init__(self):
        self.presets = self._init_presets()
    
    def _init_presets(self) -> Dict[PresetType, PresetConfig]:
        """初始化预设配置"""
        return {
            PresetType.COST_EFFECTIVE: self._get_cost_effective_config(),
            PresetType.PREMIUM: self._get_premium_config(),
            PresetType.BUDGET: self._get_budget_config(),
        }
    
    def _get_cost_effective_config(self) -> PresetConfig:
        """最高性价比配置"""
        return PresetConfig(
            name="🏆 最高性价比组合",
            description="平衡质量与成本，适合大多数用户的最佳选择",
            estimated_cost_per_5min="¥0.06-0.12",
            llm_services=[
                ServiceConfig(
                    name="通义千问",
                    priority=1,
                    cost_per_unit=0.0008,
                    unit="1K tokens",
                    description="阿里云通义千问，性价比最高的中文大模型",
                    required_keys=["QWEN_API_KEY"]
                ),
                ServiceConfig(
                    name="文心一言",
                    priority=2,
                    cost_per_unit=0.008,
                    unit="1K tokens",
                    description="百度文心一言，中文优化，备用选择",
                    required_keys=["ERNIE_API_KEY", "ERNIE_SECRET_KEY"]
                ),
            ],
            tts_services=[
                ServiceConfig(
                    name="阿里云TTS",
                    priority=1,
                    cost_per_unit=0.00002,
                    unit="字符",
                    description="阿里云语音合成，音质好价格低",
                    required_keys=["ALIYUN_ACCESS_KEY_ID", "ALIYUN_ACCESS_KEY_SECRET"]
                ),
                ServiceConfig(
                    name="Edge-TTS",
                    priority=2,
                    cost_per_unit=0.0,
                    unit="字符",
                    description="微软Edge免费TTS，无需配置",
                    required_keys=[]
                ),
            ],
            vision_services=[
                ServiceConfig(
                    name="百度AI",
                    priority=1,
                    cost_per_unit=0.002,
                    unit="图片",
                    description="百度视觉AI，识别准确免费额度大",
                    required_keys=["BAIDU_API_KEY", "BAIDU_SECRET_KEY"]
                ),
                ServiceConfig(
                    name="通义千问-VL",
                    priority=2,
                    cost_per_unit=0.008,
                    unit="图片",
                    description="阿里云多模态理解，备用选择",
                    required_keys=["QWEN_VL_API_KEY"]
                ),
            ],
            recommended_settings={
                "FRAME_SAMPLE_INTERVAL": 3,
                "MAX_FRAMES_PER_VIDEO": 50,
                "VIDEO_QUALITY": "medium",
                "AUDIO_QUALITY": "medium",
                "MAX_CONCURRENT_TASKS": 3,
            }
        )
    
    def _get_premium_config(self) -> PresetConfig:
        """质量最高配置"""
        return PresetConfig(
            name="💎 质量最高组合",
            description="追求最佳效果，适合对质量要求极高的专业用户",
            estimated_cost_per_5min="¥0.5-1.0",
            llm_services=[
                ServiceConfig(
                    name="GPT-4",
                    priority=1,
                    cost_per_unit=0.03,
                    unit="1K tokens",
                    description="OpenAI GPT-4，目前最强大的语言模型",
                    required_keys=["OPENAI_API_KEY"]
                ),
                ServiceConfig(
                    name="Claude-3 Opus",
                    priority=2,
                    cost_per_unit=0.015,
                    unit="1K tokens",
                    description="Anthropic Claude-3 Opus，高质量备选",
                    required_keys=["CLAUDE_API_KEY"]
                ),
                ServiceConfig(
                    name="通义千问-Max",
                    priority=3,
                    cost_per_unit=0.02,
                    unit="1K tokens",
                    description="通义千问最高版本，中文优化",
                    required_keys=["QWEN_API_KEY"]
                ),
            ],
            tts_services=[
                ServiceConfig(
                    name="Azure TTS",
                    priority=1,
                    cost_per_unit=0.016,
                    unit="1K字符",
                    description="微软Azure TTS，音质最佳",
                    required_keys=["AZURE_TTS_KEY", "AZURE_TTS_REGION"]
                ),
                ServiceConfig(
                    name="阿里云TTS",
                    priority=2,
                    cost_per_unit=0.00002,
                    unit="字符",
                    description="阿里云TTS，性价比备选",
                    required_keys=["ALIYUN_ACCESS_KEY_ID", "ALIYUN_ACCESS_KEY_SECRET"]
                ),
            ],
            vision_services=[
                ServiceConfig(
                    name="GPT-4V",
                    priority=1,
                    cost_per_unit=0.01,
                    unit="图片",
                    description="OpenAI GPT-4 Vision，视觉理解最强",
                    required_keys=["OPENAI_VISION_API_KEY"]
                ),
                ServiceConfig(
                    name="通义千问-VL Max",
                    priority=2,
                    cost_per_unit=0.008,
                    unit="图片",
                    description="通义千问视觉版本，中文优化",
                    required_keys=["QWEN_VL_API_KEY"]
                ),
            ],
            recommended_settings={
                "FRAME_SAMPLE_INTERVAL": 2,
                "MAX_FRAMES_PER_VIDEO": 80,
                "VIDEO_QUALITY": "high",
                "AUDIO_QUALITY": "high",
                "MAX_CONCURRENT_TASKS": 2,
                "LLM_TIMEOUT": 180,
                "TTS_TIMEOUT": 240,
            }
        )
    
    def _get_budget_config(self) -> PresetConfig:
        """最经济配置"""
        return PresetConfig(
            name="💰 最经济组合",
            description="最低成本方案，适合预算有限或大批量处理的用户",
            estimated_cost_per_5min="¥0.02-0.05",
            llm_services=[
                ServiceConfig(
                    name="文心一言-Lite",
                    priority=1,
                    cost_per_unit=0.0008,
                    unit="1K tokens",
                    description="文心一言轻量版，成本最低",
                    required_keys=["ERNIE_API_KEY", "ERNIE_SECRET_KEY"]
                ),
                ServiceConfig(
                    name="通义千问-Turbo",
                    priority=2,
                    cost_per_unit=0.0008,
                    unit="1K tokens",
                    description="通义千问快速版，备用选择",
                    required_keys=["QWEN_API_KEY"]
                ),
                ServiceConfig(
                    name="智谱AI GLM-3",
                    priority=3,
                    cost_per_unit=0.005,
                    unit="1K tokens",
                    description="智谱AI，国产模型",
                    required_keys=["ZHIPU_API_KEY"]
                ),
            ],
            tts_services=[
                ServiceConfig(
                    name="Edge-TTS",
                    priority=1,
                    cost_per_unit=0.0,
                    unit="字符",
                    description="微软Edge免费TTS，完全免费",
                    required_keys=[]
                ),
                ServiceConfig(
                    name="百度TTS",
                    priority=2,
                    cost_per_unit=0.0,
                    unit="字符",
                    description="百度TTS，每月5万字符免费",
                    required_keys=["BAIDU_TTS_API_KEY", "BAIDU_TTS_SECRET_KEY"]
                ),
            ],
            vision_services=[
                ServiceConfig(
                    name="百度AI",
                    priority=1,
                    cost_per_unit=0.002,
                    unit="图片",
                    description="百度视觉AI，免费额度大",
                    required_keys=["BAIDU_API_KEY", "BAIDU_SECRET_KEY"]
                ),
            ],
            recommended_settings={
                "FRAME_SAMPLE_INTERVAL": 5,
                "MAX_FRAMES_PER_VIDEO": 30,
                "VIDEO_QUALITY": "low",
                "AUDIO_QUALITY": "medium",
                "MAX_CONCURRENT_TASKS": 5,
                "DAILY_COST_LIMIT": 10.0,
                "MONTHLY_COST_LIMIT": 100.0,
            }
        )
    
    def get_preset(self, preset_type: PresetType) -> PresetConfig:
        """获取预设配置"""
        return self.presets[preset_type]
    
    def get_preset_by_name(self, name: str) -> Optional[PresetConfig]:
        """根据名称获取预设配置"""
        for preset_type in PresetType:
            if preset_type.value == name:
                return self.presets[preset_type]
        return None
    
    def list_presets(self) -> List[Dict]:
        """列出所有预设配置"""
        result = []
        for preset_type, config in self.presets.items():
            result.append({
                "type": preset_type.value,
                "name": config.name,
                "description": config.description,
                "estimated_cost": config.estimated_cost_per_5min,
                "llm_count": len(config.llm_services),
                "tts_count": len(config.tts_services),
                "vision_count": len(config.vision_services),
            })
        return result
    
    def get_cost_comparison(self) -> Dict:
        """获取成本对比"""
        comparison = {}
        for preset_type, config in self.presets.items():
            comparison[preset_type.value] = {
                "name": config.name,
                "cost_per_5min": config.estimated_cost_per_5min,
                "cost_per_100_videos": self._calculate_monthly_cost(config),
                "primary_llm": config.llm_services[0].name if config.llm_services else "无",
                "primary_tts": config.tts_services[0].name if config.tts_services else "无",
                "primary_vision": config.vision_services[0].name if config.vision_services else "无",
            }
        return comparison
    
    def _calculate_monthly_cost(self, config: PresetConfig) -> str:
        """计算月度成本估算"""
        cost_range = config.estimated_cost_per_5min.replace("¥", "").replace("$", "")
        if "-" in cost_range:
            min_cost, max_cost = cost_range.split("-")
            min_monthly = float(min_cost) * 100
            max_monthly = float(max_cost) * 100
            return f"¥{min_monthly:.0f}-{max_monthly:.0f}"
        else:
            monthly = float(cost_range) * 100
            return f"¥{monthly:.0f}"
    
    def validate_preset_config(self, preset_type: PresetType, env_vars: Dict[str, str]) -> Dict:
        """验证预设配置的环境变量"""
        config = self.get_preset(preset_type)
        validation_result = {
            "valid": True,
            "missing_keys": [],
            "available_services": {
                "llm": [],
                "tts": [],
                "vision": []
            },
            "recommendations": []
        }
        
        # 统一使用真实模式
        
        # 检查LLM服务
        for service in config.llm_services:
            if all(key in env_vars and env_vars[key] and not env_vars[key].startswith("your_") for key in service.required_keys):
                validation_result["available_services"]["llm"].append(service.name)
            else:
                validation_result["missing_keys"].extend(service.required_keys)
        
        # 检查TTS服务
        for service in config.tts_services:
            if not service.required_keys or all(key in env_vars and env_vars[key] and not env_vars[key].startswith("your_") for key in service.required_keys):
                validation_result["available_services"]["tts"].append(service.name)
            else:
                validation_result["missing_keys"].extend(service.required_keys)
        
        # 检查视觉服务
        for service in config.vision_services:
            if all(key in env_vars and env_vars[key] and not env_vars[key].startswith("your_") for key in service.required_keys):
                validation_result["available_services"]["vision"].append(service.name)
            else:
                validation_result["missing_keys"].extend(service.required_keys)
        
        # 检查是否至少有一个LLM服务可用
        if not validation_result["available_services"]["llm"]:
            validation_result["valid"] = False
            validation_result["recommendations"].append("至少需要配置一个LLM服务")
        
        # 去重缺失的键
        validation_result["missing_keys"] = list(set(validation_result["missing_keys"]))
        
        return validation_result


# 全局实例
preset_manager = PresetConfigManager()


def get_preset_config(preset_name: str = None) -> Optional[PresetConfig]:
    """获取预设配置的便捷函数"""
    if not preset_name:
        return preset_manager.get_preset(PresetType.COST_EFFECTIVE)
    return preset_manager.get_preset_by_name(preset_name)


def list_all_presets() -> List[Dict]:
    """列出所有预设配置的便捷函数"""
    return preset_manager.list_presets()


def get_cost_comparison() -> Dict:
    """获取成本对比的便捷函数"""
    return preset_manager.get_cost_comparison()


if __name__ == "__main__":
    # 测试代码
    manager = PresetConfigManager()
    
    print("=== 预设配置列表 ===")
    for preset in manager.list_presets():
        print(f"{preset['name']}: {preset['description']}")
        print(f"  预估成本: {preset['estimated_cost']}")
        print(f"  服务数量: LLM({preset['llm_count']}) TTS({preset['tts_count']}) Vision({preset['vision_count']})")
        print()
    
    print("=== 成本对比 ===")
    comparison = manager.get_cost_comparison()
    for preset_type, info in comparison.items():
        print(f"{info['name']}:")
        print(f"  单视频成本: {info['cost_per_5min']}")
        print(f"  月度成本(100视频): {info['cost_per_100_videos']}")
        print(f"  主要服务: {info['primary_llm']} + {info['primary_tts']} + {info['primary_vision']}")
        print() 