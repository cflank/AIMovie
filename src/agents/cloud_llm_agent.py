import asyncio
import json
from typing import List, Dict, Any
import requests
from openai import AsyncOpenAI

class CloudLLMAgent:
    def __init__(self, config):
        self.config = config
        # 支持多个LLM提供商
        self.providers = {
            'qwen': self._init_qwen_client(),
            'ernie': self._init_ernie_client(),
            'gpt': self._init_gpt_client(),
        }
        self.primary_provider = 'qwen'  # 性价比最高
    
    def _init_qwen_client(self):
        """初始化通义千问客户端"""
        return {
            'api_key': self.config.aliyun_access_key,
            'endpoint': 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'
        }
    
    def _init_ernie_client(self):
        """初始化文心一言客户端"""
        return {
            'api_key': self.config.baidu_api_key,
            'secret_key': self.config.baidu_secret_key,
            'endpoint': 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions'
        }
    
    async def generate_narration(self, 
                               video_analysis: Dict[str, Any],
                               audio_transcript: str = "") -> str:
        """生成视频旁白"""
        prompt = self._build_narration_prompt(video_analysis, audio_transcript)
        
        # 优先使用通义千问（性价比最高）
        try:
            return await self._call_qwen(prompt)
        except Exception as e:
            print(f"通义千问调用失败，切换到文心一言: {e}")
            return await self._call_ernie(prompt)
    
    def _build_narration_prompt(self, video_analysis: Dict, transcript: str) -> str:
        """构建旁白生成提示词"""
        scenes = video_analysis.get('scenes', [])
        objects = video_analysis.get('objects', [])
        
        prompt = f"""
        请为以下视频内容生成专业的旁白解说：
        
        视频场景分析：
        {json.dumps(scenes, ensure_ascii=False, indent=2)}
        
        检测到的物体：
        {json.dumps(objects, ensure_ascii=False, indent=2)}
        
        原始音频内容：
        {transcript}
        
        要求：
        1. 语言生动有趣，适合大众观看
        2. 突出视频的关键信息和亮点
        3. 保持客观中性的叙述风格
        4. 控制在2-3分钟的语音长度
        5. 分段输出，便于语音合成
        
        请直接输出旁白文本，用"||"分隔不同段落：
        """
        
        return prompt
    
    async def _call_qwen(self, prompt: str) -> str:
        """调用通义千问API"""
        headers = {
            'Authorization': f'Bearer {self.providers["qwen"]["api_key"]}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'qwen-turbo',  # 性价比最高的模型
            'input': {
                'messages': [
                    {'role': 'user', 'content': prompt}
                ]
            },
            'parameters': {
                'max_tokens': 2000,
                'temperature': 0.7
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.providers['qwen']['endpoint'],
                headers=headers,
                json=data
            ) as response:
                result = await response.json()
                return result['output']['text']
    
    async def _call_ernie(self, prompt: str) -> str:
        """调用文心一言API（备用方案）"""
        # 获取access_token
        token_url = "https://aip.baidubce.com/oauth/2.0/token"
        token_params = {
            'grant_type': 'client_credentials',
            'client_id': self.providers['ernie']['api_key'],
            'client_secret': self.providers['ernie']['secret_key']
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, params=token_params) as response:
                token_result = await response.json()
                access_token = token_result['access_token']
            
            # 调用文心一言
            chat_url = f"{self.providers['ernie']['endpoint']}?access_token={access_token}"
            chat_data = {
                'messages': [
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.7,
                'max_output_tokens': 2000
            }
            
            async with session.post(chat_url, json=chat_data) as response:
                result = await response.json()
                return result['result']