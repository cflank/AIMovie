import cv2
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip
from typing import Dict, List, Any, Tuple
import logging
from pathlib import Path

class VideoEditingAgent:
    """视频剪辑Agent"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.output_dir = Path("data/output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_short_video(self, 
                          original_video_path: str,
                          narration_audio_path: str,
                          analysis_result: Dict[str, Any],
                          narration_data: Dict[str, Any],
                          target_duration: int = 60) -> str:
        """创建短视频"""
        try:
            # 加载原视频
            video_clip = VideoFileClip(original_video_path)
            
            # 选择关键片段
            key_segments = self._select_key_segments(
                analysis_result, narration_data, target_duration
            )
            
            # 剪辑视频片段
            edited_clips = self._edit_video_segments(video_clip, key_segments)
            
            # 合并片段
            final_video = self._combine_segments(edited_clips)
            
            # 添加解说音频
            if narration_audio_path and Path(narration_audio_path).exists():
                narration_audio = AudioFileClip(narration_audio_path)
                final_video = final_video.set_audio(narration_audio)
            
            # 添加字幕
            final_video = self._add_subtitles(final_video, narration_data)
            
            # 输出文件
            output_path = self.output_dir / "edited_short_video.mp4"
            final_video.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            # 清理资源
            video_clip.close()
            final_video.close()
            if 'narration_audio' in locals():
                narration_audio.close()
            
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"视频剪辑失败: {e}")
            raise
    
    def _select_key_segments(self, analysis: Dict, narration: Dict, target_duration: int) -> List[Dict]:
        """选择关键视频片段"""
        key_moments = analysis.get('key_moments', [])
        scenes = analysis.get('scenes', [])
        narration_segments = narration.get('narration', [])
        
        segments = []
        total_duration = 0
        
        # 基于关键时刻选择片段
        for moment in sorted(key_moments, key=lambda x: x['importance'], reverse=True):
            if total_duration >= target_duration:
                break
                
            start_time = max(0, moment['timestamp'] - 2)
            end_time = min(analysis.get('duration', 0), moment['timestamp'] + 3)
            duration = end_time - start_time
            
            if total_duration + duration <= target_duration:
                segments.append({
                    'start': start_time,
                    'end': end_time,
                    'importance': moment['importance'],
                    'type': 'key_moment'
                })
                total_duration += duration
        
        # 如果时长不够，添加其他有趣片段
        if total_duration < target_duration * 0.8:
            for scene in scenes:
                if total_duration >= target_duration:
                    break
                    
                # 选择有多个对象的场景
                if len(scene.get('objects', [])) >= 2:
                    start_time = scene['timestamp']
                    end_time = min(analysis.get('duration', 0), start_time + 4)
                    duration = end_time - start_time
                    
                    # 避免重叠
                    overlap = any(
                        seg['start'] <= start_time <= seg['end'] or 
                        seg['start'] <= end_time <= seg['end']
                        for seg in segments
                    )
                    
                    if not overlap and total_duration + duration <= target_duration:
                        segments.append({
                            'start': start_time,
                            'end': end_time,
                            'importance': 0.5,
                            'type': 'scene'
                        })
                        total_duration += duration
        
        return sorted(segments, key=lambda x: x['start'])
    
    def _edit_video_segments(self, video_clip: VideoFileClip, segments: List[Dict]) -> List[VideoFileClip]:
        """剪辑视频片段"""
        clips = []
        
        for segment in segments:
            try:
                # 提取片段
                clip = video_clip.subclip(segment['start'], segment['end'])
                
                # 根据重要性调整效果
                if segment['importance'] > 0.8:
                    # 高重要性片段：轻微放大
                    clip = clip.resize(1.1).set_position('center')
                elif segment['type'] == 'key_moment':
                    # 关键时刻：添加淡入淡出
                    clip = clip.fadein(0.5).fadeout(0.5)
                
                clips.append(clip)
                
            except Exception as e:
                self.logger.warning(f"片段剪辑失败: {segment}, 错误: {e}")
                continue
        
        return clips
    
    def _combine_segments(self, clips: List[VideoFileClip]) -> VideoFileClip:
        """合并视频片段"""
        if not clips:
            raise ValueError("没有可用的视频片段")
        
        # 添加转场效果
        final_clips = []
        for i, clip in enumerate(clips):
            if i > 0:
                # 添加简单的淡入效果
                clip = clip.fadein(0.3)
            if i < len(clips) - 1:
                # 添加淡出效果
                clip = clip.fadeout(0.3)
            
            final_clips.append(clip)
        
        # 连接所有片段
        from moviepy.editor import concatenate_videoclips
        return concatenate_videoclips(final_clips, method="compose")
    
    def _add_subtitles(self, video_clip: VideoFileClip, narration_data: Dict) -> VideoFileClip:
        """添加字幕"""
        try:
            narration_segments = narration_data.get('narration', [])
            if not narration_segments:
                return video_clip
            
            subtitle_clips = []
            
            for segment in narration_segments:
                try:
                    # 解析时间戳
                    timestamp = segment.get('timestamp', '00:00')
                    text = segment.get('text', '')
                    
                    if not text:
                        continue
                    
                    # 转换时间戳为秒
                    time_parts = timestamp.split(':')
                    start_time = int(time_parts[0]) * 60 + int(time_parts[1])
                    
                    # 估算显示时长（基于文字长度）
                    duration = max(3, len(text) * 0.1)
                    
                    # 创建字幕
                    txt_clip = TextClip(
                        text,
                        fontsize=24,
                        color='white',
                        stroke_color='black',
                        stroke_width=2,
                        font='Arial-Bold'
                    ).set_position(('center', 'bottom')).set_start(start_time).set_duration(duration)
                    
                    subtitle_clips.append(txt_clip)
                    
                except Exception as e:
                    self.logger.warning(f"字幕创建失败: {segment}, 错误: {e}")
                    continue
            
            if subtitle_clips:
                return CompositeVideoClip([video_clip] + subtitle_clips)
            else:
                return video_clip
                
        except Exception as e:
            self.logger.error(f"添加字幕失败: {e}")
            return video_clip