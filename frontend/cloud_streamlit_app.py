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
    
    # 文件上传
    uploaded_file = st.file_uploader(
        "选择视频文件",
        type=['mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv'],
        help="支持常见视频格式，最大500MB"
    )
    
    if uploaded_file:
        # 显示文件信息
        st.write(f"**文件名**: {uploaded_file.name}")
        st.write(f"**文件大小**: {uploaded_file.size / 1024 / 1024:.2f} MB")
        
        # 处理参数配置
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎭 解说配置")
            narration_style = st.selectbox(
                "解说风格",
                ["professional", "humorous", "emotional", "suspenseful"],
                format_func=lambda x: {
                    "professional": "🎯 专业严肃",
                    "humorous": "😄 幽默风趣", 
                    "emotional": "❤️ 情感丰富",
                    "suspenseful": "🔍 悬疑紧张"
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
            
            narration_length = st.selectbox(
                "解说长度",
                ["short", "medium", "detailed"],
                index=1,
                format_func=lambda x: {
                    "short": "📝 简短",
                    "medium": "📄 中等",
                    "detailed": "📚 详细"
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
        if st.button("🚀 开始完整处理", type="primary", use_container_width=True):
            process_video_complete(
                uploaded_file, 
                narration_style, 
                target_audience, 
                narration_length,
                selected_voice,
                speech_speed,
                speech_pitch,
                speech_volume
            )


def process_video_complete(uploaded_file, narration_style, target_audience, narration_length, 
                          voice, speed, pitch, volume):
    """处理完整视频流程"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # 1. 上传文件
        status_text.text("📤 上传视频文件...")
        files = {"file": uploaded_file.getvalue()}
        response = requests.post(f"{API_BASE_URL}/upload/video", files=files)
        
        if response.status_code != 200:
            st.error(f"文件上传失败: {response.text}")
            return
        
        upload_result = response.json()
        video_path = upload_result["file_path"]
        progress_bar.progress(20)
        
        # 2. 分析视频
        status_text.text("🔍 分析视频内容...")
        analysis_data = {"video_path": video_path}
        response = requests.post(f"{API_BASE_URL}/analyze/video", json=analysis_data)
        
        if response.status_code != 200:
            st.error(f"视频分析失败: {response.text}")
            return
        
        analysis_result = response.json()
        progress_bar.progress(50)
        
        # 3. 生成解说
        status_text.text("📝 生成解说词...")
        narration_data = {
            "video_analysis": analysis_result,
            "style": narration_style,
            "target_audience": target_audience,
            "narration_length": narration_length
        }
        response = requests.post(f"{API_BASE_URL}/narration/generate", json=narration_data)
        
        if response.status_code != 200:
            st.error(f"解说生成失败: {response.text}")
            return
        
        narration_result = response.json()
        progress_bar.progress(70)
        
        # 4. 语音合成
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
        progress_bar.progress(90)
        
        # 5. 生成最终视频
        status_text.text("🎬 生成最终视频...")
        video_data = {
            "original_video": video_path,
            "narration_segments": narration_result["segments"],
            "audio_files": tts_result["audio_files"]
        }
        response = requests.post(f"{API_BASE_URL}/video/generate", json=video_data)
        
        if response.status_code != 200:
            st.error(f"视频生成失败: {response.text}")
            return
        
        final_result = response.json()
        progress_bar.progress(100)
        status_text.text("✅ 处理完成!")
        
        # 显示结果
        st.success("🎉 视频处理完成!")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**处理结果**")
            st.write(f"• 原视频: {uploaded_file.name}")
            st.write(f"• 解说段数: {len(narration_result['segments'])}")
            st.write(f"• 处理时长: {final_result.get('processing_time', '未知')}")
            st.write(f"• 实际成本: ¥{final_result.get('actual_cost', 0):.4f}")
        
        with col2:
            # 下载链接
            if "output_video" in final_result:
                download_url = f"{API_BASE_URL}/files/download/video/{final_result['output_video']}"
                st.markdown(f"[📥 下载解说视频]({download_url})")
            
            if "narration_text" in final_result:
                download_url = f"{API_BASE_URL}/files/download/text/{final_result['narration_text']}"
                st.markdown(f"[📄 下载解说文本]({download_url})")
        
        # 显示解说内容预览
        with st.expander("📝 解说内容预览"):
            for i, segment in enumerate(narration_result["segments"]):
                st.write(f"**段落 {i+1}** ({segment['start_time']:.1f}s - {segment['end_time']:.1f}s)")
                st.write(segment["text"])
                st.write("---")
    
    except Exception as e:
        st.error(f"处理过程中发生错误: {e}")
        logger.error(f"视频处理错误: {e}")


def render_step_by_step_tab():
    """渲染分步处理选项卡"""
    st.header("🔍 分步处理")
    
    step_tabs = st.tabs(["📤 上传视频", "🔍 视频分析", "📝 解说生成", "🎙️ 语音合成", "🎬 视频制作"])
    
    with step_tabs[0]:
        render_upload_step()
    
    with step_tabs[1]:
        render_analysis_step()
    
    with step_tabs[2]:
        render_narration_step()
    
    with step_tabs[3]:
        render_tts_step()
    
    with step_tabs[4]:
        render_video_generation_step()


def render_upload_step():
    """渲染上传步骤"""
    st.subheader("📤 视频上传")
    
    uploaded_file = st.file_uploader(
        "选择视频文件",
        type=['mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv'],
        key="step_upload"
    )
    
    if uploaded_file:
        st.write(f"文件名: {uploaded_file.name}")
        st.write(f"文件大小: {uploaded_file.size / 1024 / 1024:.2f} MB")
        
        if st.button("上传文件"):
            with st.spinner("上传中..."):
                files = {"file": uploaded_file.getvalue()}
                response = requests.post(f"{API_BASE_URL}/upload/video", files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"上传成功! 文件路径: {result['file_path']}")
                    st.session_state.uploaded_video_path = result['file_path']
                else:
                    st.error(f"上传失败: {response.text}")


def render_analysis_step():
    """渲染分析步骤"""
    st.subheader("🔍 视频分析")
    
    if 'uploaded_video_path' not in st.session_state:
        st.warning("请先上传视频文件")
        return
    
    video_path = st.session_state.uploaded_video_path
    st.write(f"分析视频: {video_path}")
    
    if st.button("开始分析"):
        with st.spinner("分析中..."):
            data = {"video_path": video_path}
            response = requests.post(f"{API_BASE_URL}/analyze/video", json=data)
            
            if response.status_code == 200:
                result = response.json()
                st.success("分析完成!")
                st.session_state.video_analysis = result
                
                # 显示分析结果
                with st.expander("分析结果"):
                    st.json(result)
            else:
                st.error(f"分析失败: {response.text}")


def render_narration_step():
    """渲染解说生成步骤"""
    st.subheader("📝 解说生成")
    
    if 'video_analysis' not in st.session_state:
        st.warning("请先完成视频分析")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        style = st.selectbox("解说风格", ["professional", "humorous", "emotional", "suspenseful"])
        target_audience = st.selectbox("目标观众", ["general", "young", "professional", "children"])
    
    with col2:
        narration_length = st.selectbox("解说长度", ["short", "medium", "detailed"])
    
    if st.button("生成解说"):
        with st.spinner("生成中..."):
            data = {
                "video_analysis": st.session_state.video_analysis,
                "style": style,
                "target_audience": target_audience,
                "narration_length": narration_length
            }
            response = requests.post(f"{API_BASE_URL}/narration/generate", json=data)
            
            if response.status_code == 200:
                result = response.json()
                st.success("解说生成完成!")
                st.session_state.narration_result = result
                
                # 显示解说内容
                for i, segment in enumerate(result["segments"]):
                    st.write(f"**段落 {i+1}** ({segment['start_time']:.1f}s - {segment['end_time']:.1f}s)")
                    st.write(segment["text"])
                    st.write("---")
            else:
                st.error(f"解说生成失败: {response.text}")


def render_tts_step():
    """渲染语音合成步骤"""
    st.subheader("🎙️ 语音合成")
    
    if 'narration_result' not in st.session_state:
        st.warning("请先完成解说生成")
        return
    
    # 语音参数配置
    col1, col2 = st.columns(2)
    
    with col1:
        # 获取可用语音
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
        speed = st.slider("语速", 0.5, 2.0, 1.0, 0.1)
    
    with col2:
        pitch = st.slider("音调", 0.5, 2.0, 1.0, 0.1)
        volume = st.slider("音量", 0.5, 2.0, 1.0, 0.1)
    
    if st.button("开始合成"):
        with st.spinner("合成中..."):
            data = {
                "segments": st.session_state.narration_result["segments"],
                "voice_style": selected_voice,
                "speed": speed,
                "pitch": pitch,
                "volume": volume
            }
            response = requests.post(f"{API_BASE_URL}/tts/batch", json=data)
            
            if response.status_code == 200:
                result = response.json()
                st.success("语音合成完成!")
                st.session_state.tts_result = result
                
                # 显示音频文件列表
                st.write("生成的音频文件:")
                for audio_file in result["audio_files"]:
                    st.write(f"• {audio_file}")
            else:
                st.error(f"语音合成失败: {response.text}")


def render_video_generation_step():
    """渲染视频生成步骤"""
    st.subheader("🎬 视频制作")
    
    if 'tts_result' not in st.session_state:
        st.warning("请先完成语音合成")
        return
    
    if st.button("生成最终视频"):
        with st.spinner("生成中..."):
            data = {
                "original_video": st.session_state.uploaded_video_path,
                "narration_segments": st.session_state.narration_result["segments"],
                "audio_files": st.session_state.tts_result["audio_files"]
            }
            response = requests.post(f"{API_BASE_URL}/video/generate", json=data)
            
            if response.status_code == 200:
                result = response.json()
                st.success("视频生成完成!")
                
                # 下载链接
                if "output_video" in result:
                    download_url = f"{API_BASE_URL}/files/download/video/{result['output_video']}"
                    st.markdown(f"[📥 下载解说视频]({download_url})")
                
                st.write(f"处理时长: {result.get('processing_time', '未知')}")
                st.write(f"实际成本: ¥{result.get('actual_cost', 0):.4f}")
            else:
                st.error(f"视频生成失败: {response.text}")


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