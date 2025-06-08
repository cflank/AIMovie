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
            "professional": "专业而富有文采的解说风格，用词精准优雅，语调沉稳有力，如学者般深邃，如诗人般优美",
            "humorous": "幽默风趣而不失文雅的解说风格，巧用比喻和双关，在轻松中蕴含智慧，在诙谐中传递深意",
            "emotional": "情感丰沛如潮水般的解说风格，用细腻的笔触描绘心灵的波澜，让每个字都带着温度和情感",
            "suspenseful": "悬疑紧张而富有诗意的解说风格，在神秘中编织美感，在紧张中营造诗意的氛围",
            "casual": "轻松自然而不失文采的解说风格，如春风化雨般亲切，如邻家智者般温暖而有深度",
            "dramatic": "戏剧化而充满文学张力的解说风格，如莎士比亚的独白般富有表现力，在激情中展现文字的魅力"
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
            prompt = f"""请深度扮演"{character_name}"这个角色，以第一人称的视角，创作富有文采和内心深度的解说词。

角色深度设定：
- 你是"{character_name}"，拥有独特的人格魅力和思想深度
- 以第一人称（我、我们）的内心独白形式来解说
- 展现角色的哲学思考和人生感悟
- 表达角色内心最真实、最深层的情感波动

字幕内容：
{subtitle_text}

内容分析：
- 主要主题：{', '.join(themes) if themes else '无'}
- 情感色彩：{', '.join(emotions) if emotions else '无'}
- 出现角色：{', '.join(characters) if characters else '无'}
- 关键词汇：{', '.join(key_phrases[:10]) if key_phrases else '无'}

角色解说创作要求：
1. 内心独白的文学性：
   - 运用内心独白的诗意表达
   - 展现角色的哲学思辨和人生感悟
   - 用富有文采的语言表达内心世界
   - 体现角色独特的思维方式和价值观

2. 情感深度挖掘：
   - 深入探索角色的内心冲突和矛盾
   - 表达角色对生活、爱情、友情的深层理解
   - 展现角色在关键时刻的心路历程
   - 用细腻的笔触描绘情感的微妙变化

3. 个性化表达：
   - 体现"{character_name}"独特的说话风格
   - 融入角色的人生阅历和智慧
   - 展现角色的文化修养和思想境界
   - 用角色特有的视角重新诠释事件

4. 风格特色：{style_prompts.get(style, '专业严肃')}
5. 目标观众：{audience_prompts.get(target_audience, '普通大众')}

角色内心独白示例风格：
- "我静静地看着这一切，心中涌起千般滋味，如同秋日的落叶，每一片都承载着不同的记忆..."
- "在这个瞬间，我突然明白了什么叫做成长，它不是年龄的增长，而是心灵的蜕变..."
- "我想，人生就像一场戏，而我们都是自己故事的主角，也是别人故事的配角..."

请生成解说词，格式如下：
[时间段] 解说内容...

创作要点：
- 每段解说都要体现"{character_name}"的独特人格魅力
- 用第一人称的内心独白形式，展现深层的思考和感悟
- 避免简单的事件描述，要有哲学思辨和人生感悟
- 语言要有文学性和诗意，体现角色的文化修养
- 展现角色在不同情境下的心理变化和成长轨迹
- 让观众感受到角色内心世界的丰富和深邃"""
        else:
            # 第三方视角模式
            prompt = f"""请以专业解说员的身份，根据以下字幕内容生成富有文采和深度的解说词。

字幕内容：
{subtitle_text}

内容分析：
- 主要主题：{', '.join(themes) if themes else '无'}
- 情感色彩：{', '.join(emotions) if emotions else '无'}
- 出现角色：{', '.join(characters) if characters else '无'}
- 关键词汇：{', '.join(key_phrases[:10]) if key_phrases else '无'}

解说创作要求：
1. 文采要求：
   - 使用优美的修辞手法（比喻、拟人、排比等）
   - 运用富有诗意的语言表达
   - 适当引用经典名句或哲理
   - 语言要有节奏感和韵律美

2. 深度解读：
   - 挖掘台词背后的深层含义
   - 分析人物心理和情感变化
   - 揭示情节的象征意义和隐喻
   - 提供文化背景和社会意义的解读

3. 创意表达：
   - 避免简单重述台词内容
   - 用独特的视角重新诠释情节
   - 加入富有想象力的描述
   - 营造画面感和氛围感

4. 风格特色：{style_prompts.get(style, '专业严肃')}
5. 目标观众：{audience_prompts.get(target_audience, '普通大众')}

解说创作示例风格：
- "在这个瞬间，时光仿佛凝固，两颗心灵在无声中碰撞..."
- "命运的齿轮开始转动，每一句话都如蝴蝶振翅，掀起未来的风暴..."
- "镜头背后，是人性的光辉与阴霾交织的复杂画卷..."

请生成解说词，格式如下：
[时间段] 解说内容...

创作要点：
- 每段解说都要有独特的文学色彩
- 深入挖掘台词的内在含义和情感层次
- 用诗意的语言描绘情感和氛围
- 提供超越表面的深度思考
- 让观众感受到文字的美感和思想的深度
- 绝对避免简单的台词复述或平铺直叙"""
        
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
                            "content": "你是一位才华横溢的文学解说大师，拥有深厚的文学功底和哲学思辨能力。你擅长用富有诗意和文采的语言，将简单的台词转化为深刻而优美的解说词，让观众在欣赏视频的同时，也能感受到文字的魅力和思想的深度。你的解说不仅仅是对内容的描述，更是对人性、情感和生活的深度思考与艺术表达。"
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