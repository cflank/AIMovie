# 可靠的音视频文件生成模块 - 支持多种备用方案
import os
import time
import wave
import struct
import math
import numpy as np
import asyncio
import subprocess
import shutil
from pathlib import Path

class MediaGenerator:
    """音视频生成器，包含多种备用方案"""
    
    def __init__(self):
        self.output_dir = Path("data/output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def create_wav_audio(self, duration_seconds=10, sample_rate=44100, text_content="", filename="audio.wav"):
        """创建高质量WAV音频文件"""
        audio_path = self.output_dir / filename
        
        try:
            frames = []
            total_samples = int(duration_seconds * sample_rate)
            
            for i in range(total_samples):
                t = i / sample_rate
                
                # 创建更复杂的音频波形，模拟语音
                value = 0
                value += 0.4 * math.sin(2 * math.pi * 150 * t)  # 基础频率
                value += 0.2 * math.sin(2 * math.pi * 300 * t)  # 谐波
                value += 0.15 * math.sin(2 * math.pi * 600 * t)
                value += 0.1 * math.sin(2 * math.pi * 1200 * t)
                
                # 添加调制
                envelope = 0.3 + 0.7 * abs(math.sin(2 * math.pi * 3 * t))
                value *= envelope
                
                # 转换为16位
                value = max(-1, min(1, value))
                sample = int(32767 * value * 0.8)
                frames.append(struct.pack('<h', sample))
            
            # 写入WAV文件
            with wave.open(str(audio_path), 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(b''.join(frames))
            
            if audio_path.exists():
                file_size = audio_path.stat().st_size
                print(f"✅ WAV音频创建成功: {file_size / 1024:.1f} KB")
                return str(audio_path)
        
        except Exception as e:
            print(f"WAV音频创建失败: {e}")
        
        return None

    def create_video_robust(self, duration_seconds=10, fps=24, width=640, height=480):
        """创建视频的稳健方法，尝试多种方案"""
        print("🎬 尝试创建视频文件...")
        
        # 方案1: OpenCV + mp4v
        try:
            import cv2
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_path = self.output_dir / "video_mp4v.mp4"
            out = cv2.VideoWriter(str(video_path), fourcc, fps, (width, height))
            
            if out.isOpened():
                total_frames = duration_seconds * fps
                for frame_num in range(total_frames):
                    frame = self._create_frame(frame_num, total_frames, width, height)
                    out.write(frame)
                out.release()
                
                if video_path.exists() and video_path.stat().st_size > 1000:
                    print(f"✅ mp4v视频创建成功: {video_path.stat().st_size / 1024 / 1024:.1f} MB")
                    return str(video_path)
        except Exception as e:
            print(f"mp4v方法失败: {e}")
        
        # 方案2: OpenCV + XVID (AVI)
        try:
            import cv2
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            video_path = self.output_dir / "video_xvid.avi"
            out = cv2.VideoWriter(str(video_path), fourcc, fps, (width, height))
            
            if out.isOpened():
                total_frames = duration_seconds * fps
                for frame_num in range(total_frames):
                    frame = self._create_frame(frame_num, total_frames, width, height)
                    out.write(frame)
                out.release()
                
                if video_path.exists() and video_path.stat().st_size > 1000:
                    print(f"✅ XVID视频创建成功: {video_path.stat().st_size / 1024 / 1024:.1f} MB")
                    return str(video_path)
        except Exception as e:
            print(f"XVID方法失败: {e}")
        
        print("❌ 所有视频创建方法都失败了")
        return None
    
    def _create_frame(self, frame_num, total_frames, width, height):
        """创建单帧"""
        import cv2
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        time_factor = frame_num / total_frames
        
        # 简单渐变背景
        for y in range(height):
            color_value = int(255 * (y / height))
            frame[y, :] = [color_value, 255 - color_value, 128]
        
        # 添加文字
        font = cv2.FONT_HERSHEY_SIMPLEX
        text = f"AIMovie Frame {frame_num}/{total_frames}"
        cv2.putText(frame, text, (50, 50), font, 1, (255, 255, 255), 2)
        
        # 添加移动圆圈
        center_x = int(width/2 + 100 * math.sin(time_factor * 6 * math.pi))
        center_y = int(height/2)
        cv2.circle(frame, (center_x, center_y), 30, (0, 255, 255), -1)
        
        return frame

    async def create_tts_audio(self, text, voice="zh-CN-XiaoxiaoNeural", filename="tts_audio.wav"):
        """使用Edge-TTS创建语音"""
        audio_path = self.output_dir / filename
        
        try:
            import edge_tts
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(str(audio_path))
            
            if audio_path.exists():
                file_size = audio_path.stat().st_size
                print(f"✅ TTS音频创建成功: {file_size / 1024:.1f} KB")
                return str(audio_path)
        except Exception as e:
            print(f"TTS创建失败: {e}")
        return None

    def create_audio_robust(self, duration_seconds=10):
        """创建音频的稳健方法"""
        print("🎵 创建音频文件...")
        audio_path = self.create_wav_audio(duration_seconds)
        if audio_path:
            return audio_path
        print("❌ 音频创建失败")
        return None

    def generate_narration_audio(self, narration_data, voice_style="女声温柔"):
        """生成解说音频"""
        voice_map = {
            "女声温柔": "zh-CN-XiaoxiaoNeural",
            "女声活泼": "zh-CN-XiaohanNeural", 
            "男声沉稳": "zh-CN-YunxiNeural",
            "男声年轻": "zh-CN-YunyangNeural"
        }
        
        try:
            narration_list = narration_data.get('narration', [])
            if not narration_list:
                return self.create_audio_robust(5)
            
            # 组合文本
            full_text = ""
            for i, item in enumerate(narration_list):
                text = item.get('text', '')
                if i > 0:
                    full_text += "。 "
                full_text += text
            
            voice = voice_map.get(voice_style, "zh-CN-XiaoxiaoNeural")
            
            # 尝试TTS
            try:
                tts_audio = asyncio.run(self.create_tts_audio(full_text, voice))
                if tts_audio:
                    return tts_audio
            except Exception as e:
                print(f"TTS失败，使用备用方案: {e}")
            
            # 备用方案：合成音频
            duration = max(5, len(narration_list) * 3)
            return self.create_audio_robust(duration)
        
        except Exception as e:
            print(f"解说音频生成失败: {e}")
            return self.create_audio_robust(10)

# 全局实例
_generator = MediaGenerator()

def create_sample_files_real():
    """创建示例文件的主函数"""
    print("🚀 开始生成音视频文件...")
    
    # 生成音频
    audio_path = _generator.create_audio_robust(10)
    
    # 生成视频
    video_path = _generator.create_video_robust(8, 24, 854, 480)
    
    return video_path, audio_path

def generate_narration_audio_real(narration_data, voice_style="女声温柔"):
    """生成解说音频的包装函数"""
    return _generator.generate_narration_audio(narration_data, voice_style)

def create_real_wav_audio(duration_seconds=10, sample_rate=44100, text_content=""):
    """向后兼容的WAV音频创建函数"""
    return _generator.create_wav_audio(duration_seconds, sample_rate, text_content)

def create_real_mp4_video(duration_seconds=10, fps=24, width=640, height=480):
    """向后兼容的视频创建函数"""
    return _generator.create_video_robust(duration_seconds, fps, width, height)

def test_all_methods():
    """测试所有生成方法"""
    print("🧪 测试所有音视频生成方法...")
    
    # 测试音频
    print("\n1. 测试音频生成...")
    audio = _generator.create_wav_audio(3, filename="test_audio.wav")
    
    # 测试视频
    print("\n2. 测试视频生成...")
    video = _generator.create_video_robust(3, 24, 640, 480)
    
    # 测试TTS
    print("\n3. 测试TTS...")
    try:
        tts_audio = asyncio.run(_generator.create_tts_audio("这是测试语音", filename="test_tts.wav"))
    except:
        tts_audio = None
    
    # 汇总结果
    print("\n📊 测试结果:")
    print(f"   音频WAV: {'✅' if audio else '❌'}")
    print(f"   视频文件: {'✅' if video else '❌'}")
    print(f"   TTS音频: {'✅' if tts_audio else '❌'}")
    
    return audio is not None, video is not None, tts_audio is not None

if __name__ == "__main__":
    test_all_methods()
