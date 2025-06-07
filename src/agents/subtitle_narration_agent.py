import time
import logging
import re
from typing import Dict, Any, List, Optional, Callable
import requests
from src.config.cloud_settings import settings

logger = logging.getLogger(__name__)

class SubtitleNarrationAgent:
    """基于字幕的解说生成代理"""
    
    def __init__(self):
        pass
    
    async def generate_narration_from_subtitle(
        self,
        subtitle_data: Dict[str, Any],
        narration_mode: str = "third_person",  # "third_person" 或 "character"
        character_name: str = "",
        style: str = "professional",
        target_audience: str = "general",
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Dict[str, Any]:
        """
        基于字幕生成解说词
        
        Args:
            subtitle_data: 字幕解析结果
            narration_mode: 解说模式 ("third_person": 第三方视角, "character": 角色第一人称)
            character_name: 当模式为角色时的角色名称
            style: 解说风格
            target_audience: 目标观众
            progress_callback: 进度回调函数
            
        Returns:
            解说生成结果
        """
        try:
            if progress_callback:
                progress_callback(0.0, "开始分析字幕内容...")
            
            # 提取字幕段落
            subtitle_segments = subtitle_data.get("subtitle_segments", [])
            analysis = subtitle_data.get("analysis", {})
            
            if not subtitle_segments:
                raise ValueError("字幕数据为空")
            
            if progress_callback:
                progress_callback(0.2, "创建解说提示词...")
            
            # 创建解说生成提示词
            prompt = self._create_subtitle_narration_prompt(
                subtitle_segments, 
                analysis, 
                narration_mode, 
                character_name, 
                style, 
                target_audience
            )
            
            if progress_callback:
                progress_callback(0.4, "调用AI服务生成解说...")
            
            # 生成解说文本
            narration_text = await self._generate_narration_text(prompt)
            
            if progress_callback:
                progress_callback(0.8, "解析解说内容...")
            
            # 解析解说文本为段落
            narration_segments = self._parse_narration_segments(narration_text, subtitle_segments)
            
            # 生成结果
            result = {
                "narration_text": narration_text,
                "narration_segments": narration_segments,
                "subtitle_segments": subtitle_segments,
                "metadata": {
                    "narration_mode": narration_mode,
                    "character_name": character_name,
                    "style": style,
                    "target_audience": target_audience,
                    "generation_time": time.time(),
                    "total_narration_segments": len(narration_segments),
                    "total_subtitle_segments": len(subtitle_segments),
                    "narration_word_count": len(narration_text),
                    "estimated_speech_time": len(narration_text) * 0.5
                }
            }
            
            if progress_callback:
                progress_callback(1.0, f"解说生成完成！共{len(narration_segments)}段")
            
            logger.info(f"基于字幕的解说生成完成: {narration_mode}模式, {len(narration_segments)}段")
            return result
            
        except Exception as e:
            logger.error(f"基于字幕的解说生成失败: {e}")
            if progress_callback:
                progress_callback(1.0, f"生成失败: {str(e)}")
            raise
    
    def _create_subtitle_narration_prompt(
        self,
        subtitle_segments: List[Dict[str, Any]],
        analysis: Dict[str, Any],
        narration_mode: str,
        character_name: str,
        style: str,
        target_audience: str
    ) -> str:
        """创建基于字幕的解说生成提示词"""
        
        # 提取字幕内容
        subtitle_text = "\n".join([
            f"[{self._seconds_to_time(seg['start_time'])} - {self._seconds_to_time(seg['end_time'])}] {seg['text']}"
            for seg in subtitle_segments[:20]  # 限制长度，避免提示词过长
        ])
        
        # 分析信息
        themes = analysis.get("themes", [])
        emotions = analysis.get("emotions", [])
        characters = analysis.get("characters", [])
        key_phrases = analysis.get("key_phrases", [])
        
        # 风格设定
        style_prompts = {
            "professional": "专业严肃的解说风格，用词准确，语调平稳",
            "humorous": "幽默风趣的解说风格，适当加入趣味性评论和比喻",
            "emotional": "情感丰富的解说风格，注重情感表达和感染力",
            "suspenseful": "悬疑紧张的解说风格，营造紧张氛围",
            "casual": "轻松随意的解说风格，语言亲切自然",
            "dramatic": "戏剧化的解说风格，富有张力和表现力"
        }
        
        # 目标观众
        audience_prompts = {
            "general": "面向普通大众",
            "young": "面向年轻观众，语言活泼",
            "professional": "面向专业人士，术语准确",
            "children": "面向儿童观众，语言简单易懂"
        }
        
        # 根据解说模式创建不同的提示词
        if narration_mode == "character" and character_name:
            # 角色第一人称模式
            prompt = f"""请以"{character_name}"的身份，用第一人称的视角，根据以下字幕内容生成解说词。

角色设定：
- 你是"{character_name}"
- 请以第一人称（我、我们）的视角来解说
- 要体现角色的个性和情感
- 可以表达角色的内心想法和感受

字幕内容：
{subtitle_text}

内容分析：
- 主要主题：{', '.join(themes) if themes else '无'}
- 情感色彩：{', '.join(emotions) if emotions else '无'}
- 出现角色：{', '.join(characters) if characters else '无'}
- 关键词汇：{', '.join(key_phrases[:10]) if key_phrases else '无'}

解说要求：
1. 视角：以"{character_name}"的第一人称视角
2. 风格：{style_prompts.get(style, '专业严肃')}
3. 目标观众：{audience_prompts.get(target_audience, '普通大众')}
4. 语言：使用中文，语言流畅自然
5. 内容：基于字幕内容，但要加入角色的个人感受和解读

请生成解说词，格式如下：
[时间段] 解说内容...

注意：
- 要体现"{character_name}"的个性特点
- 可以表达角色的情感和想法
- 解说要与字幕内容相关但不重复
- 用第一人称语气（我觉得、我看到、我们等）
"""
        else:
            # 第三方视角模式
            prompt = f"""请以第三方客观的视角，根据以下字幕内容生成解说词。

字幕内容：
{subtitle_text}

内容分析：
- 主要主题：{', '.join(themes) if themes else '无'}
- 情感色彩：{', '.join(emotions) if emotions else '无'}
- 出现角色：{', '.join(characters) if characters else '无'}
- 关键词汇：{', '.join(key_phrases[:10]) if key_phrases else '无'}

解说要求：
1. 视角：第三方客观视角（上帝视角）
2. 风格：{style_prompts.get(style, '专业严肃')}
3. 目标观众：{audience_prompts.get(target_audience, '普通大众')}
4. 语言：使用中文，语言流畅自然
5. 内容：基于字幕内容进行解读和分析

请生成解说词，格式如下：
[时间段] 解说内容...

注意：
- 保持客观中立的立场
- 可以分析角色的行为和动机
- 可以解释背景信息和情节发展
- 解说要与字幕内容相关但提供更深层的解读
- 避免简单重复字幕内容
"""
        
        return prompt
    
    async def _generate_narration_text(self, prompt: str) -> str:
        """生成解说文本"""
        # 尝试使用不同的LLM服务
        services = [
            ("通义千问", self._generate_with_qwen),
            ("文心一言", self._generate_with_ernie),
            ("GPT", self._generate_with_openai),
            ("Claude", self._generate_with_claude)
        ]
        
        for service_name, service_func in services:
            try:
                logger.info(f"尝试使用{service_name}生成解说...")
                result = await service_func(prompt)
                if result:
                    logger.info(f"使用{service_name}成功生成解说")
                    return result
            except Exception as e:
                logger.warning(f"{service_name}生成失败: {e}")
                continue
        
        # 如果所有服务都失败，返回模板解说
        logger.warning("所有LLM服务都失败，使用模板生成")
        return self._generate_template_narration()
    
    async def _generate_with_qwen(self, prompt: str) -> str:
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
                "model": settings.QWEN_MODEL or "qwen-plus",
                "input": {
                    "messages": [
                        {
                            "role": "system",
                            "content": "你是一个专业的视频解说员，擅长根据字幕内容生成生动有趣的解说词。"
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                },
                "parameters": {
                    "result_format": "message",
                    "max_tokens": 2000,
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
                raise ValueError(f"通义千问响应异常: {result}")
                
        except Exception as e:
            logger.error(f"通义千问生成失败: {e}")
            raise
    
    async def _generate_with_ernie(self, prompt: str) -> str:
        """使用文心一言生成解说"""
        try:
            if not (settings.BAIDU_API_KEY and settings.BAIDU_SECRET_KEY):
                raise ValueError("百度API密钥未配置")
            
            # 获取access_token
            access_token = await self._get_baidu_access_token()
            
            url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-4.0-8k?access_token={access_token}"
            
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
                "max_output_tokens": 2000
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            if "result" in result:
                return result["result"]
            else:
                raise ValueError(f"文心一言响应异常: {result}")
                
        except Exception as e:
            logger.error(f"文心一言生成失败: {e}")
            raise
    
    async def _generate_with_openai(self, prompt: str) -> str:
        """使用OpenAI生成解说"""
        try:
            if not settings.OPENAI_API_KEY:
                raise ValueError("OpenAI API密钥未配置")
            
            url = "https://api.openai.com/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的视频解说员，擅长根据字幕内容生成生动有趣的解说词。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.7
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            if "choices" in result and result["choices"]:
                return result["choices"][0]["message"]["content"]
            else:
                raise ValueError(f"OpenAI响应异常: {result}")
                
        except Exception as e:
            logger.error(f"OpenAI生成失败: {e}")
            raise
    
    async def _generate_with_claude(self, prompt: str) -> str:
        """使用Claude生成解说"""
        try:
            if not settings.CLAUDE_API_KEY:
                raise ValueError("Claude API密钥未配置")
            
            url = "https://api.anthropic.com/v1/messages"
            
            headers = {
                "x-api-key": settings.CLAUDE_API_KEY,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            payload = {
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 2000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            if "content" in result and result["content"]:
                return result["content"][0]["text"]
            else:
                raise ValueError(f"Claude响应异常: {result}")
                
        except Exception as e:
            logger.error(f"Claude生成失败: {e}")
            raise
    
    def _generate_template_narration(self) -> str:
        """生成模板解说（备用方案）"""
        return """[00:00] 欢迎观看本期视频解说。
[00:10] 根据字幕内容，我们可以看到故事的发展。
[00:20] 角色之间的对话展现了丰富的情感。
[00:30] 让我们继续关注剧情的发展。
[00:40] 感谢您的观看，更多精彩内容请继续关注。"""
    
    def _parse_narration_segments(
        self, 
        narration_text: str, 
        subtitle_segments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """解析解说文本为段落"""
        segments = []
        
        # 匹配时间戳格式 [MM:SS] 或 [HH:MM:SS]
        pattern = r'\[(\d{1,2}):(\d{2})(?::(\d{2}))?\]\s*([^\[\n]+)'
        matches = re.findall(pattern, narration_text)
        
        for match in matches:
            hours = 0
            minutes = int(match[0])
            seconds = int(match[1])
            
            # 如果有第三个组（秒数），说明是HH:MM:SS格式
            if match[2]:
                hours = minutes
                minutes = seconds
                seconds = int(match[2])
            
            timestamp = hours * 3600 + minutes * 60 + seconds
            content = match[3].strip()
            
            if content:
                segments.append({
                    "start_time": timestamp,
                    "end_time": timestamp + 10,  # 默认10秒
                    "text": content,
                    "duration": 10
                })
        
        # 如果没有匹配到时间戳，按段落分割
        if not segments:
            lines = [line.strip() for line in narration_text.split('\n') if line.strip()]
            segment_duration = 8
            
            for i, line in enumerate(lines):
                start_time = i * segment_duration
                segments.append({
                    "start_time": start_time,
                    "end_time": start_time + segment_duration,
                    "text": line,
                    "duration": segment_duration
                })
        
        # 调整时间，避免重叠
        for i in range(len(segments) - 1):
            if segments[i]["end_time"] > segments[i + 1]["start_time"]:
                segments[i]["end_time"] = segments[i + 1]["start_time"]
                segments[i]["duration"] = segments[i]["end_time"] - segments[i]["start_time"]
        
        return segments
    
    def _seconds_to_time(self, seconds: float) -> str:
        """将秒数转换为时间字符串"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    async def _get_baidu_access_token(self) -> str:
        """获取百度API访问令牌"""
        try:
            url = "https://aip.baidubce.com/oauth/2.0/token"
            
            params = {
                "grant_type": "client_credentials",
                "client_id": settings.BAIDU_API_KEY,
                "client_secret": settings.BAIDU_SECRET_KEY
            }
            
            response = requests.post(url, params=params, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if "access_token" in result:
                return result["access_token"]
            else:
                raise ValueError(f"获取access_token失败: {result}")
                
        except Exception as e:
            logger.error(f"获取百度access_token失败: {e}")
            raise 