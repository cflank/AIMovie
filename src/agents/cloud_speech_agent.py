import asyncio
import json
from typing import Optional, Dict, Any
from xfyun_api import XfyunASR, XfyunTTS
from baidu_aip import AipSpeech

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