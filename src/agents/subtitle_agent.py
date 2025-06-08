import os
import re
import time
import logging
from typing import List, Dict, Any, Optional, Callable
import chardet

logger = logging.getLogger(__name__)

class SubtitleAgent:
    """字幕处理代理"""
    
    def __init__(self):
        self.supported_formats = ['.srt', '.vtt', '.ass', '.ssa', '.txt']
    
    def parse_subtitle_file(
        self, 
        subtitle_path: str,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Dict[str, Any]:
        """
        解析字幕文件
        
        Args:
            subtitle_path: 字幕文件路径
            progress_callback: 进度回调函数
            
        Returns:
            包含字幕信息的字典
        """
        try:
            if progress_callback:
                progress_callback(0.0, "开始解析字幕文件...")
            
            # 检查文件是否存在
            if not os.path.exists(subtitle_path):
                raise FileNotFoundError(f"字幕文件不存在: {subtitle_path}")
            
            # 检查文件格式
            file_ext = os.path.splitext(subtitle_path)[1].lower()
            if file_ext not in self.supported_formats:
                raise ValueError(f"不支持的字幕格式: {file_ext}")
            
            if progress_callback:
                progress_callback(0.2, "读取字幕文件...")
            
            # 读取文件内容
            content = self._read_file_with_encoding(subtitle_path)
            
            if progress_callback:
                progress_callback(0.5, "解析字幕内容...")
            
            # 根据格式解析
            if file_ext == '.srt':
                segments = self._parse_srt(content)
            elif file_ext == '.vtt':
                segments = self._parse_vtt(content)
            elif file_ext in ['.ass', '.ssa']:
                segments = self._parse_ass(content)
            elif file_ext == '.txt':
                segments = self._parse_txt(content)
            else:
                raise ValueError(f"暂不支持解析 {file_ext} 格式")
            
            if progress_callback:
                progress_callback(0.8, "分析字幕内容...")
            
            # 分析字幕内容
            analysis = self._analyze_subtitle_content(segments)
            
            result = {
                "subtitle_segments": segments,
                "analysis": analysis,
                "metadata": {
                    "file_path": subtitle_path,
                    "file_format": file_ext,
                    "total_segments": len(segments),
                    "total_duration": max([seg["end_time"] for seg in segments]) if segments else 0,
                    "total_characters": sum([len(seg["text"]) for seg in segments]),
                    "parse_time": time.time()
                }
            }
            
            if progress_callback:
                progress_callback(1.0, f"字幕解析完成！共{len(segments)}段")
            
            logger.info(f"字幕解析完成: {len(segments)}段, 总字数: {result['metadata']['total_characters']}")
            return result
            
        except Exception as e:
            logger.error(f"字幕解析失败: {e}")
            if progress_callback:
                progress_callback(1.0, f"解析失败: {str(e)}")
            raise
    
    def _read_file_with_encoding(self, file_path: str) -> str:
        """自动检测编码并读取文件"""
        try:
            # 检测文件编码
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                encoding_result = chardet.detect(raw_data)
                encoding = encoding_result['encoding'] or 'utf-8'
            
            # 使用检测到的编码读取文件
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                return f.read()
                
        except Exception as e:
            logger.warning(f"编码检测失败，使用UTF-8: {e}")
            # 备用方案：使用UTF-8
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
    
    def _parse_srt(self, content: str) -> List[Dict[str, Any]]:
        """解析SRT格式字幕"""
        segments = []
        
        # 标准化换行符
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # 分割成字幕块
        blocks = re.split(r'\n\s*\n', content.strip())
        
        for block in blocks:
            if not block.strip():
                continue
                
            lines = block.strip().split('\n')
            if len(lines) < 3:
                continue
            
            try:
                # 第一行：序号
                index = int(lines[0].strip())
                
                # 第二行：时间戳
                time_line = lines[1].strip()
                time_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})', time_line)
                if not time_match:
                    continue
                
                start_time = self._time_to_seconds(time_match.group(1))
                end_time = self._time_to_seconds(time_match.group(2))
                
                # 第三行及以后：字幕文本
                text = '\n'.join(lines[2:]).strip()
                
                if text:  # 忽略空字幕
                    segments.append({
                        "index": index,
                        "start_time": start_time,
                        "end_time": end_time,
                        "text": text,
                        "duration": end_time - start_time
                    })
                    
            except (ValueError, IndexError) as e:
                logger.warning(f"跳过无效的字幕块: {e}")
                continue

        
        return segments
    
    def _parse_vtt(self, content: str) -> List[Dict[str, Any]]:
        """解析VTT格式字幕"""
        segments = []
        
        # 移除WEBVTT头部
        content = re.sub(r'^WEBVTT.*?\n\n', '', content, flags=re.MULTILINE)
        
        # VTT格式正则表达式
        pattern = r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})\s*\n(.*?)(?=\n\d{2}:\d{2}:\d{2}|\n*$)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for i, match in enumerate(matches, 1):
            start_time = self._time_to_seconds(match[0].replace('.', ','))
            end_time = self._time_to_seconds(match[1].replace('.', ','))
            text = match[2].strip().replace('\n', ' ')
            
            if text:
                segments.append({
                    "index": i,
                    "start_time": start_time,
                    "end_time": end_time,
                    "text": text,
                    "duration": end_time - start_time
                })
        
        return segments
    
    def _parse_ass(self, content: str) -> List[Dict[str, Any]]:
        """解析ASS/SSA格式字幕"""
        segments = []
        
        # 查找对话部分
        dialogue_section = False
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('[Events]'):
                dialogue_section = True
                continue
            elif line.startswith('[') and dialogue_section:
                break
            
            if dialogue_section and line.startswith('Dialogue:'):
                parts = line.split(',', 9)
                if len(parts) >= 10:
                    start_time = self._time_to_seconds(parts[1])
                    end_time = self._time_to_seconds(parts[2])
                    text = parts[9].strip()
                    
                    # 移除ASS格式标签
                    text = re.sub(r'\{[^}]*\}', '', text)
                    
                    if text:
                        segments.append({
                            "index": len(segments) + 1,
                            "start_time": start_time,
                            "end_time": end_time,
                            "text": text,
                            "duration": end_time - start_time
                        })
        
        return segments
    
    def _parse_txt(self, content: str) -> List[Dict[str, Any]]:
        """解析纯文本格式（简单分段）"""
        segments = []
        
        # 按行分割
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        # 简单时间分配（每行5秒）
        segment_duration = 5.0
        current_time = 0.0
        
        for i, line in enumerate(lines, 1):
            start_time = current_time
            end_time = current_time + segment_duration
            
            segments.append({
                "index": i,
                "start_time": start_time,
                "end_time": end_time,
                "text": line,
                "duration": segment_duration
            })
            
            current_time = end_time
        
        return segments
    
    def _time_to_seconds(self, time_str: str) -> float:
        """将时间字符串转换为秒数"""
        try:
            # 处理不同的时间格式
            time_str = time_str.strip()
            
            # SRT格式: 00:01:23,456
            if ',' in time_str:
                time_part, ms_part = time_str.split(',')
                ms = int(ms_part) / 1000.0
            # VTT格式: 00:01:23.456
            elif '.' in time_str and len(time_str.split('.')[-1]) == 3:
                time_part, ms_part = time_str.split('.')
                ms = int(ms_part) / 1000.0
            # ASS格式: 0:01:23.45
            elif '.' in time_str:
                time_part, ms_part = time_str.split('.')
                ms = int(ms_part.ljust(3, '0')[:3]) / 1000.0
            else:
                time_part = time_str
                ms = 0.0
            
            # 解析时:分:秒
            time_parts = time_part.split(':')
            if len(time_parts) == 3:
                hours, minutes, seconds = map(int, time_parts)
            elif len(time_parts) == 2:
                hours = 0
                minutes, seconds = map(int, time_parts)
            else:
                return 0.0
            
            total_seconds = hours * 3600 + minutes * 60 + seconds + ms
            return total_seconds
            
        except Exception as e:
            logger.warning(f"时间格式解析失败: {time_str}, 错误: {e}")
            return 0.0
    
    def _analyze_subtitle_content(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析字幕内容"""
        try:
            if not segments:
                return {
                    "characters": [],
                    "themes": [],
                    "emotions": [],
                    "key_phrases": [],
                    "dialogue_density": 0,
                    "average_segment_length": 0
                }
            
            # 提取所有文本
            all_text = " ".join([seg["text"] for seg in segments])
            
            # 角色识别（简化版）
            characters = self._extract_characters(segments)
            
            # 主题分析
            themes = self._extract_themes(all_text)
            
            # 情感分析
            emotions = self._analyze_emotions(all_text)
            
            # 关键短语提取
            key_phrases = self._extract_key_phrases(all_text)
            
            # 计算对话密度
            total_duration = max([seg["end_time"] for seg in segments])
            dialogue_density = len(segments) / total_duration if total_duration > 0 else 0
            
            # 平均段落长度
            average_length = sum([len(seg["text"]) for seg in segments]) / len(segments)
            
            return {
                "characters": characters,
                "themes": themes,
                "emotions": emotions,
                "key_phrases": key_phrases,
                "dialogue_density": dialogue_density,
                "average_segment_length": average_length,
                "total_characters": len(all_text),
                "segment_count": len(segments)
            }
            
        except Exception as e:
            logger.error(f"字幕内容分析失败: {e}")
            return {}
    
    def _extract_characters(self, segments: List[Dict[str, Any]]) -> List[str]:
        """提取角色名称"""
        characters = set()
        
        for segment in segments:
            text = segment["text"]
            
            # 查找对话格式：角色名: 对话内容 或 角色名：对话内容
            if ':' in text or '：' in text:
                # 处理中英文冒号
                separator = ':' if ':' in text else '：'
                potential_character = text.split(separator)[0].strip()
                
                # 验证是否为角色名
                # 1. 长度合理（1-10个字符）
                # 2. 只包含中文、英文、数字、空格
                # 3. 不是纯数字
                # 4. 不包含常见的非角色词汇
                if (1 <= len(potential_character) <= 10 and 
                    re.match(r'^[a-zA-Z\u4e00-\u9fff0-9\s]+$', potential_character) and
                    not potential_character.isdigit() and
                    not any(word in potential_character for word in ['时间', '地点', '场景', '背景', '音乐', '效果'])):
                    characters.add(potential_character)
            
            # 查找括号中的角色标识
            bracket_matches = re.findall(r'[\(（]([^)）]+)[\)）]', text)
            for match in bracket_matches:
                match = match.strip()
                if (1 <= len(match) <= 8 and 
                    not any(char.isdigit() for char in match) and
                    not any(word in match for word in ['旁白', '画外音', '背景', '音乐', '效果'])):
                    characters.add(match)
            
            # 查找常见的角色提及模式
            # 例如："小明走进咖啡店" - 提取"小明"
            name_patterns = [
                r'^([a-zA-Z\u4e00-\u9fff]{2,4})(?:走|来|去|说|问|答|看|听|想|做|拿|给)',
                r'([a-zA-Z\u4e00-\u9fff]{2,4})(?:对|向|跟|和)([a-zA-Z\u4e00-\u9fff]{2,4})(?:说|问|答)',
                r'([a-zA-Z\u4e00-\u9fff]{2,4})(?:告诉|询问|回答)([a-zA-Z\u4e00-\u9fff]{2,4})'
            ]
            
            for pattern in name_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    if isinstance(match, tuple):
                        for name in match:
                            if name and len(name) >= 2:
                                characters.add(name)
                    else:
                        if match and len(match) >= 2:
                            characters.add(match)
        
        # 过滤掉可能的误识别
        filtered_characters = []
        for char in characters:
            # 排除常见的非角色词汇
            if not any(word in char for word in ['咖啡店', '书店', '学校', '公司', '家里', '房间', '客厅']):
                filtered_characters.append(char)
        
        return filtered_characters
    
    def _extract_themes(self, text: str) -> List[str]:
        """提取主题"""
        themes = []
        
        theme_keywords = {
            "爱情": ["爱情", "恋爱", "喜欢", "爱", "情侣", "约会", "表白", "心动"],
            "友情": ["朋友", "友谊", "友情", "伙伴", "同伴", "兄弟", "姐妹", "闺蜜"],
            "家庭": ["家庭", "父母", "孩子", "家人", "亲情", "家", "爸爸", "妈妈"],
            "工作": ["工作", "职业", "事业", "公司", "老板", "同事", "项目", "会议"],
            "学习": ["学习", "学校", "老师", "学生", "考试", "知识", "课程", "作业"],
            "冒险": ["冒险", "探险", "旅行", "发现", "挑战", "勇气", "未知", "探索"],
            "悬疑": ["秘密", "谜团", "调查", "真相", "线索", "推理", "神秘", "隐藏"],
            "成长": ["成长", "改变", "学会", "明白", "成熟", "经历", "感悟", "蜕变"]
        }
        
        for theme, keywords in theme_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    themes.append(theme)
                    break
        
        return themes
    
    def _analyze_emotions(self, text: str) -> List[str]:
        """分析情感"""
        emotions = []
        
        emotion_keywords = {
            "开心": ["开心", "高兴", "快乐", "兴奋", "愉快", "欢乐", "笑", "哈哈"],
            "悲伤": ["悲伤", "难过", "伤心", "痛苦", "哭", "眼泪", "失落", "沮丧"],
            "愤怒": ["愤怒", "生气", "恼火", "暴怒", "气愤", "讨厌", "烦躁", "愤慨"],
            "惊讶": ["惊讶", "震惊", "吃惊", "意外", "惊奇", "不敢相信", "天哪", "哇"],
            "恐惧": ["害怕", "恐惧", "担心", "紧张", "焦虑", "恐慌", "可怕", "吓人"],
            "感动": ["感动", "温暖", "感激", "谢谢", "温馨", "暖心", "触动", "感谢"]
        }
        
        for emotion, keywords in emotion_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    emotions.append(emotion)
                    break
        
        return list(set(emotions))
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """提取关键短语"""
        try:
            # 移除标点符号
            import re
            clean_text = re.sub(r'[^\w\s]', '', text)
            
            # 分词
            words = clean_text.split()
            
            # 统计词频
            word_count = {}
            for word in words:
                if len(word) > 1:  # 忽略单字符
                    word_count[word] = word_count.get(word, 0) + 1
            
            # 返回频率最高的词
            sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
            return [word for word, count in sorted_words[:15] if count > 1]
            
        except Exception as e:
            logger.error(f"关键短语提取失败: {e}")
            return [] 