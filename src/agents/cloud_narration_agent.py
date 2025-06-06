import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Callable, Any
import requests
import re

try:
    from ..config.cloud_settings import settings
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from src.config.cloud_settings import settings

logger = logging.getLogger(__name__)

class CloudNarrationAgent:
    """云端解说生成Agent - 使用通义千问和文心一言"""
    
    def __init__(self):
        self.ernie_access_token = None
        self.ernie_token_expires_at = 0
    
    async def _get_ernie_access_token(self) -> str:
        """获取文心一言访问令牌"""
        if self.ernie_access_token and time.time() < self.ernie_token_expires_at:
            return self.ernie_access_token
            
        if not settings.ERNIE_API_KEY or not settings.ERNIE_SECRET_KEY:
            raise ValueError("文心一言API密钥未配置")
            
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": settings.ERNIE_API_KEY,
            "client_secret": settings.ERNIE_SECRET_KEY
        }
        
        try:
            response = requests.post(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "access_token" in data:
                self.ernie_access_token = data["access_token"]
                self.ernie_token_expires_at = time.time() + data.get("expires_in", 3600) - 300
                return self.ernie_access_token
            else:
                raise ValueError(f"获取文心一言访问令牌失败: {data}")
                
        except Exception as e:
            logger.error(f"获取文心一言访问令牌失败: {e}")
            raise
    
    async def _generate_with_qwen(self, prompt: str, max_tokens: int = 2000) -> str:
        """使用通义千问生成解说"""
        try:
            if not settings.QWEN_API_KEY:
                raise ValueError("通义千问API密钥未配置")
            
            url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
            
            headers = {
                "Authorization": f"Bearer {settings.QWEN_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": settings.QWEN_MODEL,
                "input": {
                    "messages": [
                        {
                            "role": "system",
                            "content": "你是一个专业的视频解说员，擅长根据视频内容生成生动有趣的解说词。"
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ]
                },
                "parameters": {
                    "result_format": "message",
                    "max_tokens": max_tokens,
                    "temperature": 0.7,
                    "top_p": 0.8
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            if "output" in result and "choices" in result["output"]:
                return result["output"]["choices"][0]["message"]["content"]
            else:
                logger.warning(f"通义千问响应异常: {result}")
                return ""
                
        except Exception as e:
            logger.error(f"通义千问生成失败: {e}")
            raise
    
    async def _generate_with_ernie(self, prompt: str, max_tokens: int = 2000) -> str:
        """使用文心一言生成解说"""
        try:
            access_token = await self._get_ernie_access_token()
            
            url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{settings.ERNIE_MODEL}?access_token={access_token}"
            
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "top_p": 0.8,
                "penalty_score": 1.0,
                "max_output_tokens": max_tokens
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            if "result" in result:
                return result["result"]
            else:
                logger.warning(f"文心一言响应异常: {result}")
                return ""
                
        except Exception as e:
            logger.error(f"文心一言生成失败: {e}")
            raise
    
    def _create_narration_prompt(
        self, 
        video_analysis: Dict[str, Any], 
        style: str = "professional",
        target_audience: str = "general",
        narration_length: str = "medium"
    ) -> str:
        """创建解说生成提示词"""
        
        # 提取视频信息
        video_info = video_analysis.get("video_info", {})
        summary = video_analysis.get("summary", {})
        key_moments = summary.get("key_moments", [])
        audio_info = video_analysis.get("audio_analysis", {})
        
        duration = video_info.get("duration", 0)
        scene_types = summary.get("scene_types", {})
        top_objects = summary.get("top_objects", [])
        
        # 风格设定
        style_prompts = {
            "professional": "专业严肃的解说风格，用词准确，语调平稳",
            "humorous": "幽默风趣的解说风格，适当加入趣味性评论和比喻",
            "emotional": "情感丰富的解说风格，注重情感表达和感染力",
            "suspenseful": "悬疑紧张的解说风格，营造紧张氛围"
        }
        
        # 目标观众
        audience_prompts = {
            "general": "面向普通大众",
            "young": "面向年轻观众，语言活泼",
            "professional": "面向专业人士，术语准确",
            "children": "面向儿童观众，语言简单易懂"
        }
        
        # 解说长度
        length_prompts = {
            "short": f"简短解说，约{int(duration * 0.3)}秒",
            "medium": f"中等长度解说，约{int(duration * 0.6)}秒", 
            "long": f"详细解说，约{int(duration * 0.9)}秒"
        }
        
        prompt = f"""请根据以下视频分析结果，生成{style_prompts.get(style, '专业')}的视频解说词。

视频基本信息：
- 时长：{duration:.1f}秒
- 音频：{'有背景音' if audio_info.get('has_audio') else '无音频'}

场景分析：
"""
        
        if scene_types:
            prompt += "- 主要场景：" + "、".join([f"{k}({v}帧)" for k, v in scene_types.items()]) + "\n"
        
        if top_objects:
            prompt += "- 主要元素：" + "、".join([obj["name"] for obj in top_objects[:5]]) + "\n"
        
        if key_moments:
            prompt += "\n关键时刻：\n"
            for i, moment in enumerate(key_moments[:5], 1):
                timestamp = moment["timestamp"]
                desc = moment["description"]
                prompt += f"{i}. {timestamp:.1f}秒: {desc}\n"
        
        prompt += f"""
解说要求：
1. 风格：{style_prompts.get(style, '专业严肃')}
2. 目标观众：{audience_prompts.get(target_audience, '普通大众')}
3. 长度：{length_prompts.get(narration_length, '中等长度')}
4. 格式：请按时间顺序生成解说词，每段解说标注时间点
5. 语言：使用中文，语言流畅自然

请生成格式如下的解说词：
[00:00] 开场解说内容...
[00:05] 第一个场景的解说...
[00:15] 第二个场景的解说...
...

注意：
- 解说词要与视频内容紧密结合
- 时间点要合理分布
- 语言要符合选定的风格和观众
- 避免过于冗长或过于简短
"""
        
        return prompt
    
    def _parse_narration_text(self, narration_text: str) -> List[Dict[str, Any]]:
        """解析解说文本，提取时间戳和内容"""
        segments = []
        
        # 匹配时间戳格式 [MM:SS] 或 [M:SS] 或 [SS]
        pattern = r'\[(\d{1,2}):?(\d{2})?\]\s*([^\[\n]+)'
        matches = re.findall(pattern, narration_text)
        
        for match in matches:
            minutes = int(match[0]) if match[0] else 0
            seconds = int(match[1]) if match[1] else int(match[0])
            content = match[2].strip()
            
            if not content:
                continue
                
            timestamp = minutes * 60 + seconds
            
            segments.append({
                "timestamp": timestamp,
                "content": content,
                "duration": 5  # 默认每段5秒
            })
        
        # 如果没有匹配到时间戳，尝试按段落分割
        if not segments:
            lines = [line.strip() for line in narration_text.split('\n') if line.strip()]
            segment_duration = 10  # 每段10秒
            
            for i, line in enumerate(lines):
                segments.append({
                    "timestamp": i * segment_duration,
                    "content": line,
                    "duration": segment_duration
                })
        
        # 调整duration，避免重叠
        for i in range(len(segments) - 1):
            next_timestamp = segments[i + 1]["timestamp"]
            current_timestamp = segments[i]["timestamp"]
            max_duration = next_timestamp - current_timestamp
            
            if max_duration > 0:
                segments[i]["duration"] = min(segments[i]["duration"], max_duration)
        
        return segments
    
    async def generate_narration(
        self,
        video_analysis: Dict[str, Any],
        style: str = "professional",
        target_audience: str = "general", 
        narration_length: str = "medium",
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Dict[str, Any]:
        """
        生成视频解说
        
        Args:
            video_analysis: 视频分析结果
            style: 解说风格 (professional/humorous/emotional/suspenseful)
            target_audience: 目标观众 (general/young/professional/children)
            narration_length: 解说长度 (short/medium/long)
            progress_callback: 进度回调函数
            
        Returns:
            解说生成结果
        """
        try:
            if progress_callback:
                progress_callback(0.0, "开始生成解说...")
            
            # 创建提示词
            prompt = self._create_narration_prompt(
                video_analysis, style, target_audience, narration_length
            )
            
            if progress_callback:
                progress_callback(0.2, "准备调用AI服务...")
            
            # 尝试使用通义千问
            narration_text = ""
            service_used = ""
            
            try:
                if progress_callback:
                    progress_callback(0.4, "使用通义千问生成解说...")
                
                narration_text = await self._generate_with_qwen(prompt)
                service_used = "通义千问"
                
            except Exception as e:
                logger.warning(f"通义千问生成失败，尝试文心一言: {e}")
                
                if progress_callback:
                    progress_callback(0.6, "使用文心一言生成解说...")
                
                try:
                    narration_text = await self._generate_with_ernie(prompt)
                    service_used = "文心一言"
                except Exception as e2:
                    logger.error(f"文心一言也失败: {e2}")
                    # 使用模板生成
                    if progress_callback:
                        progress_callback(0.8, "使用模板生成解说...")
                    
                    narration_text = self._generate_template_narration(video_analysis, style)
                    service_used = "模板生成"
            
            if not narration_text:
                raise ValueError("所有解说生成方法都失败了")
            
            if progress_callback:
                progress_callback(0.9, "解析解说内容...")
            
            # 解析解说文本
            segments = self._parse_narration_text(narration_text)
            
            # 计算统计信息
            total_duration = sum(seg["duration"] for seg in segments)
            word_count = sum(len(seg["content"]) for seg in segments)
            
            result = {
                "narration_text": narration_text,
                "segments": segments,
                "metadata": {
                    "style": style,
                    "target_audience": target_audience,
                    "narration_length": narration_length,
                    "service_used": service_used,
                    "generation_time": time.time(),
                    "total_segments": len(segments),
                    "total_duration": total_duration,
                    "word_count": word_count,
                    "estimated_speech_time": word_count * 0.5  # 估算语音时长（秒）
                }
            }
            
            if progress_callback:
                progress_callback(1.0, f"解说生成完成! 共{len(segments)}段")
            
            logger.info(f"解说生成完成: {service_used}, {len(segments)}段, {word_count}字")
            return result
            
        except Exception as e:
            logger.error(f"解说生成失败: {e}")
            if progress_callback:
                progress_callback(1.0, f"生成失败: {str(e)}")
            raise
    
    def _generate_template_narration(
        self, 
        video_analysis: Dict[str, Any], 
        style: str = "professional"
    ) -> str:
        """生成模板解说（备用方案）"""
        try:
            video_info = video_analysis.get("video_info", {})
            summary = video_analysis.get("summary", {})
            key_moments = summary.get("key_moments", [])
            
            duration = video_info.get("duration", 0)
            scene_types = summary.get("scene_types", {})
            
            # 根据风格选择模板
            if style == "humorous":
                opening = "哈喽大家好！今天我们来看一个有趣的视频。"
                transition = "接下来让我们看看"
                ending = "好了，这个视频就到这里，觉得有趣的话记得点赞哦！"
            elif style == "emotional":
                opening = "朋友们，今天要和大家分享一个触动人心的视频。"
                transition = "让我们一起感受"
                ending = "希望这个视频能给大家带来一些思考和感动。"
            elif style == "suspenseful":
                opening = "各位观众，接下来您将看到的内容可能会让您感到惊讶..."
                transition = "紧接着发生的事情是"
                ending = "真相往往比我们想象的更加复杂..."
            else:  # professional
                opening = "欢迎观看本期视频解说。"
                transition = "我们可以看到"
                ending = "以上就是本期视频的全部内容。"
            
            # 生成解说内容
            narration = f"[00:00] {opening}\n\n"
            
            # 根据关键时刻生成解说
            if key_moments:
                for i, moment in enumerate(key_moments[:5]):
                    timestamp = int(moment["timestamp"])
                    minutes = timestamp // 60
                    seconds = timestamp % 60
                    time_str = f"{minutes:02d}:{seconds:02d}"
                    
                    description = moment.get("description", "")
                    narration += f"[{time_str}] {transition}{description}\n\n"
            else:
                # 如果没有关键时刻，根据场景类型生成
                segment_time = 0
                for scene_type in scene_types.keys():
                    minutes = segment_time // 60
                    seconds = segment_time % 60
                    time_str = f"{minutes:02d}:{seconds:02d}"
                    
                    narration += f"[{time_str}] {transition}视频中的{scene_type}场景。\n\n"
                    segment_time += 15
            
            # 添加结尾
            end_time = int(duration - 5) if duration > 5 else int(duration)
            minutes = end_time // 60
            seconds = end_time % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
            
            narration += f"[{time_str}] {ending}"
            
            return narration
            
        except Exception as e:
            logger.error(f"模板解说生成失败: {e}")
            return "[00:00] 欢迎观看本期视频。\n[00:10] 视频内容正在播放中。\n[00:20] 感谢您的观看。"
    
    async def optimize_narration(
        self, 
        narration_result: Dict[str, Any], 
        video_duration: float
    ) -> Dict[str, Any]:
        """优化解说时间分布"""
        try:
            segments = narration_result.get("segments", [])
            if not segments:
                return narration_result
            
            # 确保解说不超过视频时长
            optimized_segments = []
            
            for segment in segments:
                if segment["timestamp"] < video_duration:
                    # 调整持续时间，确保不超过视频结束
                    max_duration = video_duration - segment["timestamp"]
                    segment["duration"] = min(segment["duration"], max_duration)
                    optimized_segments.append(segment)
            
            # 更新结果
            narration_result["segments"] = optimized_segments
            narration_result["metadata"]["optimized"] = True
            narration_result["metadata"]["final_segments"] = len(optimized_segments)
            
            return narration_result
            
        except Exception as e:
            logger.error(f"解说优化失败: {e}")
            return narration_result 