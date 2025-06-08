import asyncio
import base64
import json
import logging
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
import requests
import hashlib
import hmac
from datetime import datetime

try:
    from ..config.cloud_settings import settings
    from ..utils.audio_utils import merge_audio_files
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from src.config.cloud_settings import settings
    from src.utils.audio_utils import merge_audio_files

logger = logging.getLogger(__name__)

class CloudTTSAgent:
    """云端TTS Agent - 支持阿里云和腾讯云语音合成"""
    
    def __init__(self):
        self.temp_dir = settings.TEMP_DIR
        self.temp_dir.mkdir(exist_ok=True)
    
    def _generate_aliyun_signature(self, params: Dict[str, str]) -> str:
        """生成阿里云签名"""
        try:
            # 按字典序排序参数
            sorted_params = sorted(params.items())
            
            # 构建查询字符串
            query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
            
            # 构建待签名字符串
            string_to_sign = f"POST&%2F&{requests.utils.quote(query_string, safe='')}"
            
            # 计算签名
            signing_key = settings.ALIYUN_ACCESS_KEY_SECRET + "&"
            signature = base64.b64encode(
                hmac.new(
                    signing_key.encode('utf-8'),
                    string_to_sign.encode('utf-8'),
                    hashlib.sha1
                ).digest()
            ).decode('utf-8')
            
            return signature
            
        except Exception as e:
            logger.error(f"生成阿里云签名失败: {e}")
            raise
    
    def _generate_tencent_signature(self, params: Dict[str, str]) -> str:
        """生成腾讯云签名"""
        try:
            # 腾讯云API 3.0签名算法
            algorithm = "TC3-HMAC-SHA256"
            service = "tts"
            version = "2019-08-23"
            action = "TextToVoice"
            region = settings.TENCENT_TTS_REGION
            
            # 时间戳
            timestamp = int(time.time())
            date = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')
            
            # 构建规范请求串
            http_request_method = "POST"
            canonical_uri = "/"
            canonical_querystring = ""
            canonical_headers = f"content-type:application/json; charset=utf-8\nhost:tts.tencentcloudapi.com\n"
            signed_headers = "content-type;host"
            payload = json.dumps(params)
            hashed_request_payload = hashlib.sha256(payload.encode("utf-8")).hexdigest()
            canonical_request = f"{http_request_method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{hashed_request_payload}"
            
            # 构建待签名字符串
            credential_scope = f"{date}/{service}/tc3_request"
            hashed_canonical_request = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
            string_to_sign = f"{algorithm}\n{timestamp}\n{credential_scope}\n{hashed_canonical_request}"
            
            # 计算签名
            secret_date = hmac.new(("TC3" + settings.TENCENT_SECRET_KEY).encode("utf-8"), date.encode("utf-8"), hashlib.sha256).digest()
            secret_service = hmac.new(secret_date, service.encode("utf-8"), hashlib.sha256).digest()
            secret_signing = hmac.new(secret_service, "tc3_request".encode("utf-8"), hashlib.sha256).digest()
            signature = hmac.new(secret_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()
            
            # 构建Authorization
            authorization = f"{algorithm} Credential={settings.TENCENT_SECRET_ID}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
            
            return authorization, timestamp
            
        except Exception as e:
            logger.error(f"生成腾讯云签名失败: {e}")
            raise
    
    async def _synthesize_with_aliyun(
        self, 
        text: str, 
        voice: str = "xiaoyun",
        speed: float = 1.0,
        pitch: float = 1.0,
        volume: float = 1.0
    ) -> str:
        """使用阿里云TTS合成语音"""
        try:
            if not settings.ALIYUN_ACCESS_KEY_ID or not settings.ALIYUN_ACCESS_KEY_SECRET:
                raise ValueError("阿里云TTS密钥未配置")
            
            # 构建请求参数
            params = {
                "AccessKeyId": settings.ALIYUN_ACCESS_KEY_ID,
                "Action": "SpeechSynthesizer",
                "Format": "JSON",
                "RegionId": settings.ALIYUN_TTS_REGION,
                "SignatureMethod": "HMAC-SHA1",
                "SignatureNonce": str(uuid.uuid4()),
                "SignatureVersion": "1.0",
                "Text": text,
                "Timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                "Version": "2019-02-28",
                "Voice": voice,
                "SampleRate": "16000",
                "Format": "wav",
                "Volume": str(int(volume * 100)),
                "SpeechRate": str(int(speed * 100)),
                "PitchRate": str(int(pitch * 100))
            }
            
            # 生成签名
            signature = self._generate_aliyun_signature(params)
            params["Signature"] = signature
            
            # 发送请求
            url = f"https://nls-meta.cn-shanghai.aliyuncs.com/"
            
            response = requests.post(url, data=params, timeout=60)
            response.raise_for_status()
            
            # 保存音频文件
            output_path = self.temp_dir / f"aliyun_tts_{int(time.time())}.wav"
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"阿里云TTS合成失败: {e}")
            raise
    
    async def _synthesize_with_tencent(
        self,
        text: str,
        voice: str = "101001",  # 智瑜
        speed: float = 1.0,
        volume: float = 1.0
    ) -> str:
        """使用腾讯云TTS合成语音"""
        try:
            if not settings.TENCENT_SECRET_ID or not settings.TENCENT_SECRET_KEY:
                raise ValueError("腾讯云TTS密钥未配置")
            
            # 构建请求参数
            params = {
                "Text": text,
                "SessionId": str(uuid.uuid4()),
                "VoiceType": int(voice),
                "Codec": "wav",
                "SampleRate": 16000,
                "Speed": speed,
                "Volume": volume,
                "PrimaryLanguage": 1  # 中文
            }
            
            # 生成签名
            authorization, timestamp = self._generate_tencent_signature(params)
            
            # 构建请求头
            headers = {
                "Authorization": authorization,
                "Content-Type": "application/json; charset=utf-8",
                "Host": "tts.tencentcloudapi.com",
                "X-TC-Action": "TextToVoice",
                "X-TC-Timestamp": str(timestamp),
                "X-TC-Version": "2019-08-23",
                "X-TC-Region": settings.TENCENT_TTS_REGION
            }
            
            # 发送请求
            url = "https://tts.tencentcloudapi.com/"
            
            response = requests.post(
                url, 
                headers=headers, 
                data=json.dumps(params),
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            
            if "Response" in result and "Audio" in result["Response"]:
                # 解码音频数据
                audio_data = base64.b64decode(result["Response"]["Audio"])
                
                # 保存音频文件
                output_path = self.temp_dir / f"tencent_tts_{int(time.time())}.wav"
                with open(output_path, "wb") as f:
                    f.write(audio_data)
                
                return str(output_path)
            else:
                raise ValueError(f"腾讯云TTS响应异常: {result}")
                
        except Exception as e:
            logger.error(f"腾讯云TTS合成失败: {e}")
            raise
    
    async def _synthesize_with_edge(
        self,
        text: str,
        voice: str = "zh-CN-XiaoxiaoNeural",
        rate: str = "+0%",
        pitch: str = "+0Hz",
        volume: str = "+0%"
    ) -> str:
        """使用Edge-TTS合成语音（免费备用方案）"""
        try:
            import edge_tts
            
            # 调整语音参数
            communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, volume=volume)
            
            # 保存音频文件
            output_path = self.temp_dir / f"edge_tts_{int(time.time())}.wav"
            await communicate.save(str(output_path))
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Edge-TTS合成失败: {e}")
            raise
    
    def _get_voice_mapping(self, service: str, voice_style: str) -> str:
        """获取不同服务的语音映射"""
        voice_mappings = {
            "aliyun": {
                "female_gentle": "xiaoyun",      # 小云，温柔女声
                "female_lively": "xiaogang",     # 小刚，活泼女声  
                "female_intellectual": "ruoxi",  # 若汐，知性女声
                "male_steady": "zhitian_emo",    # 志天，沉稳男声
                "male_young": "zhiqi_emo",       # 志琪，年轻男声
                "male_magnetic": "zhichen_emo"   # 志辰，磁性男声
            },
            "tencent": {
                "female_gentle": "101001",       # 智瑜，温柔女声
                "female_lively": "101002",       # 智聆，活泼女声
                "female_intellectual": "101003", # 智美，知性女声
                "male_steady": "101004",         # 智云，沉稳男声
                "male_young": "101005",          # 智莉，年轻男声
                "male_magnetic": "101006"        # 智言，磁性男声
            },
            "edge": {
                "female_gentle": "zh-CN-XiaoxiaoNeural",     # 晓晓，温柔
                "female_lively": "zh-CN-XiaohanNeural",      # 晓涵，活泼
                "female_intellectual": "zh-CN-XiaomengNeural", # 晓梦，知性
                "male_steady": "zh-CN-YunxiNeural",          # 云希，沉稳
                "male_young": "zh-CN-YunjianNeural",         # 云健，年轻
                "male_magnetic": "zh-CN-YunxiaNeural"        # 云夏，磁性
            }
        }
        
        return voice_mappings.get(service, {}).get(voice_style, "")
    
    async def synthesize_speech(
        self,
        text: str,
        voice_style: str = "female_gentle",
        speed: float = 1.0,
        pitch: float = 1.0,
        volume: float = 1.0,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> str:
        """
        合成语音
        
        Args:
            text: 要合成的文本
            voice_style: 语音风格
            speed: 语速 (0.5-2.0)
            pitch: 音调 (0.5-2.0)
            volume: 音量 (0.5-2.0)
            progress_callback: 进度回调函数
            
        Returns:
            音频文件路径
        """
        try:
            if progress_callback:
                progress_callback(0.0, "开始语音合成...")
            
            if not text.strip():
                raise ValueError("合成文本不能为空")
            
            # 获取可用的TTS服务
            available_services = settings.get_available_tts_services()
            logger.info(f"可用TTS服务: {available_services}")
            logger.info(f"服务类型: {type(available_services)}")
            
            if not available_services:
                raise ValueError("没有可用的TTS服务")
            
            # 按优先级尝试合成
            for i, service in enumerate(available_services):
                logger.info(f"处理服务 {i}: {service}, 类型: {type(service)}")
                
                # 处理服务名称映射
                if isinstance(service, dict):
                    service_name = service["name"]
                    display_name = service.get("display_name", service_name)
                else:
                    # 字符串格式，需要映射到内部服务名
                    service_display_name = service
                    service_name_mapping = {
                        "阿里云TTS": "aliyun",
                        "腾讯TTS": "tencent", 
                        "Edge-TTS": "edge"
                    }
                    service_name = service_name_mapping.get(service, service.lower())
                    display_name = service
                
                try:
                    if progress_callback:
                        progress_callback(0.2 + i * 0.3, f"使用{display_name}合成...")
                    
                    voice = self._get_voice_mapping(service_name, voice_style)
                    if not voice:
                        logger.warning(f"{service_name}不支持语音风格: {voice_style}")
                        continue
                    
                    audio_path = ""
                    
                    if service_name == "aliyun":
                        audio_path = await self._synthesize_with_aliyun(
                            text, voice, speed, pitch, volume
                        )
                    elif service_name == "tencent":
                        audio_path = await self._synthesize_with_tencent(
                            text, voice, speed, volume
                        )
                    elif service_name == "edge":
                        # Edge-TTS参数格式不同
                        rate = f"{int((speed - 1) * 100):+d}%"
                        pitch_hz = f"{int((pitch - 1) * 50):+d}Hz"
                        vol = f"{int((volume - 1) * 100):+d}%"
                        
                        audio_path = await self._synthesize_with_edge(
                            text, voice, rate, pitch_hz, vol
                        )
                    
                    if audio_path and Path(audio_path).exists():
                        if progress_callback:
                            progress_callback(1.0, f"语音合成完成! 使用{display_name}")
                        
                        logger.info(f"语音合成成功: {display_name}, 文件: {audio_path}")
                        return audio_path
                    
                except Exception as e:
                    logger.warning(f"{display_name}合成失败: {e}")
                    continue
            
            raise ValueError("所有TTS服务都失败了")
            
        except Exception as e:
            logger.error(f"语音合成失败: {e}")
            if progress_callback:
                progress_callback(1.0, f"合成失败: {str(e)}")
            raise
    
    async def synthesize_narration(
        self,
        narration_segments: List[Dict[str, Any]],
        voice_style: str = "female_gentle",
        speed: float = 1.0,
        pitch: float = 1.0,
        volume: float = 1.0,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> List[Dict[str, Any]]:
        """
        为解说段落批量合成语音
        
        Args:
            narration_segments: 解说段落列表
            voice_style: 语音风格
            speed: 语速
            pitch: 音调
            volume: 音量
            progress_callback: 进度回调函数
            
        Returns:
            包含音频文件路径的段落列表
        """
        try:
            if progress_callback:
                progress_callback(0.0, "开始批量语音合成...")
            
            if not narration_segments:
                raise ValueError("解说段落不能为空")
            
            synthesized_segments = []
            total_segments = len(narration_segments)
            
            for i, segment in enumerate(narration_segments):
                try:
                    if progress_callback:
                        progress = (i / total_segments) * 0.9
                        progress_callback(progress, f"合成第{i+1}/{total_segments}段...")
                    
                    # 添加调试信息
                    logger.info(f"处理第{i+1}段: {type(segment)}, 内容: {segment}")
                    
                    text = segment.get("text", segment.get("content", "")).strip()
                    if not text:
                        logger.warning(f"第{i+1}段内容为空，跳过")
                        continue
                    
                    # 合成单段语音
                    audio_path = await self.synthesize_speech(
                        text, voice_style, speed, pitch, volume
                    )
                    
                    # 添加音频路径到段落信息
                    segment_with_audio = segment.copy()
                    segment_with_audio["audio_path"] = audio_path
                    segment_with_audio["audio_duration"] = await self._get_audio_duration(audio_path)
                    
                    synthesized_segments.append(segment_with_audio)
                    
                    # 避免API调用过于频繁
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"第{i+1}段合成失败: {e}")
                    # 继续处理下一段
                    continue
            
            if progress_callback:
                progress_callback(1.0, f"批量合成完成! 成功{len(synthesized_segments)}段")
            
            logger.info(f"批量语音合成完成: {len(synthesized_segments)}/{total_segments}段成功")
            return synthesized_segments
            
        except Exception as e:
            logger.error(f"批量语音合成失败: {e}")
            if progress_callback:
                progress_callback(1.0, f"批量合成失败: {str(e)}")
            raise
    
    async def _get_audio_duration(self, audio_path: str) -> float:
        """获取音频时长"""
        try:
            import librosa
            y, sr = librosa.load(audio_path)
            return len(y) / sr
        except Exception as e:
            logger.warning(f"获取音频时长失败: {e}")
            return 0.0
    
    async def merge_narration_audio(
        self,
        synthesized_segments: List[Dict[str, Any]],
        output_path: str,
        background_music: Optional[str] = None,
        music_volume: float = 0.3,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> str:
        """
        合并解说音频段落
        
        Args:
            synthesized_segments: 已合成的解说段落
            output_path: 输出文件路径
            background_music: 背景音乐文件路径
            music_volume: 背景音乐音量
            progress_callback: 进度回调函数
            
        Returns:
            合并后的音频文件路径
        """
        try:
            if progress_callback:
                progress_callback(0.0, "开始合并音频...")
            
            if not synthesized_segments:
                raise ValueError("没有可合并的音频段落")
            
            # 提取音频文件路径和时间信息
            audio_files = []
            for segment in synthesized_segments:
                if "audio_path" in segment and Path(segment["audio_path"]).exists():
                    audio_files.append({
                        "path": segment["audio_path"],
                        "timestamp": segment.get("timestamp", 0),
                        "duration": segment.get("duration", 5)
                    })
            
            if not audio_files:
                raise ValueError("没有有效的音频文件")
            
            if progress_callback:
                progress_callback(0.5, f"合并{len(audio_files)}个音频文件...")
            
            # 使用音频工具合并
            merged_path = await merge_audio_files(
                audio_files, 
                output_path,
                background_music,
                music_volume
            )
            
            if progress_callback:
                progress_callback(1.0, "音频合并完成!")
            
            logger.info(f"解说音频合并完成: {merged_path}")
            return merged_path
            
        except Exception as e:
            logger.error(f"音频合并失败: {e}")
            if progress_callback:
                progress_callback(1.0, f"合并失败: {str(e)}")
            raise
    
    def get_available_voices(self) -> Dict[str, List[Dict[str, str]]]:
        """获取可用的语音列表"""
        voices = {
            "female": [
                {"id": "female_gentle", "name": "温柔女声", "description": "声音温柔甜美，适合温馨内容"},
                {"id": "female_lively", "name": "活泼女声", "description": "声音活泼开朗，适合轻松内容"},
                {"id": "female_intellectual", "name": "知性女声", "description": "声音知性优雅，适合专业内容"}
            ],
            "male": [
                {"id": "male_steady", "name": "沉稳男声", "description": "声音沉稳有力，适合严肃内容"},
                {"id": "male_young", "name": "年轻男声", "description": "声音年轻活力，适合时尚内容"},
                {"id": "male_magnetic", "name": "磁性男声", "description": "声音磁性迷人，适合情感内容"}
            ]
        }
        
        return voices
    
    async def test_voice(
        self,
        voice_style: str,
        test_text: str = "这是一段测试语音，用来试听不同的声音效果。",
        speed: float = 1.0,
        pitch: float = 1.0,
        volume: float = 1.0
    ) -> str:
        """
        测试语音效果
        
        Args:
            voice_style: 语音风格
            test_text: 测试文本
            speed: 语速
            pitch: 音调
            volume: 音量
            
        Returns:
            测试音频文件路径
        """
        try:
            audio_path = await self.synthesize_speech(
                test_text, voice_style, speed, pitch, volume
            )
            
            logger.info(f"语音测试完成: {voice_style}, 文件: {audio_path}")
            return audio_path
            
        except Exception as e:
            logger.error(f"语音测试失败: {e}")
            raise 