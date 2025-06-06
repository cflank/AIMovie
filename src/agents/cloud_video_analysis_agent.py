import asyncio
import base64
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
import cv2
import requests
from PIL import Image
import io

try:
    from ..config.cloud_settings import settings
    from ..utils.video_utils import extract_frames_from_video, extract_audio_from_video
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from src.config.cloud_settings import settings
    from src.utils.video_utils import extract_frames_from_video, extract_audio_from_video

logger = logging.getLogger(__name__)

class CloudVideoAnalysisAgent:
    """云端视频分析Agent - 使用百度AI和通义千问-VL"""
    
    def __init__(self):
        self.baidu_access_token = None
        self.token_expires_at = 0
        
    async def _get_baidu_access_token(self) -> str:
        """获取百度AI访问令牌"""
        if self.baidu_access_token and time.time() < self.token_expires_at:
            return self.baidu_access_token
            
        if not settings.BAIDU_API_KEY or not settings.BAIDU_SECRET_KEY:
            raise ValueError("百度AI API密钥未配置")
            
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": settings.BAIDU_API_KEY,
            "client_secret": settings.BAIDU_SECRET_KEY
        }
        
        try:
            response = requests.post(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "access_token" in data:
                self.baidu_access_token = data["access_token"]
                self.token_expires_at = time.time() + data.get("expires_in", 3600) - 300  # 提前5分钟刷新
                return self.baidu_access_token
            else:
                raise ValueError(f"获取百度访问令牌失败: {data}")
                
        except Exception as e:
            logger.error(f"获取百度访问令牌失败: {e}")
            raise
    
    def _encode_image_to_base64(self, image_path: str) -> str:
        """将图片编码为base64"""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    
    async def _analyze_image_with_baidu(self, image_path: str) -> Dict[str, Any]:
        """使用百度AI分析图片"""
        try:
            access_token = await self._get_baidu_access_token()
            
            # 通用物体识别
            url = f"https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general?access_token={access_token}"
            
            image_b64 = self._encode_image_to_base64(image_path)
            
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = {'image': image_b64}
            
            response = requests.post(url, headers=headers, data=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if "result" in result:
                objects = []
                for item in result["result"]:
                    objects.append({
                        "name": item.get("keyword", ""),
                        "confidence": item.get("score", 0),
                        "description": item.get("root", "")
                    })
                
                return {
                    "objects": objects,
                    "scene_description": f"检测到{len(objects)}个物体",
                    "confidence": max([obj["confidence"] for obj in objects]) if objects else 0
                }
            else:
                logger.warning(f"百度AI分析结果异常: {result}")
                return {"objects": [], "scene_description": "分析失败", "confidence": 0}
                
        except Exception as e:
            logger.error(f"百度AI图片分析失败: {e}")
            return {"objects": [], "scene_description": "分析失败", "confidence": 0}
    
    async def _analyze_image_with_qwen_vl(self, image_path: str) -> Dict[str, Any]:
        """使用通义千问-VL分析图片"""
        try:
            if not settings.QWEN_VL_API_KEY:
                return {"objects": [], "scene_description": "通义千问-VL未配置", "confidence": 0}
            
            # 读取并编码图片
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()
            
            url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
            
            headers = {
                "Authorization": f"Bearer {settings.QWEN_VL_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "qwen-vl-plus",
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "image": f"data:image/jpeg;base64,{image_data}"
                                },
                                {
                                    "text": "请详细描述这张图片中的内容，包括主要物体、场景、人物动作等。用中文回答。"
                                }
                            ]
                        }
                    ]
                },
                "parameters": {
                    "result_format": "message"
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if "output" in result and "choices" in result["output"]:
                description = result["output"]["choices"][0]["message"]["content"]
                return {
                    "objects": [],  # 通义千问-VL主要提供描述
                    "scene_description": description,
                    "confidence": 0.8
                }
            else:
                logger.warning(f"通义千问-VL分析结果异常: {result}")
                return {"objects": [], "scene_description": "分析失败", "confidence": 0}
                
        except Exception as e:
            logger.error(f"通义千问-VL图片分析失败: {e}")
            return {"objects": [], "scene_description": "分析失败", "confidence": 0}
    
    async def _analyze_single_frame(self, frame_path: str, timestamp: float) -> Dict[str, Any]:
        """分析单个视频帧"""
        # 优先使用通义千问-VL，备用百度AI
        qwen_result = await self._analyze_image_with_qwen_vl(frame_path)
        baidu_result = await self._analyze_image_with_baidu(frame_path)
        
        # 合并结果
        scene_description = qwen_result.get("scene_description", "") or baidu_result.get("scene_description", "")
        objects = baidu_result.get("objects", [])
        confidence = max(qwen_result.get("confidence", 0), baidu_result.get("confidence", 0))
        
        return {
            "timestamp": timestamp,
            "scene_description": scene_description,
            "objects": objects,
            "confidence": confidence,
            "frame_path": frame_path
        }
    
    async def _extract_audio_features(self, video_path: str) -> Dict[str, Any]:
        """提取音频特征（简化版本）"""
        try:
            # 提取音频
            audio_path = await extract_audio_from_video(video_path)
            if not audio_path or not Path(audio_path).exists():
                return {"has_audio": False, "duration": 0, "description": "无音频"}
            
            # 获取音频基本信息
            import librosa
            y, sr = librosa.load(audio_path, duration=30)  # 只分析前30秒
            
            # 计算基本特征
            duration = len(y) / sr
            rms_energy = float(librosa.feature.rms(y=y).mean())
            zero_crossing_rate = float(librosa.feature.zero_crossing_rate(y).mean())
            
            # 简单判断音频类型
            if rms_energy > 0.02:
                audio_type = "音乐或强音频"
            elif zero_crossing_rate > 0.1:
                audio_type = "语音"
            else:
                audio_type = "背景音或静音"
            
            return {
                "has_audio": True,
                "duration": duration,
                "energy": rms_energy,
                "type": audio_type,
                "description": f"音频时长{duration:.1f}秒，类型：{audio_type}"
            }
            
        except Exception as e:
            logger.error(f"音频分析失败: {e}")
            return {"has_audio": False, "duration": 0, "description": "音频分析失败"}
    
    async def analyze_video(
        self, 
        video_path: str, 
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Dict[str, Any]:
        """
        云端视频分析主函数
        
        Args:
            video_path: 视频文件路径
            progress_callback: 进度回调函数
            
        Returns:
            分析结果字典
        """
        try:
            if progress_callback:
                progress_callback(0.0, "开始视频分析...")
            
            video_path = Path(video_path)
            if not video_path.exists():
                raise FileNotFoundError(f"视频文件不存在: {video_path}")
            
            # 获取视频基本信息
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                raise ValueError("无法打开视频文件")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
            
            if progress_callback:
                progress_callback(0.1, f"视频信息: {duration:.1f}秒, {width}x{height}")
            
            # 提取关键帧
            if progress_callback:
                progress_callback(0.2, "提取关键帧...")
            
            frames = await extract_frames_from_video(
                str(video_path),
                interval=settings.FRAME_SAMPLE_INTERVAL,
                max_frames=settings.MAX_FRAMES_PER_VIDEO
            )
            
            if not frames:
                raise ValueError("无法提取视频帧")
            
            if progress_callback:
                progress_callback(0.4, f"提取了{len(frames)}个关键帧")
            
            # 分析每个关键帧
            frame_analyses = []
            for i, (frame_path, timestamp) in enumerate(frames):
                if progress_callback:
                    progress = 0.4 + (i / len(frames)) * 0.4
                    progress_callback(progress, f"分析第{i+1}/{len(frames)}帧...")
                
                frame_analysis = await self._analyze_single_frame(frame_path, timestamp)
                frame_analyses.append(frame_analysis)
                
                # 避免API调用过于频繁
                await asyncio.sleep(0.5)
            
            # 分析音频
            if progress_callback:
                progress_callback(0.8, "分析音频...")
            
            audio_analysis = await self._extract_audio_features(str(video_path))
            
            # 生成总结
            if progress_callback:
                progress_callback(0.9, "生成分析总结...")
            
            # 统计场景类型
            scene_types = {}
            all_objects = []
            
            for frame in frame_analyses:
                # 统计物体
                for obj in frame.get("objects", []):
                    all_objects.append(obj["name"])
                
                # 简单场景分类
                description = frame.get("scene_description", "").lower()
                if "人" in description or "person" in description:
                    scene_types["人物"] = scene_types.get("人物", 0) + 1
                if "建筑" in description or "房" in description:
                    scene_types["建筑"] = scene_types.get("建筑", 0) + 1
                if "自然" in description or "树" in description or "山" in description:
                    scene_types["自然"] = scene_types.get("自然", 0) + 1
                if "车" in description or "交通" in description:
                    scene_types["交通"] = scene_types.get("交通", 0) + 1
            
            # 统计最常见的物体
            from collections import Counter
            object_counts = Counter(all_objects)
            top_objects = object_counts.most_common(10)
            
            # 生成关键时刻
            key_moments = []
            for frame in frame_analyses:
                if frame.get("confidence", 0) > 0.7:
                    key_moments.append({
                        "timestamp": frame["timestamp"],
                        "description": frame.get("scene_description", "")[:100],
                        "confidence": frame["confidence"]
                    })
            
            # 排序关键时刻
            key_moments.sort(key=lambda x: x["confidence"], reverse=True)
            key_moments = key_moments[:10]  # 取前10个
            
            result = {
                "video_info": {
                    "duration": duration,
                    "fps": fps,
                    "resolution": (width, height),
                    "frame_count": frame_count,
                    "file_size": video_path.stat().st_size
                },
                "frame_analysis": frame_analyses,
                "audio_analysis": audio_analysis,
                "summary": {
                    "total_frames_analyzed": len(frame_analyses),
                    "scene_types": scene_types,
                    "top_objects": [{"name": name, "count": count} for name, count in top_objects],
                    "key_moments": key_moments,
                    "has_audio": audio_analysis.get("has_audio", False),
                    "analysis_method": "云端API (百度AI + 通义千问-VL)"
                },
                "processing_info": {
                    "analysis_time": time.time(),
                    "frame_interval": settings.FRAME_SAMPLE_INTERVAL,
                    "max_frames": settings.MAX_FRAMES_PER_VIDEO,
                    "services_used": []
                }
            }
            
            # 记录使用的服务
            if settings.QWEN_VL_API_KEY:
                result["processing_info"]["services_used"].append("通义千问-VL")
            if settings.BAIDU_API_KEY:
                result["processing_info"]["services_used"].append("百度AI")
            
            if progress_callback:
                progress_callback(1.0, "视频分析完成!")
            
            logger.info(f"云端视频分析完成: {len(frame_analyses)}帧, {len(key_moments)}个关键时刻")
            return result
            
        except Exception as e:
            logger.error(f"云端视频分析失败: {e}")
            if progress_callback:
                progress_callback(1.0, f"分析失败: {str(e)}")
            raise
    
    async def get_video_summary(self, analysis_result: Dict[str, Any]) -> str:
        """根据分析结果生成视频摘要"""
        try:
            video_info = analysis_result.get("video_info", {})
            summary = analysis_result.get("summary", {})
            audio_info = analysis_result.get("audio_analysis", {})
            
            duration = video_info.get("duration", 0)
            resolution = video_info.get("resolution", (0, 0))
            
            # 生成摘要文本
            summary_text = f"""视频基本信息：
- 时长：{duration:.1f}秒
- 分辨率：{resolution[0]}x{resolution[1]}
- 音频：{'有' if audio_info.get('has_audio') else '无'}

场景分析：
"""
            
            # 添加场景类型
            scene_types = summary.get("scene_types", {})
            if scene_types:
                summary_text += "- 主要场景：" + "、".join([f"{k}({v}帧)" for k, v in scene_types.items()]) + "\n"
            
            # 添加主要物体
            top_objects = summary.get("top_objects", [])[:5]
            if top_objects:
                summary_text += "- 主要物体：" + "、".join([f"{obj['name']}({obj['count']}次)" for obj in top_objects]) + "\n"
            
            # 添加关键时刻
            key_moments = summary.get("key_moments", [])[:3]
            if key_moments:
                summary_text += "\n关键时刻：\n"
                for i, moment in enumerate(key_moments, 1):
                    timestamp = moment["timestamp"]
                    desc = moment["description"]
                    summary_text += f"{i}. {timestamp:.1f}秒: {desc}\n"
            
            return summary_text
            
        except Exception as e:
            logger.error(f"生成视频摘要失败: {e}")
            return "视频摘要生成失败"