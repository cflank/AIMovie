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
    
    async def analyze_video_guided(
        self,
        video_path: str,
        narration_segments: List[Dict[str, Any]],
        analysis_mode: str = "narration_guided",
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Dict[str, Any]:
        """基于解说词指导的视频分析"""
        try:
            if progress_callback:
                progress_callback(0.1, "开始基于解说词的视频分析...")
            
            # 根据解说词确定关键时间点
            key_timestamps = []
            for segment in narration_segments:
                start_time = segment.get("start_time", 0)
                end_time = segment.get("end_time", start_time + 5)
                mid_time = (start_time + end_time) / 2
                key_timestamps.append({
                    "timestamp": mid_time,
                    "narration": segment.get("text", ""),
                    "importance": self._calculate_importance(segment.get("text", ""))
                })
            
            if progress_callback:
                progress_callback(0.3, "提取关键帧...")
            
            # 提取关键帧
            frames_dir = settings.TEMP_DIR / f"guided_frames_{int(time.time())}"
            frames_dir.mkdir(exist_ok=True)
            
            key_frames = []
            cap = cv2.VideoCapture(video_path)
            
            for i, key_point in enumerate(key_timestamps):
                timestamp = key_point["timestamp"]
                frame_path = frames_dir / f"frame_{i:04d}.jpg"
                
                # 提取指定时间点的帧
                cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
                ret, frame = cap.read()
                if ret:
                    cv2.imwrite(str(frame_path), frame)
                    key_frames.append({
                        "timestamp": timestamp,
                        "frame_path": str(frame_path),
                        "narration": key_point["narration"],
                        "importance": key_point["importance"]
                    })
            
            cap.release()
            
            if progress_callback:
                progress_callback(0.6, "分析关键帧内容...")
            
            # 分析关键帧
            analyzed_frames = []
            for i, frame_info in enumerate(key_frames):
                if progress_callback:
                    progress = 0.6 + (i / len(key_frames)) * 0.3
                    progress_callback(progress, f"分析第{i+1}帧...")
                
                frame_analysis = await self._analyze_single_frame(
                    frame_info["frame_path"],
                    frame_info["timestamp"]
                )
                frame_analysis.update({
                    "narration": frame_info["narration"],
                    "importance": frame_info["importance"]
                })
                analyzed_frames.append(frame_analysis)
                
                # 避免API调用过于频繁
                await asyncio.sleep(0.5)
            
            if progress_callback:
                progress_callback(0.9, "生成视频重点片段...")
            
            # 生成重点片段
            highlights = self._generate_highlights(analyzed_frames, narration_segments)
            
            if progress_callback:
                progress_callback(1.0, "基于解说词的视频分析完成")
            
            return {
                "analysis_mode": analysis_mode,
                "key_frames": analyzed_frames,
                "highlights": highlights,
                "total_segments": len(narration_segments),
                "processing_time": time.time()
            }
            
        except Exception as e:
            logger.error(f"基于解说词的视频分析失败: {e}")
            raise
    
    def _calculate_importance(self, text: str) -> float:
        """计算文本重要性"""
        if not text:
            return 0.5
        
        # 扩展重要性关键词
        important_keywords = [
            "重要", "关键", "核心", "主要", "突出", "显著", "明显",
            "特别", "尤其", "值得注意", "需要", "必须", "应该",
            "开始", "结束", "转折", "高潮", "精彩", "有趣", "惊喜",
            "对话", "交流", "互动", "表情", "动作", "反应",
            "AI", "人工智能", "技术", "学习", "成长", "发现",
            "咖啡店", "书", "看", "说", "问", "答", "走进", "坐下",
            "演示", "测试", "分析", "生成", "解说", "视频", "制作",
            "神奇", "实用", "节省", "时间", "生动", "有趣", "期待"
        ]
        
        importance = 0.7  # 进一步提高基础重要性
        
        # 关键词匹配
        keyword_count = 0
        for keyword in important_keywords:
            if keyword in text:
                importance += 0.1
                keyword_count += 1
        
        # 多个关键词额外加分
        if keyword_count >= 2:
            importance += 0.1
        
        # 根据文本长度调整
        text_length = len(text)
        if text_length > 20:
            importance += 0.05
        if text_length > 40:
            importance += 0.05
        
        # 包含问号或感叹号的文本通常更重要
        if "？" in text or "！" in text or "?" in text or "!" in text:
            importance += 0.1
        
        # 包含冒号的文本（对话或解释）通常更重要
        if "：" in text or ":" in text:
            importance += 0.1
        
        # 包含引号的文本（对话）通常更重要
        if """ in text or """ in text or "\"" in text or "'" in text:
            importance += 0.1
        
        # 包含人名的文本更重要
        if "小明" in text or "小红" in text:
            importance += 0.1
        
        return min(importance, 1.0)
    
    def _generate_highlights(self, analyzed_frames: List[Dict[str, Any]], narration_segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成视频重点片段"""
        highlights = []
        
        if not analyzed_frames:
            logger.warning("没有分析帧数据，无法生成重点片段")
            return highlights
        
        # 根据重要性排序
        sorted_frames = sorted(analyzed_frames, key=lambda x: x.get("importance", 0), reverse=True)
        
        # 确保至少生成一些片段，即使重要性不高
        min_highlights = min(3, len(sorted_frames))  # 至少3个片段
        max_highlights = min(6, len(sorted_frames))  # 最多6个片段
        
        # 降低重要性阈值，确保能生成片段
        importance_threshold = 0.6  # 降低阈值
        
        # 选择重要片段
        selected_count = 0
        for i, frame in enumerate(sorted_frames):
            # 如果重要性足够高，或者还没有达到最小数量要求
            if frame.get("importance", 0) >= importance_threshold or selected_count < min_highlights:
                highlight = {
                    "start": max(0, frame["timestamp"] - 2),  # 片段开始时间
                    "end": frame["timestamp"] + 3,  # 片段结束时间
                    "importance": frame.get("importance", 0),
                    "description": frame.get("scene_description", "视频片段"),
                    "narration": frame.get("narration", ""),
                    "rank": selected_count + 1,
                    "timestamp": frame["timestamp"]
                }
                highlights.append(highlight)
                selected_count += 1
                
                if selected_count >= max_highlights:
                    break
        
        # 如果还是没有足够的片段，降低标准继续选择
        if selected_count < min_highlights:
            logger.info(f"重要性阈值{importance_threshold}只选出{selected_count}个片段，降低标准继续选择")
            for i, frame in enumerate(sorted_frames):
                if selected_count >= min_highlights:
                    break
                    
                # 检查是否已经选择过
                already_selected = any(h["timestamp"] == frame["timestamp"] for h in highlights)
                if not already_selected:
                    highlight = {
                        "start": max(0, frame["timestamp"] - 2),
                        "end": frame["timestamp"] + 3,
                        "importance": frame.get("importance", 0),
                        "description": frame.get("scene_description", "视频片段"),
                        "narration": frame.get("narration", ""),
                        "rank": selected_count + 1,
                        "timestamp": frame["timestamp"]
                    }
                    highlights.append(highlight)
                    selected_count += 1
        
        # 按时间顺序排序
        highlights.sort(key=lambda x: x["start"])
        
        # 重新分配排名
        for i, highlight in enumerate(highlights):
            highlight["rank"] = i + 1
        
        logger.info(f"生成了{len(highlights)}个重点片段，重要性范围: {min([h['importance'] for h in highlights]):.2f} - {max([h['importance'] for h in highlights]):.2f}")
        return highlights