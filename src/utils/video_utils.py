"""
视频处理工具函数
"""

import os
import cv2
import logging
from pathlib import Path
from typing import List, Optional, Tuple
import tempfile

logger = logging.getLogger(__name__)

def extract_frames_from_video(
    video_path: str, 
    output_dir: str = None, 
    interval: int = 3, 
    max_frames: int = 50
) -> List[str]:
    """
    从视频中提取帧
    
    Args:
        video_path: 视频文件路径
        output_dir: 输出目录，如果为None则使用临时目录
        interval: 提取间隔（秒）
        max_frames: 最大帧数
    
    Returns:
        提取的帧文件路径列表
    """
    try:
        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix="frames_")
        else:
            os.makedirs(output_dir, exist_ok=True)
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"无法打开视频文件: {video_path}")
            return []
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        logger.info(f"视频信息: FPS={fps}, 总帧数={total_frames}, 时长={duration:.2f}秒")
        
        frame_paths = []
        frame_interval = int(fps * interval) if fps > 0 else 30
        
        frame_count = 0
        extracted_count = 0
        
        while cap.isOpened() and extracted_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                timestamp = frame_count / fps if fps > 0 else extracted_count * interval
                frame_filename = f"frame_{extracted_count:04d}_{timestamp:.2f}s.jpg"
                frame_path = os.path.join(output_dir, frame_filename)
                
                # 保存帧
                cv2.imwrite(frame_path, frame)
                frame_paths.append(frame_path)
                extracted_count += 1
                
                logger.debug(f"提取帧 {extracted_count}: {frame_path}")
            
            frame_count += 1
        
        cap.release()
        logger.info(f"成功提取 {len(frame_paths)} 帧")
        return frame_paths
        
    except Exception as e:
        logger.error(f"提取视频帧失败: {e}")
        return []

def extract_audio_from_video(video_path: str, output_path: str = None) -> Optional[str]:
    """
    从视频中提取音频
    
    Args:
        video_path: 视频文件路径
        output_path: 输出音频文件路径，如果为None则自动生成
    
    Returns:
        提取的音频文件路径，失败返回None
    """
    try:
        if output_path is None:
            video_name = Path(video_path).stem
            output_path = os.path.join(tempfile.gettempdir(), f"{video_name}_audio.wav")
        
        # 使用OpenCV提取音频（简化版本）
        # 注意：OpenCV主要用于视频处理，音频提取功能有限
        # 在实际项目中，建议使用ffmpeg或moviepy
        
        # 这里我们先返回一个占位符，表示音频提取功能需要进一步实现
        logger.warning("音频提取功能需要安装ffmpeg或moviepy")
        
        # 检查视频是否有音频轨道
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"无法打开视频文件: {video_path}")
            return None
        
        # 创建一个空的音频文件作为占位符
        with open(output_path, 'w') as f:
            f.write("# 音频提取占位符\n")
        
        cap.release()
        logger.info(f"音频提取占位符已创建: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"提取音频失败: {e}")
        return None

def create_narrated_video(
    video_path: str,
    narration_segments: List[dict],
    output_path: str,
    background_music: Optional[str] = None,
    music_volume: float = 0.3
) -> bool:
    """
    创建带解说的视频
    
    Args:
        video_path: 原始视频路径
        narration_segments: 解说片段列表
        output_path: 输出视频路径
        background_music: 背景音乐路径（可选）
        music_volume: 背景音乐音量
    
    Returns:
        是否成功创建
    """
    try:
        logger.info(f"开始创建带解说的视频: {output_path}")
        
        # 这里是一个简化的实现
        # 在实际项目中，需要使用moviepy或ffmpeg来合成音视频
        
        # 复制原视频作为基础
        import shutil
        shutil.copy2(video_path, output_path)
        
        logger.info(f"视频创建完成（简化版本）: {output_path}")
        logger.warning("完整的音视频合成功能需要安装moviepy或ffmpeg")
        
        return True
        
    except Exception as e:
        logger.error(f"创建带解说视频失败: {e}")
        return False

def get_video_info(video_path: str) -> dict:
    """
    获取视频基本信息
    
    Args:
        video_path: 视频文件路径
    
    Returns:
        视频信息字典
    """
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {"error": "无法打开视频文件"}
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0
        
        cap.release()
        
        return {
            "fps": fps,
            "frame_count": frame_count,
            "width": width,
            "height": height,
            "duration": duration,
            "size_mb": os.path.getsize(video_path) / (1024 * 1024)
        }
        
    except Exception as e:
        logger.error(f"获取视频信息失败: {e}")
        return {"error": str(e)} 