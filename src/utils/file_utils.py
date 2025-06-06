"""
文件处理工具函数
"""

import os
import shutil
import logging
import tempfile
from pathlib import Path
from typing import Optional, List
import aiofiles
from fastapi import UploadFile

logger = logging.getLogger(__name__)

async def save_uploaded_file(file: UploadFile, upload_dir: str) -> str:
    """
    保存上传的文件
    
    Args:
        file: FastAPI上传文件对象
        upload_dir: 上传目录
    
    Returns:
        保存的文件路径
    """
    try:
        # 确保上传目录存在
        os.makedirs(upload_dir, exist_ok=True)
        
        # 生成安全的文件名
        safe_filename = secure_filename(file.filename)
        file_path = os.path.join(upload_dir, safe_filename)
        
        # 如果文件已存在，添加时间戳
        if os.path.exists(file_path):
            import time
            name, ext = os.path.splitext(safe_filename)
            timestamp = int(time.time())
            safe_filename = f"{name}_{timestamp}{ext}"
            file_path = os.path.join(upload_dir, safe_filename)
        
        # 异步保存文件
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        logger.info(f"文件保存成功: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"保存文件失败: {e}")
        raise

def secure_filename(filename: str) -> str:
    """
    生成安全的文件名
    
    Args:
        filename: 原始文件名
    
    Returns:
        安全的文件名
    """
    if not filename:
        return "unnamed_file"
    
    # 移除路径分隔符
    filename = os.path.basename(filename)
    
    # 替换危险字符
    dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')
    
    # 限制文件名长度
    name, ext = os.path.splitext(filename)
    if len(name) > 100:
        name = name[:100]
    
    return name + ext

def cleanup_temp_files(temp_dir: str = None, max_age_hours: int = 24) -> int:
    """
    清理临时文件
    
    Args:
        temp_dir: 临时文件目录，如果为None则使用系统临时目录
        max_age_hours: 文件最大保留时间（小时）
    
    Returns:
        清理的文件数量
    """
    try:
        if temp_dir is None:
            temp_dir = tempfile.gettempdir()
        
        if not os.path.exists(temp_dir):
            return 0
        
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        cleaned_count = 0
        
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    # 检查文件年龄
                    file_age = current_time - os.path.getmtime(file_path)
                    if file_age > max_age_seconds:
                        os.remove(file_path)
                        cleaned_count += 1
                        logger.debug(f"删除过期临时文件: {file_path}")
                except Exception as e:
                    logger.warning(f"删除文件失败 {file_path}: {e}")
        
        logger.info(f"清理了 {cleaned_count} 个临时文件")
        return cleaned_count
        
    except Exception as e:
        logger.error(f"清理临时文件失败: {e}")
        return 0

def get_file_size(file_path: str) -> int:
    """
    获取文件大小
    
    Args:
        file_path: 文件路径
    
    Returns:
        文件大小（字节）
    """
    try:
        return os.path.getsize(file_path)
    except Exception as e:
        logger.error(f"获取文件大小失败 {file_path}: {e}")
        return 0

def get_file_extension(filename: str) -> str:
    """
    获取文件扩展名
    
    Args:
        filename: 文件名
    
    Returns:
        文件扩展名（小写，包含点）
    """
    return os.path.splitext(filename)[1].lower()

def is_supported_video_format(filename: str) -> bool:
    """
    检查是否为支持的视频格式
    
    Args:
        filename: 文件名
    
    Returns:
        是否为支持的视频格式
    """
    supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
    return get_file_extension(filename) in supported_formats

def is_supported_audio_format(filename: str) -> bool:
    """
    检查是否为支持的音频格式
    
    Args:
        filename: 文件名
    
    Returns:
        是否为支持的音频格式
    """
    supported_formats = ['.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a']
    return get_file_extension(filename) in supported_formats

def create_directory(dir_path: str) -> bool:
    """
    创建目录
    
    Args:
        dir_path: 目录路径
    
    Returns:
        是否创建成功
    """
    try:
        os.makedirs(dir_path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"创建目录失败 {dir_path}: {e}")
        return False

def copy_file(src_path: str, dst_path: str) -> bool:
    """
    复制文件
    
    Args:
        src_path: 源文件路径
        dst_path: 目标文件路径
    
    Returns:
        是否复制成功
    """
    try:
        # 确保目标目录存在
        dst_dir = os.path.dirname(dst_path)
        create_directory(dst_dir)
        
        shutil.copy2(src_path, dst_path)
        logger.info(f"文件复制成功: {src_path} -> {dst_path}")
        return True
    except Exception as e:
        logger.error(f"文件复制失败: {e}")
        return False

def move_file(src_path: str, dst_path: str) -> bool:
    """
    移动文件
    
    Args:
        src_path: 源文件路径
        dst_path: 目标文件路径
    
    Returns:
        是否移动成功
    """
    try:
        # 确保目标目录存在
        dst_dir = os.path.dirname(dst_path)
        create_directory(dst_dir)
        
        shutil.move(src_path, dst_path)
        logger.info(f"文件移动成功: {src_path} -> {dst_path}")
        return True
    except Exception as e:
        logger.error(f"文件移动失败: {e}")
        return False

def delete_file(file_path: str) -> bool:
    """
    删除文件
    
    Args:
        file_path: 文件路径
    
    Returns:
        是否删除成功
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"文件删除成功: {file_path}")
        return True
    except Exception as e:
        logger.error(f"文件删除失败: {e}")
        return False

def get_directory_size(dir_path: str) -> int:
    """
    获取目录大小
    
    Args:
        dir_path: 目录路径
    
    Returns:
        目录大小（字节）
    """
    try:
        total_size = 0
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    total_size += os.path.getsize(file_path)
                except Exception:
                    pass
        return total_size
    except Exception as e:
        logger.error(f"获取目录大小失败 {dir_path}: {e}")
        return 0

def list_files_in_directory(dir_path: str, extension: str = None) -> List[str]:
    """
    列出目录中的文件
    
    Args:
        dir_path: 目录路径
        extension: 文件扩展名过滤（可选）
    
    Returns:
        文件路径列表
    """
    try:
        if not os.path.exists(dir_path):
            return []
        
        files = []
        for file in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file)
            if os.path.isfile(file_path):
                if extension is None or file.lower().endswith(extension.lower()):
                    files.append(file_path)
        
        return sorted(files)
    except Exception as e:
        logger.error(f"列出目录文件失败 {dir_path}: {e}")
        return [] 