# 媒体生成包装器 - 调用可靠的生成模块
from .robust_media_generator import (
    create_sample_files_real,
    generate_narration_audio_real,
    create_real_wav_audio,
    create_real_mp4_video,
    test_all_methods as test_robust_methods
)

# 向后兼容的函数名
def create_sample_files():
    return create_sample_files_real()

def generate_narration_audio(narration_data, voice_style="女声温柔"):
    return generate_narration_audio_real(narration_data, voice_style)

def create_combined_video_with_audio(video_path, audio_path, output_path="data/output/final_video.mp4"):
    """合并视频和音频 - 简化版本"""
    try:
        import shutil
        import os
        
        # 如果有ffmpeg，尝试合并
        if shutil.which("ffmpeg"):
            import subprocess
            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-i", audio_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"✅ 合并视频创建成功: {file_size / 1024 / 1024:.1f} MB")
                return output_path
        
        # 备用方案：返回原视频
        print("⚠️  ffmpeg不可用或合并失败，返回原视频文件")
        return video_path
        
    except Exception as e:
        print(f"视频合并失败: {e}")
        return video_path
