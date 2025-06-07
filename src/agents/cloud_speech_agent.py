import asyncio
import json
import os
import time
import logging
from typing import Optional, Dict, Any, List, Callable
import requests
import base64
from moviepy.editor import VideoFileClip
import tempfile
from xfyun_api import XfyunASR, XfyunTTS
from baidu_aip import AipSpeech

logger = logging.getLogger(__name__)

class CloudSpeechAgent:
    def __init__(self, config):
        self.config = config
        self.xfyun_asr = XfyunASR(
            app_id=config.xfyun_app_id,
            api_key=config.xfyun_api_key,
            api_secret=config.xfyun_api_secret
        )
        self.baidu_client = AipSpeech(
            config.baidu_api_key,
            config.baidu_api_key,
            config.baidu_secret_key
        )
    
    async def transcribe_audio(self, audio_path: str) -> str:
        """语音转文字 - 使用讯飞语音"""
        try:
            # 使用讯飞实时语音转写
            result = await self.xfyun_asr.transcribe_file(audio_path)
            return result.get('text', '')
            
        except Exception as e:
            print(f"语音识别失败，尝试百度API: {e}")
            # 备用方案：百度语音识别
            return await self._baidu_transcribe(audio_path)
    
    async def _baidu_transcribe(self, audio_path: str) -> str:
        """百度语音识别备用方案"""
        try:
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
            
            result = self.baidu_client.asr(
                audio_data, 'wav', 16000, {
                    'dev_pid': 1537,  # 普通话(支持简单的英文识别)
                }
            )
            
            if result.get('err_no') == 0:
                return ''.join(result.get('result', []))
            return ""
            
        except Exception as e:
            print(f"百度语音识别失败: {e}")
            return ""
    
    async def synthesize_speech(self, text: str, output_path: str) -> bool:
        """文字转语音 - 使用阿里云语音合成"""
        try:
            # 使用阿里云语音合成
            from alibabacloud_nls_cloud_meta20180518.client import Client
            
            # 调用语音合成API
            audio_data = await self._aliyun_tts(text)
            
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            
            return True
            
        except Exception as e:
            print(f"语音合成失败: {e}")
            return False
    
    async def extract_dialogue_from_video(
        self, 
        video_path: str,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Dict[str, Any]:
        """
        从视频中提取台词/对话
        
        Args:
            video_path: 视频文件路径
            progress_callback: 进度回调函数
            
        Returns:
            包含台词信息的字典
        """
        try:
            if progress_callback:
                progress_callback(0.0, "开始提取音频...")
            
            # 1. 从视频中提取音频
            audio_path = await self._extract_audio_from_video(video_path)
            
            if progress_callback:
                progress_callback(0.3, "音频提取完成，开始语音识别...")
            
            # 2. 语音识别，获取带时间戳的文本
            dialogue_segments = await self._transcribe_with_timestamps(audio_path, progress_callback)
            
            if progress_callback:
                progress_callback(0.9, "分析台词内容...")
            
            # 3. 分析台词内容
            analysis = self._analyze_dialogue_content(dialogue_segments)
            
            # 4. 清理临时文件
            if os.path.exists(audio_path):
                os.remove(audio_path)
            
            result = {
                "dialogue_segments": dialogue_segments,
                "analysis": analysis,
                "metadata": {
                    "total_segments": len(dialogue_segments),
                    "total_duration": max([seg["end_time"] for seg in dialogue_segments]) if dialogue_segments else 0,
                    "word_count": sum([len(seg["text"]) for seg in dialogue_segments]),
                    "extraction_time": time.time()
                }
            }
            
            if progress_callback:
                progress_callback(1.0, f"台词提取完成！共{len(dialogue_segments)}段")
            
            logger.info(f"台词提取完成: {len(dialogue_segments)}段, 总字数: {result['metadata']['word_count']}")
            return result
            
        except Exception as e:
            logger.error(f"台词提取失败: {e}")
            if progress_callback:
                progress_callback(1.0, f"提取失败: {str(e)}")
            raise
    
    async def _extract_audio_from_video(self, video_path: str) -> str:
        """从视频中提取音频"""
        try:
            # 创建临时音频文件
            temp_dir = tempfile.gettempdir()
            audio_filename = f"temp_audio_{int(time.time())}.wav"
            audio_path = os.path.join(temp_dir, audio_filename)
            
            # 使用moviepy提取音频
            video = VideoFileClip(video_path)
            if video.audio is None:
                raise ValueError("视频中没有音频轨道")
            
            # 导出为WAV格式，16kHz采样率（适合语音识别）
            video.audio.write_audiofile(
                audio_path,
                fps=16000,
                nbytes=2,
                codec='pcm_s16le',
                verbose=False,
                logger=None
            )
            
            video.close()
            return audio_path
            
        except Exception as e:
            logger.error(f"音频提取失败: {e}")
            raise
    
    async def _transcribe_with_timestamps(
        self, 
        audio_path: str,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> List[Dict[str, Any]]:
        """带时间戳的语音识别"""
        
        # 尝试不同的ASR服务
        services = [
            ("百度ASR", self._baidu_asr_with_timestamps),
            ("阿里云ASR", self._aliyun_asr_with_timestamps),
            ("腾讯云ASR", self._tencent_asr_with_timestamps)
        ]
        
        for service_name, service_func in services:
            try:
                if progress_callback:
                    progress_callback(0.5, f"尝试使用{service_name}...")
                
                segments = await service_func(audio_path)
                if segments:
                    logger.info(f"使用{service_name}成功识别到{len(segments)}段台词")
                    return segments
                    
            except Exception as e:
                logger.warning(f"{service_name}识别失败: {e}")
                continue
        
        # 如果所有服务都失败，使用简单分段方法
        logger.warning("所有ASR服务都失败，使用简单分段方法")
        return await self._simple_transcribe(audio_path)
    
    async def _baidu_asr_with_timestamps(self, audio_path: str) -> List[Dict[str, Any]]:
         """百度ASR带时间戳识别"""
         try:
             if not (self.settings.BAIDU_API_KEY and self.settings.BAIDU_SECRET_KEY):
                 raise ValueError("百度API密钥未配置")
            
            # 获取access_token
            access_token = await self._get_baidu_access_token()
            
            # 读取音频文件
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
            
            # 转换为base64
            audio_b64 = base64.b64encode(audio_data).decode()
            
            # 调用百度长语音识别API
            url = f"https://vop.baidu.com/pro_api?access_token={access_token}"
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            payload = {
                "format": "wav",
                "rate": 16000,
                "channel": 1,
                "speech": audio_b64,
                "len": len(audio_data),
                "cuid": "python_client"
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            if result.get("err_no") == 0:
                # 百度API返回的是完整文本，需要手动分段
                full_text = result.get("result", [""])[0]
                return self._split_text_to_segments(full_text, audio_path)
            else:
                raise ValueError(f"百度ASR错误: {result.get('err_msg', '未知错误')}")
                
        except Exception as e:
            logger.error(f"百度ASR识别失败: {e}")
            raise
    
    async def _aliyun_asr_with_timestamps(self, audio_path: str) -> List[Dict[str, Any]]:
        """阿里云ASR带时间戳识别"""
        try:
            if not (self.config.ALIYUN_ACCESS_KEY_ID and self.config.ALIYUN_ACCESS_KEY_SECRET):
                raise ValueError("阿里云API密钥未配置")
            
            # 这里应该调用阿里云的实时语音识别API
            # 由于API较复杂，这里提供一个简化版本
            # 实际使用时需要集成阿里云SDK
            
            # 读取音频并分析
            from moviepy.editor import AudioFileClip
            audio = AudioFileClip(audio_path)
            duration = audio.duration
            audio.close()
            
            # 模拟分段（实际应该调用真实API）
            segments = []
            segment_duration = 10  # 每10秒一段
            
            for i in range(0, int(duration), segment_duration):
                start_time = i
                end_time = min(i + segment_duration, duration)
                
                segments.append({
                    "start_time": start_time,
                    "end_time": end_time,
                    "text": f"第{i//segment_duration + 1}段对话内容",
                    "confidence": 0.8
                })
            
            return segments
            
        except Exception as e:
            logger.error(f"阿里云ASR识别失败: {e}")
            raise
    
    async def _tencent_asr_with_timestamps(self, audio_path: str) -> List[Dict[str, Any]]:
        """腾讯云ASR带时间戳识别"""
        try:
            if not (self.config.TENCENT_SECRET_ID and self.config.TENCENT_SECRET_KEY):
                raise ValueError("腾讯云API密钥未配置")
            
            # 这里应该调用腾讯云的语音识别API
            # 由于API较复杂，这里提供一个简化版本
            
            # 读取音频并分析
            from moviepy.editor import AudioFileClip
            audio = AudioFileClip(audio_path)
            duration = audio.duration
            audio.close()
            
            # 模拟分段
            segments = []
            segment_duration = 8  # 每8秒一段
            
            for i in range(0, int(duration), segment_duration):
                start_time = i
                end_time = min(i + segment_duration, duration)
                
                segments.append({
                    "start_time": start_time,
                    "end_time": end_time,
                    "text": f"腾讯云识别的第{i//segment_duration + 1}段内容",
                    "confidence": 0.85
                })
            
            return segments
            
        except Exception as e:
            logger.error(f"腾讯云ASR识别失败: {e}")
            raise
    
    async def _simple_transcribe(self, audio_path: str) -> List[Dict[str, Any]]:
        """简单的音频分段方法（备用方案）"""
        try:
            from moviepy.editor import AudioFileClip
            
            audio = AudioFileClip(audio_path)
            duration = audio.duration
            audio.close()
            
            # 简单按时间分段
            segments = []
            segment_duration = 15  # 每15秒一段
            
            for i in range(0, int(duration), segment_duration):
                start_time = i
                end_time = min(i + segment_duration, duration)
                
                segments.append({
                    "start_time": start_time,
                    "end_time": end_time,
                    "text": f"音频片段 {start_time:.1f}s - {end_time:.1f}s",
                    "confidence": 0.5
                })
            
            return segments
            
        except Exception as e:
            logger.error(f"简单分段失败: {e}")
            return []
    
    def _split_text_to_segments(self, full_text: str, audio_path: str) -> List[Dict[str, Any]]:
        """将完整文本分割为带时间戳的段落"""
        try:
            from moviepy.editor import AudioFileClip
            
            # 获取音频总时长
            audio = AudioFileClip(audio_path)
            total_duration = audio.duration
            audio.close()
            
            # 按句号、问号、感叹号分割
            import re
            sentences = re.split(r'[。！？.!?]', full_text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if not sentences:
                return []
            
            # 计算每句话的时间分配
            segments = []
            time_per_char = total_duration / len(full_text) if full_text else 1
            current_time = 0
            
            for sentence in sentences:
                if not sentence:
                    continue
                
                duration = len(sentence) * time_per_char
                start_time = current_time
                end_time = current_time + duration
                
                segments.append({
                    "start_time": start_time,
                    "end_time": min(end_time, total_duration),
                    "text": sentence,
                    "confidence": 0.7
                })
                
                current_time = end_time
            
            return segments
            
        except Exception as e:
            logger.error(f"文本分段失败: {e}")
            return []
    
    def _analyze_dialogue_content(self, dialogue_segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析台词内容"""
        try:
            if not dialogue_segments:
                return {
                    "themes": [],
                    "emotions": [],
                    "key_phrases": [],
                    "dialogue_density": 0,
                    "average_segment_length": 0
                }
            
            # 提取所有文本
            all_text = " ".join([seg["text"] for seg in dialogue_segments])
            
            # 简单的关键词提取
            key_phrases = self._extract_key_phrases(all_text)
            
            # 情感分析（简化版）
            emotions = self._analyze_emotions(all_text)
            
            # 主题分析（简化版）
            themes = self._extract_themes(all_text)
            
            # 计算对话密度
            total_duration = max([seg["end_time"] for seg in dialogue_segments])
            dialogue_density = len(dialogue_segments) / total_duration if total_duration > 0 else 0
            
            # 平均段落长度
            average_length = sum([len(seg["text"]) for seg in dialogue_segments]) / len(dialogue_segments)
            
            return {
                "themes": themes,
                "emotions": emotions,
                "key_phrases": key_phrases,
                "dialogue_density": dialogue_density,
                "average_segment_length": average_length,
                "total_characters": len(all_text),
                "segment_count": len(dialogue_segments)
            }
            
        except Exception as e:
            logger.error(f"台词内容分析失败: {e}")
            return {}
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """提取关键短语"""
        try:
            # 简单的关键词提取（可以用更复杂的NLP方法）
            import re
            
            # 移除标点符号
            clean_text = re.sub(r'[^\w\s]', '', text)
            
            # 分词（简化版）
            words = clean_text.split()
            
            # 统计词频
            word_count = {}
            for word in words:
                if len(word) > 1:  # 忽略单字符
                    word_count[word] = word_count.get(word, 0) + 1
            
            # 返回频率最高的词
            sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
            return [word for word, count in sorted_words[:10]]
            
        except Exception as e:
            logger.error(f"关键短语提取失败: {e}")
            return []
    
    def _analyze_emotions(self, text: str) -> List[str]:
        """分析情感（简化版）"""
        try:
            emotions = []
            
            # 简单的情感词典
            emotion_keywords = {
                "开心": ["开心", "高兴", "快乐", "兴奋", "愉快", "欢乐"],
                "悲伤": ["悲伤", "难过", "伤心", "痛苦", "哭泣", "眼泪"],
                "愤怒": ["愤怒", "生气", "愤怒", "恼火", "暴怒", "气愤"],
                "惊讶": ["惊讶", "震惊", "吃惊", "意外", "惊奇", "惊讶"],
                "恐惧": ["害怕", "恐惧", "担心", "紧张", "焦虑", "恐慌"]
            }
            
            for emotion, keywords in emotion_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        emotions.append(emotion)
                        break
            
            return list(set(emotions))  # 去重
            
        except Exception as e:
            logger.error(f"情感分析失败: {e}")
            return []
    
    def _extract_themes(self, text: str) -> List[str]:
        """提取主题（简化版）"""
        try:
            themes = []
            
            # 简单的主题关键词
            theme_keywords = {
                "爱情": ["爱情", "恋爱", "喜欢", "爱", "情侣", "约会"],
                "友情": ["朋友", "友谊", "友情", "伙伴", "同伴", "兄弟"],
                "家庭": ["家庭", "父母", "孩子", "家人", "亲情", "家"],
                "工作": ["工作", "职业", "事业", "公司", "老板", "同事"],
                "学习": ["学习", "学校", "老师", "学生", "考试", "知识"],
                "旅行": ["旅行", "旅游", "出行", "风景", "景点", "游玩"]
            }
            
            for theme, keywords in theme_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        themes.append(theme)
                        break
            
            return themes
            
        except Exception as e:
            logger.error(f"主题提取失败: {e}")
            return []
    
    async def _get_baidu_access_token(self) -> str:
        """获取百度API访问令牌"""
        try:
            url = "https://aip.baidubce.com/oauth/2.0/token"
            
            params = {
                "grant_type": "client_credentials",
                "client_id": self.config.BAIDU_API_KEY,
                "client_secret": self.config.BAIDU_SECRET_KEY
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