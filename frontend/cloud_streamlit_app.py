"""
AIMovie Cloud Streamlit 前端应用
集成多种大模型组合和预设配置选择
"""

import streamlit as st
import requests
import os
import sys
import json
import time
from typing import Dict, Any, Optional, List
import logging

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config_selector import (
    render_preset_selector, 
    render_service_status, 
    render_detailed_service_info,
    render_cost_calculator,
    render_configuration_guide,
    render_preset_comparison
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 配置页面
st.set_page_config(
    page_title="AIMovie Cloud - 智能视频解说生成器",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API基础URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .cost-info {
        background: #e8f5e8;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #28a745;
    }
    .warning-info {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #ffc107;
    }
    .error-info {
        background: #f8d7da;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)


def check_api_health() -> bool:
    """检查API服务健康状态"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def get_system_info() -> Optional[Dict]:
    """获取系统信息"""
    try:
        response = requests.get(f"{API_BASE_URL}/system/info", timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logger.error(f"获取系统信息失败: {e}")
    return None


def render_header():
    """渲染页面头部"""
    st.markdown("""
    <div class="main-header">
        <h1>🎬 AIMovie Cloud</h1>
        <h3>智能视频解说生成器 - 云端版</h3>
        <p>完全基于云端API，无需GPU硬件，成本透明可控</p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.title("🎛️ 控制面板")
        
        # API状态检查
        api_healthy = check_api_health()
        if api_healthy:
            st.success("✅ API服务正常")
        else:
            st.error("❌ API服务不可用")
            st.write("请检查后端服务是否启动")
            st.code("python start.py")
        
        st.divider()
        
        # 系统信息
        system_info = get_system_info()
        if system_info:
            preset_info = system_info.get("preset", {})
            st.write("**当前配置**")
            st.write(f"方案: {preset_info.get('name', '未知')}")
            st.write(f"预估成本: {preset_info.get('estimated_cost', '未知')}")
            
            # 服务状态
            st.write("**服务状态**")
            st.write(f"LLM: {preset_info.get('available_llm', 0)}/{preset_info.get('llm_services', 0)}")
            st.write(f"TTS: {preset_info.get('available_tts', 0)}/{preset_info.get('tts_services', 0)}")
            st.write(f"视觉: {preset_info.get('available_vision', 0)}/{preset_info.get('vision_services', 0)}")
        
        st.divider()
        
        # 快速链接
        st.write("**快速链接**")
        st.markdown("- [📖 使用指南](https://github.com/cflank/AIMovie/blob/master/CLOUD_USAGE_GUIDE.md)")
        st.markdown("- [🔧 API文档](http://127.0.0.1:8000/docs)")
        st.markdown("- [🐛 问题反馈](https://github.com/cflank/AIMovie/issues)")
        st.markdown("- [💡 功能建议](https://github.com/cflank/AIMovie/issues/new?template=feature_request.md)")


def render_main_tabs():
    """渲染主要选项卡"""
    tabs = st.tabs([
        "🎯 配置选择", 
        "🎬 完整流程", 
        "🔍 分步处理", 
        "💰 成本管理", 
        "📊 系统状态",
        "📖 帮助文档"
    ])
    
    with tabs[0]:
        render_config_tab()
    
    with tabs[1]:
        render_complete_workflow_tab()
    
    with tabs[2]:
        render_step_by_step_tab()
    
    with tabs[3]:
        render_cost_management_tab()
    
    with tabs[4]:
        render_system_status_tab()
    
    with tabs[5]:
        render_help_tab()


def render_config_tab():
    """渲染配置选择选项卡"""
    st.header("🎯 大模型组合配置")
    
    # 预设选择器
    selected_preset = render_preset_selector()
    
    if selected_preset:
        st.success(f"配置已更新为: {selected_preset}")
        # 这里可以添加保存配置到环境变量的逻辑
        st.info("💡 提示: 配置更改后需要重启应用才能生效")
    
    st.divider()
    
    # 服务状态
    render_service_status()
    
    st.divider()
    
    # 详细服务信息
    render_detailed_service_info()
    
    st.divider()
    
    # 配置指南
    render_configuration_guide()


def render_complete_workflow_tab():
    """渲染完整流程选项卡"""
    st.header("🎬 一键完整处理")
    
    # 检查API状态
    if not check_api_health():
        st.error("❌ API服务不可用，请先启动后端服务")
        return
    
    st.info("📋 **处理流程**: 上传视频和字幕文件 → 基于字幕生成解说词 → 根据解说词分析视频并剪辑成短视频")
    
    render_video_subtitle_workflow()


def render_video_subtitle_workflow():
    """渲染视频+字幕的工作流程"""
    st.subheader("📹 基于字幕的智能视频解说生成")
    st.write("同时上传视频和字幕文件，基于字幕生成解说词，然后分析视频并剪辑成短视频")
    
    # 文件上传区域
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📹 上传视频文件**")
        uploaded_video = st.file_uploader(
            "选择视频文件",
            type=['mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv'],
            help="支持常见视频格式，最大500MB",
            key="video_upload"
        )
    
    with col2:
        st.write("**📄 上传字幕文件**")
        uploaded_subtitle = st.file_uploader(
            "选择字幕文件",
            type=['srt', 'vtt', 'ass', 'ssa', 'txt'],
            help="支持SRT、VTT、ASS、SSA、TXT格式",
            key="subtitle_upload"
        )
    
    if uploaded_video and uploaded_subtitle:
        # 显示文件信息
        st.write("**📁 文件信息**")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"视频: {uploaded_video.name}")
            st.write(f"大小: {uploaded_video.size / 1024 / 1024:.2f} MB")
        with col2:
            st.write(f"字幕: {uploaded_subtitle.name}")
            st.write(f"大小: {uploaded_subtitle.size / 1024:.2f} KB")
        
        st.divider()
        
        # 解说模式选择
        st.subheader("🎭 解说模式配置")
        
        narration_mode = st.radio(
            "选择解说模式",
            ["third_person", "character"],
            format_func=lambda x: {
                "third_person": "🎯 第三方视角（客观解说）",
                "character": "👤 角色第一人称（主观解说）"
            }[x],
            help="第三方视角：以旁观者身份客观解说；角色第一人称：以指定角色身份主观解说"
        )
        
        character_name = ""
        if narration_mode == "character":
            character_name = st.text_input(
                "角色名称",
                placeholder="请输入要扮演的角色名称，如：小明、张老师、主角等",
                help="将以此角色的第一人称视角进行解说"
            )
            if not character_name:
                st.warning("⚠️ 请输入角色名称")
        
        # 处理参数配置
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎨 解说风格")
            narration_style = st.selectbox(
                "解说风格",
                ["professional", "humorous", "emotional", "suspenseful", "casual", "dramatic"],
                format_func=lambda x: {
                    "professional": "🎯 专业严肃",
                    "humorous": "😄 幽默风趣", 
                    "emotional": "❤️ 情感丰富",
                    "suspenseful": "🔍 悬疑紧张",
                    "casual": "😊 轻松随意",
                    "dramatic": "🎭 戏剧化"
                }[x]
            )
            
            target_audience = st.selectbox(
                "目标观众",
                ["general", "young", "professional", "children"],
                format_func=lambda x: {
                    "general": "👥 普通大众",
                    "young": "🧑‍💼 年轻观众",
                    "professional": "👔 专业人士", 
                    "children": "👶 儿童观众"
                }[x]
            )
        
        with col2:
            st.subheader("🎙️ 语音配置")
            
            # 获取可用的TTS服务
            try:
                response = requests.get(f"{API_BASE_URL}/tts/voices")
                if response.status_code == 200:
                    voices = response.json().get("voices", [])
                    voice_options = {voice["name"]: voice["display_name"] for voice in voices}
                else:
                    voice_options = {"default": "默认语音"}
            except:
                voice_options = {"default": "默认语音"}
            
            selected_voice = st.selectbox("语音风格", list(voice_options.keys()), format_func=lambda x: voice_options[x])
            
            speech_speed = st.slider("语速", 0.5, 2.0, 1.0, 0.1)
            speech_pitch = st.slider("音调", 0.5, 2.0, 1.0, 0.1)
            speech_volume = st.slider("音量", 0.5, 2.0, 1.0, 0.1)
        
        # 成本估算
        st.subheader("💰 成本估算")
        try:
            # 估算参数
            estimated_frames = 50  # 默认帧数
            estimated_text_length = 500  # 默认文本长度
            estimated_audio_length = 500  # 默认音频长度
            
            response = requests.get(
                f"{API_BASE_URL}/cost/estimate",
                params={
                    "text_length": estimated_text_length,
                    "audio_length": estimated_audio_length,
                    "frame_count": estimated_frames
                }
            )
            
            if response.status_code == 200:
                cost_data = response.json()
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("LLM成本", f"¥{cost_data['llm_cost']:.4f}")
                with col2:
                    st.metric("TTS成本", f"¥{cost_data['tts_cost']:.4f}")
                with col3:
                    st.metric("视觉成本", f"¥{cost_data['vision_cost']:.4f}")
                with col4:
                    st.metric("总成本", f"¥{cost_data['total_cost']:.4f}")
                
                # 成本详情
                with st.expander("成本详情"):
                    for service_type, cost_info in cost_data['breakdown'].items():
                        st.write(f"• {cost_info}")
            
        except Exception as e:
            st.warning(f"无法获取成本估算: {e}")
        
        # 开始处理按钮
        can_process = True
        if narration_mode == "character" and not character_name:
            can_process = False
        
        if can_process:
            if st.button("🚀 开始完整处理", type="primary", use_container_width=True):
                process_video_subtitle_complete(
                    uploaded_video,
                    uploaded_subtitle,
                    narration_mode,
                    character_name,
                    narration_style, 
                    target_audience,
                    selected_voice,
                    speech_speed,
                    speech_pitch,
                    speech_volume
                )
        else:
            st.button("🚀 开始完整处理", type="primary", use_container_width=True, disabled=True)
    
    elif uploaded_video or uploaded_subtitle:
        st.warning("⚠️ 请同时上传视频文件和字幕文件才能开始处理")


def process_video_subtitle_complete(uploaded_video, uploaded_subtitle, narration_mode, character_name,
                                   narration_style, target_audience, voice, speed, pitch, volume):
    """处理视频+字幕的完整流程"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # 1. 上传视频文件
        status_text.text("📤 上传视频文件...")
        video_files = {"file": (uploaded_video.name, uploaded_video.getvalue(), uploaded_video.type)}
        response = requests.post(f"{API_BASE_URL}/upload/video", files=video_files)
        
        if response.status_code != 200:
            st.error(f"视频文件上传失败: {response.text}")
            return
        
        video_upload_result = response.json()
        video_path = video_upload_result["file_path"]
        progress_bar.progress(10)
        
        # 2. 上传字幕文件
        status_text.text("📤 上传字幕文件...")
        subtitle_files = {"file": (uploaded_subtitle.name, uploaded_subtitle.getvalue(), uploaded_subtitle.type)}
        response = requests.post(f"{API_BASE_URL}/upload/subtitle", files=subtitle_files)
        
        if response.status_code != 200:
            st.error(f"字幕文件上传失败: {response.text}")
            return
        
        subtitle_upload_result = response.json()
        subtitle_path = subtitle_upload_result["file_path"]
        progress_bar.progress(20)
        
        # 3. 解析字幕
        status_text.text("📝 解析字幕内容...")
        subtitle_data = {"subtitle_path": subtitle_path}
        response = requests.post(f"{API_BASE_URL}/subtitle/parse", params=subtitle_data)
        
        if response.status_code != 200:
            st.error(f"字幕解析失败: {response.text}")
            return
        
        subtitle_result = response.json()
        progress_bar.progress(35)
        
        # 4. 基于字幕生成解说
        status_text.text("🎭 生成解说词...")
        narration_data = {
            "subtitle_content": subtitle_result["content"],
            "subtitle_analysis": subtitle_result["analysis"],
            "mode": narration_mode,
            "character_name": character_name if narration_mode == "character" else "",
            "style": narration_style,
            "target_audience": target_audience
        }
        response = requests.post(f"{API_BASE_URL}/subtitle/narration/generate", json=narration_data)
        
        if response.status_code != 200:
            st.error(f"解说生成失败: {response.text}")
            return
        
        narration_result = response.json()
        progress_bar.progress(55)
        
        # 6. 根据解说词分析视频
        status_text.text("🔍 根据解说词分析视频...")
        video_analysis_data = {
            "video_path": video_path,
            "narration_segments": narration_result["segments"],
            "analysis_mode": "narration_guided"  # 基于解说词指导的分析
        }
        response = requests.post(f"{API_BASE_URL}/analyze/video/guided", json=video_analysis_data)
        
        if response.status_code != 200:
            st.error(f"视频分析失败: {response.text}")
            return
        
        video_analysis_result = response.json()
        progress_bar.progress(70)
        
        # 7. 语音合成
        status_text.text("🎙️ 合成语音...")
        tts_data = {
            "segments": narration_result["segments"],
            "voice_style": voice,
            "speed": speed,
            "pitch": pitch,
            "volume": volume
        }
        response = requests.post(f"{API_BASE_URL}/tts/batch", json=tts_data)
        
        if response.status_code != 200:
            st.error(f"语音合成失败: {response.text}")
            return
        
        tts_result = response.json()
        progress_bar.progress(85)
        
        # 8. 剪辑生成短视频
        status_text.text("✂️ 剪辑生成短视频...")
        video_edit_data = {
            "original_video": video_path,
            "video_analysis": video_analysis_result,
            "narration_segments": narration_result["segments"],
            "audio_files": tts_result["audio_files"],
            "edit_style": "highlight_based"  # 基于重点内容剪辑
        }
        response = requests.post(f"{API_BASE_URL}/video/edit/short", json=video_edit_data)
        
        if response.status_code != 200:
            st.error(f"视频剪辑失败: {response.text}")
            return
        
        final_result = response.json()
        progress_bar.progress(100)
        status_text.text("✅ 处理完成!")
        
        # 显示结果
        st.success("🎉 短视频生成完成!")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**处理结果**")
            st.write(f"• 原视频: {uploaded_video.name}")
            st.write(f"• 字幕文件: {uploaded_subtitle.name}")
            st.write(f"• 解说段数: {len(narration_result['segments'])}")
            st.write(f"• 短视频时长: {final_result.get('duration', '未知')}秒")
            st.write(f"• 处理时长: {final_result.get('processing_time', '未知')}")
            st.write(f"• 实际成本: ¥{final_result.get('actual_cost', 0):.4f}")
        
        with col2:
            # 下载链接
            if "output_video" in final_result:
                download_url = f"{API_BASE_URL}/files/download/video/{final_result['output_video']}"
                st.markdown(f"[📥 下载短视频]({download_url})")
            
            if "narration_text" in final_result:
                download_url = f"{API_BASE_URL}/files/download/text/{final_result['narration_text']}"
                st.markdown(f"[📄 下载解说文本]({download_url})")
            
            if "analysis_report" in final_result:
                download_url = f"{API_BASE_URL}/files/download/text/{final_result['analysis_report']}"
                st.markdown(f"[📊 下载分析报告]({download_url})")
        
        # 显示解说内容预览
        with st.expander("📝 解说内容预览"):
            for i, segment in enumerate(narration_result["segments"]):
                st.write(f"**段落 {i+1}** ({segment['start_time']:.1f}s - {segment['end_time']:.1f}s)")
                st.write(segment["text"])
                st.write("---")
        
        # 显示视频分析结果
        if "highlights" in video_analysis_result:
            with st.expander("🎯 视频重点片段"):
                for i, highlight in enumerate(video_analysis_result["highlights"]):
                    st.write(f"**片段 {i+1}** ({highlight['start']:.1f}s - {highlight['end']:.1f}s)")
                    st.write(f"重要度: {highlight['importance']:.2f}")
                    st.write(f"描述: {highlight['description']}")
                    st.write("---")
    
    except Exception as e:
        st.error(f"处理过程中发生错误: {e}")
        logger.error(f"视频处理错误: {e}")








def render_step_by_step_tab():
    """渲染分步处理选项卡"""
    st.header("🔍 分步处理")
    
    st.info("📋 **新流程**: 上传视频和字幕 → 分析字幕 → 生成解说 → 分析视频 → 剪辑短视频")
    
    step_tabs = st.tabs(["📤 上传文件", "📝 字幕分析", "🎭 解说生成", "🔍 视频分析", "✂️ 视频剪辑"])
    
    with step_tabs[0]:
        render_upload_files_step()
    
    with step_tabs[1]:
        render_subtitle_analysis_step()
    
    with step_tabs[2]:
        render_subtitle_narration_step()
    
    with step_tabs[3]:
        render_guided_video_analysis_step()
    
    with step_tabs[4]:
        render_video_editing_step()


def render_upload_files_step():
    """渲染文件上传步骤"""
    st.subheader("📤 上传视频和字幕文件")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📹 上传视频文件**")
        uploaded_video = st.file_uploader(
            "选择视频文件",
            type=['mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv'],
            key="step_video_upload"
        )
        
        if uploaded_video:
            st.write(f"文件名: {uploaded_video.name}")
            st.write(f"文件大小: {uploaded_video.size / 1024 / 1024:.2f} MB")
    
    with col2:
        st.write("**📄 上传字幕文件**")
        uploaded_subtitle = st.file_uploader(
            "选择字幕文件",
            type=['srt', 'vtt', 'ass', 'ssa', 'txt'],
            key="step_subtitle_upload"
        )
        
        if uploaded_subtitle:
            st.write(f"文件名: {uploaded_subtitle.name}")
            st.write(f"文件大小: {uploaded_subtitle.size / 1024:.2f} KB")
    
    if uploaded_video and uploaded_subtitle:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("上传视频文件", use_container_width=True):
                with st.spinner("上传视频中..."):
                    files = {"file": (uploaded_video.name, uploaded_video.getvalue(), uploaded_video.type)}
                    response = requests.post(f"{API_BASE_URL}/upload/video", files=files)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"视频上传成功!")
                        st.session_state.uploaded_video_path = result['file_path']
                    else:
                        st.error(f"视频上传失败: {response.text}")
        
        with col2:
            if st.button("上传字幕文件", use_container_width=True):
                with st.spinner("上传字幕中..."):
                    files = {"file": (uploaded_subtitle.name, uploaded_subtitle.getvalue(), uploaded_subtitle.type)}
                    response = requests.post(f"{API_BASE_URL}/upload/subtitle", files=files)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"字幕上传成功!")
                        st.session_state.uploaded_subtitle_path = result['file_path']
                    else:
                        st.error(f"字幕上传失败: {response.text}")
    
    # 显示上传状态
    if 'uploaded_video_path' in st.session_state and 'uploaded_subtitle_path' in st.session_state:
        st.success("✅ 视频和字幕文件都已上传完成，可以进行下一步！")
        st.write(f"视频路径: {st.session_state.uploaded_video_path}")
        st.write(f"字幕路径: {st.session_state.uploaded_subtitle_path}")
    elif 'uploaded_video_path' in st.session_state:
        st.info("📹 视频已上传，还需要上传字幕文件")
    elif 'uploaded_subtitle_path' in st.session_state:
        st.info("📄 字幕已上传，还需要上传视频文件")
    else:
        st.warning("⚠️ 请同时上传视频和字幕文件")


def render_subtitle_analysis_step():
    """渲染字幕分析步骤"""
    st.subheader("📝 字幕分析")
    
    if 'uploaded_subtitle_path' not in st.session_state:
        st.warning("请先上传字幕文件")
        return
    
    subtitle_path = st.session_state.uploaded_subtitle_path
    st.write(f"分析字幕: {subtitle_path}")
    
    if st.button("开始分析字幕", type="primary"):
        with st.spinner("分析字幕中..."):
            data = {"subtitle_path": subtitle_path}
            response = requests.post(f"{API_BASE_URL}/subtitle/parse", params=data)
            
            if response.status_code == 200:
                result = response.json()
                task_id = result["task_id"]
                
                # 轮询任务状态
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                while True:
                    time.sleep(2)
                    status_response = requests.get(f"{API_BASE_URL}/task/{task_id}")
                    
                    if status_response.status_code == 200:
                        task_status = status_response.json()
                        progress = task_status.get("progress", 0)
                        message = task_status.get("message", "处理中...")
                        status = task_status.get("status", "running")
                        
                        progress_bar.progress(progress)
                        status_text.text(f"📊 {message}")
                        
                        if status == "completed":
                            st.success("字幕分析完成!")
                            st.session_state.subtitle_analysis = task_status.get("result", {})
                            
                            # 显示分析结果
                            result = st.session_state.subtitle_analysis
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write("**字幕统计**")
                                # 修正数据结构访问
                                subtitle_segments = result.get("subtitle_segments", [])
                                metadata = result.get("metadata", {})
                                st.write(f"• 总段数: {metadata.get('total_segments', len(subtitle_segments))}")
                                st.write(f"• 总时长: {metadata.get('total_duration', 0):.1f}秒")
                                st.write(f"• 字符数: {metadata.get('total_characters', 0)}")
                            
                            with col2:
                                st.write("**内容分析**")
                                analysis = result.get("analysis", {})
                                characters = analysis.get('characters', [])
                                themes = analysis.get('themes', [])
                                emotions = analysis.get('emotions', [])
                                st.write(f"• 主要角色: {', '.join(characters[:3]) if characters else '无'}")
                                st.write(f"• 主题: {', '.join(themes[:3]) if themes else '学习, 成长'}")
                                st.write(f"• 情感倾向: {', '.join(emotions[:3]) if emotions else '未知'}")
                            
                            # 显示字幕预览
                            with st.expander("📝 字幕内容预览"):
                                segments = result.get("subtitle_segments", [])
                                for i, segment in enumerate(segments[:10]):
                                    st.write(f"**{segment.get('start_time', 0):.1f}s - {segment.get('end_time', 0):.1f}s**")
                                    st.write(segment.get("text", ""))
                                    st.write("---")
                                
                                if len(segments) > 10:
                                    st.write(f"... 还有 {len(segments) - 10} 段字幕")
                            
                            break
                        elif status == "failed":
                            st.error(f"字幕分析失败: {task_status.get('error', '未知错误')}")
                            break
                    else:
                        st.error("无法获取任务状态")
                        break
            else:
                st.error(f"字幕分析失败: {response.text}")
    
    # 显示已有的分析结果
    if 'subtitle_analysis' in st.session_state:
        st.info("✅ 字幕分析已完成，可以进行下一步生成解说！")


def render_subtitle_narration_step():
    """渲染基于字幕的解说生成步骤"""
    st.subheader("🎭 基于字幕生成解说")
    
    if 'subtitle_analysis' not in st.session_state:
        st.warning("请先完成字幕分析")
        return
    
    # 解说模式配置
    st.write("**解说模式配置**")
    narration_mode = st.radio(
        "选择解说模式",
        ["third_person", "character"],
        format_func=lambda x: {
            "third_person": "🎯 第三方视角（客观解说）",
            "character": "👤 角色第一人称（主观解说）"
        }[x],
        help="第三方视角：以旁观者身份客观解说；角色第一人称：以指定角色身份主观解说"
    )
    
    character_name = ""
    if narration_mode == "character":
        character_name = st.text_input(
            "角色名称",
            placeholder="请输入要扮演的角色名称，如：小明、张老师、主角等",
            help="将以此角色的第一人称视角进行解说"
        )
        if not character_name:
            st.warning("⚠️ 请输入角色名称")
    
    col1, col2 = st.columns(2)
    
    with col1:
        style = st.selectbox(
            "解说风格", 
            ["professional", "humorous", "emotional", "suspenseful", "casual", "dramatic"],
            format_func=lambda x: {
                "professional": "🎯 专业严肃",
                "humorous": "😄 幽默风趣", 
                "emotional": "❤️ 情感丰富",
                "suspenseful": "🔍 悬疑紧张",
                "casual": "😊 轻松随意",
                "dramatic": "🎭 戏剧化"
            }[x]
        )
    
    with col2:
        target_audience = st.selectbox(
            "目标观众", 
            ["general", "young", "professional", "children"],
            format_func=lambda x: {
                "general": "👥 普通大众",
                "young": "🧑‍💼 年轻观众",
                "professional": "👔 专业人士", 
                "children": "👶 儿童观众"
            }[x]
        )
    
    # 解说模式说明
    if narration_mode == "third_person":
        st.info("""
        **🎯 第三方视角（客观解说）**
        - 以客观中立的立场进行解说
        - 分析角色的行为和动机
        - 解释背景信息和情节发展
        - 适合纪录片、教学视频等
        
        示例：*"在这个场景中，主角表现出了内心的矛盾..."*
        """)
    else:
        st.info(f"""
        **👤 角色第一人称（{character_name or '角色名'}）**
        - 以指定角色的身份进行解说
        - 表达角色的个人感受和想法
        - 使用第一人称语气（我、我们等）
        - 适合角色扮演、个人Vlog等
        
        示例：*"我在这里感到非常紧张，因为..."*
        """)
    
    can_generate = True
    if narration_mode == "character" and not character_name:
        can_generate = False
    
    if st.button("生成解说", type="primary", disabled=not can_generate):
        # 保存用户选择的参数，用于重新生成
        st.session_state.last_narration_mode = narration_mode
        st.session_state.last_character_name = character_name
        st.session_state.last_narration_style = style
        st.session_state.last_target_audience = target_audience
        
        with st.spinner("生成解说中..."):
            data = {
                "subtitle_data": st.session_state.subtitle_analysis,
                "narration_mode": narration_mode,
                "character_name": character_name if narration_mode == "character" else "",
                "style": style,
                "target_audience": target_audience
            }
            response = requests.post(f"{API_BASE_URL}/subtitle/narration/generate", json=data)
            
            if response.status_code == 200:
                task_result = response.json()
                task_id = task_result["task_id"]
                
                # 轮询任务状态
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                while True:
                    time.sleep(2)
                    status_response = requests.get(f"{API_BASE_URL}/task/{task_id}")
                    
                    if status_response.status_code == 200:
                        task_status = status_response.json()
                        progress = task_status.get("progress", 0)
                        message = task_status.get("message", "生成中...")
                        status = task_status.get("status", "running")
                        
                        progress_bar.progress(progress)
                        status_text.text(f"🎭 {message}")
                        
                        if status == "completed":
                            st.success("解说生成完成!")
                            result = task_status.get("result", {})
                            st.session_state.narration_result = result
                            
                            # 显示和编辑解说内容
                            narration_segments = result.get("narration_segments", [])
                            if narration_segments:
                                st.subheader("📝 解说内容编辑")
                                st.info("💡 您可以直接编辑下面的解说内容，修改后点击'保存修改'按钮")
                                
                                # 创建编辑表单
                                with st.form("edit_narration_form"):
                                    edited_segments = []
                                    
                                    for i, segment in enumerate(narration_segments):
                                        st.write(f"**段落 {i+1}** ({segment.get('start_time', 0):.1f}s - {segment.get('end_time', 0):.1f}s)")
                                        
                                        # 可编辑的文本区域
                                        edited_text = st.text_area(
                                            f"解说内容 {i+1}",
                                            value=segment.get("text", ""),
                                            height=80,
                                            key=f"narration_text_{i}",
                                            help="您可以修改这段解说的内容"
                                        )
                                        
                                        # 保存编辑后的段落
                                        edited_segment = segment.copy()
                                        edited_segment["text"] = edited_text
                                        edited_segments.append(edited_segment)
                                        
                                        st.write("---")
                                    
                                    # 保存按钮
                                    col1, col2, col3 = st.columns([1, 1, 1])
                                    with col2:
                                        if st.form_submit_button("💾 保存修改", type="primary"):
                                            # 更新session state中的解说结果
                                            updated_result = result.copy()
                                            updated_result["narration_segments"] = edited_segments
                                            st.session_state.narration_result = updated_result
                                            st.success("✅ 解说内容已保存！")
                                            st.rerun()
                                
                                # 显示预览和操作按钮
                                with st.expander("👀 解说预览", expanded=False):
                                    current_segments = st.session_state.narration_result.get("narration_segments", [])
                                    for i, segment in enumerate(current_segments):
                                        st.write(f"**段落 {i+1}** ({segment.get('start_time', 0):.1f}s - {segment.get('end_time', 0):.1f}s)")
                                        st.write(f"📝 {segment.get('text', '')}")
                                        st.write("---")
                                
                                # 操作按钮
                                st.subheader("🔄 解说操作")
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    if st.button("🔄 重新生成解说", help="使用相同参数重新生成解说内容"):
                                        # 重新生成解说
                                        with st.spinner("正在重新生成解说..."):
                                            narration_data = {
                                                "subtitle_data": st.session_state.subtitle_analysis,
                                                "narration_mode": st.session_state.get('last_narration_mode', 'third_person'),
                                                "character_name": st.session_state.get('last_character_name', ''),
                                                "style": st.session_state.get('last_narration_style', 'professional'),
                                                "target_audience": st.session_state.get('last_target_audience', 'general')
                                            }
                                            
                                            response = requests.post(f"{API_BASE_URL}/subtitle/narration/generate", json=narration_data)
                                            
                                            if response.status_code == 200:
                                                task_result = response.json()
                                                task_id = task_result["task_id"]
                                                
                                                # 等待任务完成
                                                while True:
                                                    time.sleep(2)
                                                    task_response = requests.get(f"{API_BASE_URL}/task/{task_id}")
                                                    
                                                    if task_response.status_code == 200:
                                                        task_status = task_response.json()
                                                        status = task_status.get("status", "running")
                                                        
                                                        if status == "completed":
                                                            new_result = task_status.get("result", {})
                                                            st.session_state.narration_result = new_result
                                                            st.success("✅ 解说重新生成完成！")
                                                            st.rerun()
                                                            break
                                                        elif status == "failed":
                                                            st.error(f"解说重新生成失败: {task_status.get('error', '未知错误')}")
                                                            break
                                                    else:
                                                        st.error("无法获取任务状态")
                                                        break
                                            else:
                                                st.error(f"解说重新生成失败: {response.text}")
                                
                                with col2:
                                    if st.button("📋 复制解说文本", help="复制所有解说内容到剪贴板"):
                                        current_segments = st.session_state.narration_result.get("narration_segments", [])
                                        full_text = "\n\n".join([
                                            f"段落 {i+1} ({segment.get('start_time', 0):.1f}s - {segment.get('end_time', 0):.1f}s):\n{segment.get('text', '')}"
                                            for i, segment in enumerate(current_segments)
                                        ])
                                        
                                        # 使用JavaScript复制到剪贴板
                                        st.components.v1.html(f"""
                                        <script>
                                        navigator.clipboard.writeText(`{full_text}`).then(function() {{
                                            console.log('Text copied to clipboard');
                                        }});
                                        </script>
                                        """, height=0)
                                        st.success("📋 解说文本已复制到剪贴板！")
                                
                                with col3:
                                    if st.button("💾 导出解说文件", help="导出解说内容为文本文件"):
                                        current_segments = st.session_state.narration_result.get("narration_segments", [])
                                        export_text = "\n\n".join([
                                            f"段落 {i+1} ({segment.get('start_time', 0):.1f}s - {segment.get('end_time', 0):.1f}s):\n{segment.get('text', '')}"
                                            for i, segment in enumerate(current_segments)
                                        ])
                                        
                                        st.download_button(
                                            label="📥 下载解说文本",
                                            data=export_text,
                                            file_name=f"narration_{int(time.time())}.txt",
                                            mime="text/plain"
                                        )
                                        
                            else:
                                st.warning("未生成解说内容")
                            break
                        elif status == "failed":
                            st.error(f"解说生成失败: {task_status.get('error', '未知错误')}")
                            break
                    else:
                        st.error("无法获取任务状态")
                        break
            else:
                st.error(f"解说生成失败: {response.text}")
    
    # 显示已有的解说结果
    if 'narration_result' in st.session_state:
        st.info("✅ 解说生成已完成，可以进行下一步视频分析！")


def render_guided_video_analysis_step():
    """渲染基于解说词的视频分析步骤"""
    st.subheader("🔍 基于解说词分析视频")
    
    if 'uploaded_video_path' not in st.session_state:
        st.warning("请先上传视频文件")
        return
    
    if 'narration_result' not in st.session_state:
        st.warning("请先完成解说生成")
        return
    
    video_path = st.session_state.uploaded_video_path
    narration_segments = st.session_state.narration_result.get("narration_segments", [])
    
    st.write(f"分析视频: {video_path}")
    st.write(f"基于 {len(narration_segments)} 段解说进行分析")
    
    if st.button("开始基于解说词的视频分析", type="primary"):
        with st.spinner("分析视频中..."):
            data = {
                "video_path": video_path,
                "narration_segments": narration_segments,
                "analysis_mode": "narration_guided"
            }
            response = requests.post(f"{API_BASE_URL}/analyze/video/guided", json=data)
            
            if response.status_code == 200:
                result = response.json()
                task_id = result["task_id"]
                
                # 轮询任务状态
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                while True:
                    time.sleep(2)
                    status_response = requests.get(f"{API_BASE_URL}/task/{task_id}")
                    
                    if status_response.status_code == 200:
                        task_status = status_response.json()
                        progress = task_status.get("progress", 0)
                        message = task_status.get("message", "处理中...")
                        status = task_status.get("status", "running")
                        
                        progress_bar.progress(progress)
                        status_text.text(f"📊 {message}")
                        
                        if status == "completed":
                            st.success("视频分析完成!")
                            st.session_state.video_analysis = task_status.get("result", {})
                            
                            # 显示分析结果
                            result = st.session_state.video_analysis
                            highlights = result.get("highlights", [])
                            
                            st.write(f"**发现 {len(highlights)} 个重点片段**")
                            
                            # 显示重点片段
                            with st.expander("🎯 视频重点片段"):
                                for i, highlight in enumerate(highlights):
                                    st.write(f"**片段 {i+1}** ({highlight['start']:.1f}s - {highlight['end']:.1f}s)")
                                    st.write(f"重要度: {highlight['importance']:.2f}")
                                    st.write(f"描述: {highlight['description']}")
                                    st.write(f"解说: {highlight['narration']}")
                                    st.write("---")
                            
                            break
                        elif status == "failed":
                            st.error(f"视频分析失败: {task_status.get('error', '未知错误')}")
                            break
                    else:
                        st.error("无法获取任务状态")
                        break
            else:
                st.error(f"视频分析失败: {response.text}")
    
    # 显示已有的分析结果
    if 'video_analysis' in st.session_state:
        st.info("✅ 视频分析已完成，可以进行下一步视频剪辑！")


def render_video_editing_step():
    """渲染视频剪辑步骤"""
    st.subheader("✂️ 剪辑生成短视频")
    
    if 'uploaded_video_path' not in st.session_state:
        st.warning("请先上传视频文件")
        return
    
    if 'narration_result' not in st.session_state:
        st.warning("请先完成解说生成")
        return
    
    if 'video_analysis' not in st.session_state:
        st.warning("请先完成视频分析")
        return
    
    video_path = st.session_state.uploaded_video_path
    narration_segments = st.session_state.narration_result.get("narration_segments", [])
    video_analysis = st.session_state.video_analysis
    
    st.write("**剪辑配置**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 获取可用语音
        try:
            response = requests.get(f"{API_BASE_URL}/tts/voices")
            if response.status_code == 200:
                voices = response.json().get("voices", [])
                voice_options = {voice["name"]: voice["display_name"] for voice in voices}
                if not voice_options:
                    voice_options = {"female_gentle": "温柔女声"}
            else:
                voice_options = {"female_gentle": "温柔女声"}
        except:
            voice_options = {"female_gentle": "温柔女声"}
        
        selected_voice = st.selectbox("语音风格", list(voice_options.keys()), format_func=lambda x: voice_options[x])
        
        # 确保选择的语音不为空
        if not selected_voice:
            selected_voice = "female_gentle"
        speech_speed = st.slider("语速", 0.5, 2.0, 1.0, 0.1)
    
    with col2:
        speech_pitch = st.slider("音调", 0.5, 2.0, 1.0, 0.1)
        speech_volume = st.slider("音量", 0.5, 2.0, 1.0, 0.1)
    
    edit_style = st.selectbox(
        "剪辑风格",
        ["highlight_based", "narrative_flow", "dynamic_cuts"],
        format_func=lambda x: {
            "highlight_based": "🎯 基于重点内容",
            "narrative_flow": "📖 叙事流畅",
            "dynamic_cuts": "⚡ 动态剪辑"
        }[x]
    )
    
    if st.button("开始剪辑短视频", type="primary"):
        with st.spinner("剪辑短视频中..."):
            # 验证数据
            if not narration_segments:
                st.error("没有解说段落可用于语音合成")
                return
            
            if not selected_voice:
                st.error("请选择语音风格")
                return
            
            # 首先进行语音合成
            tts_data = {
                "segments": narration_segments,
                "voice_style": str(selected_voice),  # 确保是字符串
                "speed": float(speech_speed),
                "pitch": float(speech_pitch),
                "volume": float(speech_volume)
            }
            
            # 调试信息
            st.write(f"🔍 调试信息: 语音风格={selected_voice}, 段落数={len(narration_segments)}")
            
            tts_response = requests.post(f"{API_BASE_URL}/tts/batch", json=tts_data)
            
            if tts_response.status_code == 200:
                tts_result = tts_response.json()
                tts_task_id = tts_result["task_id"]
                
                # 等待TTS完成
                st.write("🎙️ 正在合成语音...")
                while True:
                    time.sleep(2)
                    tts_status_response = requests.get(f"{API_BASE_URL}/task/{tts_task_id}")
                    
                    if tts_status_response.status_code == 200:
                        tts_task_status = tts_status_response.json()
                        if tts_task_status.get("status") == "completed":
                            audio_files = tts_task_status.get("result", {}).get("audio_files", [])
                            break
                        elif tts_task_status.get("status") == "failed":
                            st.error("语音合成失败")
                            return
                    else:
                        st.error("无法获取TTS任务状态")
                        return
                
                # 开始视频剪辑
                st.write("✂️ 正在剪辑视频...")
                edit_data = {
                    "original_video": video_path,
                    "video_analysis": video_analysis,
                    "narration_segments": narration_segments,
                    "audio_files": audio_files,
                    "edit_style": edit_style
                }
                edit_response = requests.post(f"{API_BASE_URL}/video/edit/short", json=edit_data)
                
                if edit_response.status_code == 200:
                    edit_result = edit_response.json()
                    edit_task_id = edit_result["task_id"]
                    
                    # 轮询剪辑任务状态
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    while True:
                        time.sleep(2)
                        edit_status_response = requests.get(f"{API_BASE_URL}/task/{edit_task_id}")
                        
                        if edit_status_response.status_code == 200:
                            edit_task_status = edit_status_response.json()
                            progress = edit_task_status.get("progress", 0)
                            message = edit_task_status.get("message", "处理中...")
                            status = edit_task_status.get("status", "running")
                            
                            progress_bar.progress(progress)
                            status_text.text(f"📊 {message}")
                            
                            if status == "completed":
                                st.success("🎉 短视频剪辑完成!")
                                final_result = edit_task_status.get("result", {})
                                
                                # 显示结果
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.write("**剪辑结果**")
                                    st.write(f"• 短视频时长: {final_result.get('duration', 0):.1f}秒")
                                    st.write(f"• 文件大小: {final_result.get('file_size', '未知')}")
                                    st.write(f"• 处理时长: {final_result.get('processing_time', '未知')}")
                                    st.write(f"• 实际成本: ¥{final_result.get('actual_cost', 0):.4f}")
                                
                                with col2:
                                    st.write("**下载链接**")
                                    if "output_video" in final_result:
                                        download_url = f"{API_BASE_URL}/files/download/video/{final_result['output_video']}"
                                        st.markdown(f"[📥 下载短视频]({download_url})")
                                    
                                    if "analysis_report" in final_result:
                                        download_url = f"{API_BASE_URL}/files/download/text/{final_result['analysis_report']}"
                                        st.markdown(f"[📊 下载分析报告]({download_url})")
                                
                                break
                            elif status == "failed":
                                st.error(f"视频剪辑失败: {edit_task_status.get('error', '未知错误')}")
                                break
                        else:
                            st.error("无法获取剪辑任务状态")
                            break
                else:
                    st.error(f"视频剪辑失败: {edit_response.text}")
            else:
                st.error(f"语音合成失败: {tts_response.text}")



def render_cost_management_tab():
    """渲染成本管理选项卡"""
    st.header("💰 成本管理")
    
    # 成本计算器
    render_cost_calculator()
    
    st.divider()
    
    # 成本统计
    st.subheader("📊 成本统计")
    try:
        response = requests.get(f"{API_BASE_URL}/cost/stats")
        if response.status_code == 200:
            stats = response.json()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("今日成本", f"¥{stats.get('daily_cost', 0):.4f}")
            with col2:
                st.metric("本月成本", f"¥{stats.get('monthly_cost', 0):.4f}")
            with col3:
                st.metric("总成本", f"¥{stats.get('total_cost', 0):.4f}")
            with col4:
                st.metric("处理视频数", stats.get('video_count', 0))
            
            # 成本限制
            st.subheader("⚙️ 成本限制")
            col1, col2 = st.columns(2)
            with col1:
                daily_limit = stats.get('daily_limit', 50)
                daily_usage = stats.get('daily_cost', 0) / daily_limit * 100
                st.metric("日度限制", f"¥{daily_limit}", f"{daily_usage:.1f}%")
                st.progress(min(daily_usage / 100, 1.0))
            
            with col2:
                monthly_limit = stats.get('monthly_limit', 500)
                monthly_usage = stats.get('monthly_cost', 0) / monthly_limit * 100
                st.metric("月度限制", f"¥{monthly_limit}", f"{monthly_usage:.1f}%")
                st.progress(min(monthly_usage / 100, 1.0))
        
    except Exception as e:
        st.error(f"无法获取成本统计: {e}")
    
    st.divider()
    
    # 方案对比
    render_preset_comparison()


def render_system_status_tab():
    """渲染系统状态选项卡"""
    st.header("📊 系统状态")
    
    # 服务状态
    render_service_status()
    
    st.divider()
    
    # 详细服务信息
    render_detailed_service_info()
    
    st.divider()
    
    # 系统信息
    st.subheader("🖥️ 系统信息")
    system_info = get_system_info()
    if system_info:
        with st.expander("详细信息"):
            st.json(system_info)
    
    # 健康检查
    st.subheader("🏥 健康检查")
    if st.button("执行健康检查"):
        with st.spinner("检查中..."):
            try:
                response = requests.get(f"{API_BASE_URL}/health/detailed")
                if response.status_code == 200:
                    health_data = response.json()
                    
                    for service, status in health_data.items():
                        if status["healthy"]:
                            st.success(f"✅ {service}: 正常")
                        else:
                            st.error(f"❌ {service}: {status.get('error', '异常')}")
                else:
                    st.error("健康检查失败")
            except Exception as e:
                st.error(f"健康检查错误: {e}")


def render_help_tab():
    """渲染帮助文档选项卡"""
    st.header("📖 帮助文档")
    
    help_tabs = st.tabs(["🚀 快速开始", "🔧 配置指南", "💡 使用技巧", "🐛 故障排除", "📞 获取支持"])
    
    with help_tabs[0]:
        st.subheader("🚀 快速开始")
        st.markdown("""
        ### 1. 选择配置方案
        - 在"配置选择"选项卡中选择适合的大模型组合
        - 推荐新手选择"最高性价比组合"
        
        ### 2. 配置API密钥
        - 编辑项目根目录下的 `.env` 文件
        - 添加所选方案对应的API密钥
        - 重启应用以加载新配置
        
        ### 3. 开始使用
        - 上传视频文件
        - 选择解说风格和语音参数
        - 点击"开始完整处理"
        - 等待处理完成并下载结果
        """)
    
    with help_tabs[1]:
        st.subheader("🔧 配置指南")
        render_configuration_guide()
    
    with help_tabs[2]:
        st.subheader("💡 使用技巧")
        st.markdown("""
        ### 成本优化技巧
        - 选择"最经济组合"可大幅降低成本
        - 减少视频帧采样频率
        - 使用Edge-TTS免费语音合成
        - 批量处理多个视频
        
        ### 质量提升技巧
        - 选择"质量最高组合"获得最佳效果
        - 增加视频帧采样数量
        - 使用高质量TTS服务
        - 选择合适的解说风格和目标观众
        
        ### 处理速度优化
        - 减少并发任务数量
        - 选择响应速度快的服务
        - 避免在高峰期处理
        """)
    
    with help_tabs[3]:
        st.subheader("🐛 故障排除")
        st.markdown("""
        ### 常见问题
        
        **API服务不可用**
        - 检查后端服务是否启动: `python start.py`
        - 检查端口是否被占用
        - 查看日志文件: `logs/aimovie_cloud.log`
        
        **API密钥配置错误**
        - 确认 `.env` 文件存在且格式正确
        - 验证API密钥是否有效
        - 检查网络连接
        
        **处理失败**
        - 检查视频文件格式是否支持
        - 确认文件大小不超过限制
        - 查看错误日志获取详细信息
        
        **成本超限**
        - 调整成本限制设置
        - 选择更经济的服务组合
        - 监控API使用量
        """)
    
    with help_tabs[4]:
        st.subheader("📞 获取支持")
        st.markdown("""
        ### 支持渠道
        
        - **GitHub Issues**: [报告问题](https://github.com/cflank/AIMovie/issues)
        - **功能建议**: [提交建议](https://github.com/cflank/AIMovie/issues/new?template=feature_request.md)
        - **讨论交流**: [GitHub Discussions](https://github.com/cflank/AIMovie/discussions)
        - **完整文档**: [使用指南](https://github.com/cflank/AIMovie/blob/master/CLOUD_USAGE_GUIDE.md)
        - **API文档**: [在线文档](http://127.0.0.1:8000/docs)
        
        ### 项目信息
        - **GitHub**: https://github.com/cflank/AIMovie
        - **版本**: v1.0.0
        - **许可证**: MIT License
        """)


def main():
    """主函数"""
    # 渲染页面头部
    render_header()
    
    # 渲染侧边栏
    render_sidebar()
    
    # 渲染主要内容
    render_main_tabs()
    
    # 页脚
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem 0;">
        <p>🎬 AIMovie Cloud v1.0.0 | 
        <a href="https://github.com/cflank/AIMovie" target="_blank">GitHub</a> | 
        <a href="https://github.com/cflank/AIMovie/blob/master/CLOUD_USAGE_GUIDE.md" target="_blank">文档</a> | 
        <a href="https://github.com/cflank/AIMovie/issues" target="_blank">反馈</a>
        </p>
        <p>Made with ❤️ by AIMovie Team</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main() 