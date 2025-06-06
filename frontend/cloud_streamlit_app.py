import streamlit as st
import requests
import time
import json
from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from src.config.cloud_settings import settings

# 页面配置
st.set_page_config(
    page_title="AIMovie Cloud - AI视频解说生成器",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API基础URL
API_BASE_URL = settings.API_BASE_URL

def check_api_health():
    """检查API服务状态"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except:
        return False, None

def upload_video(video_file):
    """上传视频文件"""
    try:
        files = {"file": (video_file.name, video_file.getvalue(), video_file.type)}
        response = requests.post(f"{API_BASE_URL}/upload/video", files=files)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"视频上传失败: {e}")
        return None

def get_task_status(task_id):
    """获取任务状态"""
    try:
        response = requests.get(f"{API_BASE_URL}/task/{task_id}")
        response.raise_for_status()
        return response.json()
    except:
        return None

def wait_for_task(task_id, progress_bar=None, status_text=None):
    """等待任务完成"""
    while True:
        status = get_task_status(task_id)
        if not status:
            break
        
        if progress_bar:
            progress_bar.progress(status.get("progress", 0))
        
        if status_text:
            status_text.text(status.get("message", "处理中..."))
        
        if status.get("status") in ["completed", "failed"]:
            return status
        
        time.sleep(1)
    
    return None

def estimate_cost(text_length, audio_length, frame_count):
    """估算处理成本"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/cost/estimate",
            params={
                "text_length": text_length,
                "audio_length": audio_length,
                "frame_count": frame_count
            }
        )
        response.raise_for_status()
        return response.json()
    except:
        return None

def main():
    # 标题和描述
    st.title("🎬 AIMovie Cloud - AI视频解说生成器")
    st.markdown("### 🌐 云端版 - 高性价比AI服务组合")
    
    # 检查API服务状态
    api_healthy, health_info = check_api_health()
    
    if not api_healthy:
        st.error("⚠️ API服务未启动或无法连接")
        st.markdown("""
        请确保API服务正在运行:
        ```bash
        python -m src.api.cloud_main
        ```
        """)
        return
    
    # 显示服务状态
    with st.sidebar:
        st.header("🔧 服务状态")
        
        if health_info:
            config = health_info.get("config", {})
            services = config.get("services", {})
            
            # LLM服务
            st.subheader("📝 解说生成")
            llm_services = services.get("llm", [])
            if llm_services:
                for service in llm_services:
                    st.success(f"✅ {service['display_name']}")
            else:
                st.warning("⚠️ 未配置LLM服务")
            
            # TTS服务
            st.subheader("🎤 语音合成")
            tts_services = services.get("tts", [])
            if tts_services:
                for service in tts_services:
                    st.success(f"✅ {service['display_name']}")
            else:
                st.warning("⚠️ 未配置TTS服务")
            
            # 视频分析服务
            st.subheader("🔍 视频分析")
            video_services = services.get("video", [])
            if video_services:
                for service in video_services:
                    st.success(f"✅ {service['display_name']}")
            else:
                st.warning("⚠️ 未配置视频分析服务")
            
            # 配置警告
            if health_info.get("warnings"):
                st.subheader("⚠️ 配置警告")
                for warning in health_info["warnings"]:
                    st.warning(warning)
        
        # 成本估算
        st.header("💰 成本估算")
        with st.expander("估算处理成本"):
            text_len = st.number_input("解说字数", min_value=100, max_value=2000, value=500)
            audio_len = st.number_input("音频字数", min_value=100, max_value=2000, value=500)
            frame_count = st.number_input("分析帧数", min_value=10, max_value=100, value=50)
            
            if st.button("估算成本"):
                cost_info = estimate_cost(text_len, audio_len, frame_count)
                if cost_info:
                    st.success(f"预估成本: ¥{cost_info['estimated_cost']}")
                    st.caption("实际费用可能因API调用情况而有所不同")
    
    # 主界面选项卡
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎬 完整流程", 
        "🔍 视频分析", 
        "📝 解说生成", 
        "🎤 语音合成", 
        "📁 文件管理"
    ])
    
    # ==========================================
    # 完整流程
    # ==========================================
    with tab1:
        st.header("🎬 一键生成解说视频")
        st.markdown("上传视频，自动完成分析、解说生成、语音合成和视频制作的完整流程")
        
        # 视频上传
        video_file = st.file_uploader(
            "选择视频文件",
            type=['mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv'],
            help="支持常见视频格式，最大500MB"
        )
        
        if video_file:
            # 显示视频信息
            st.video(video_file)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("解说设置")
                style = st.selectbox(
                    "解说风格",
                    ["professional", "humorous", "emotional", "suspenseful"],
                    format_func=lambda x: {
                        "professional": "专业严肃",
                        "humorous": "幽默风趣", 
                        "emotional": "情感丰富",
                        "suspenseful": "悬疑紧张"
                    }[x]
                )
                
                target_audience = st.selectbox(
                    "目标观众",
                    ["general", "young", "professional", "children"],
                    format_func=lambda x: {
                        "general": "普通大众",
                        "young": "年轻观众",
                        "professional": "专业人士", 
                        "children": "儿童观众"
                    }[x]
                )
                
                narration_length = st.selectbox(
                    "解说长度",
                    ["short", "medium", "long"],
                    index=1,
                    format_func=lambda x: {
                        "short": "简短",
                        "medium": "中等",
                        "long": "详细"
                    }[x]
                )
            
            with col2:
                st.subheader("语音设置")
                
                # 获取可用语音
                try:
                    response = requests.get(f"{API_BASE_URL}/tts/voices")
                    voices_data = response.json()
                    
                    voice_options = []
                    voice_mapping = {}
                    
                    for gender, voices in voices_data.items():
                        for voice in voices:
                            display_name = f"{voice['name']} ({gender})"
                            voice_options.append(display_name)
                            voice_mapping[display_name] = voice['id']
                    
                    selected_voice_display = st.selectbox("语音风格", voice_options)
                    voice_style = voice_mapping[selected_voice_display]
                    
                except:
                    voice_style = st.selectbox(
                        "语音风格",
                        ["female_gentle", "female_lively", "female_intellectual", 
                         "male_steady", "male_young", "male_magnetic"],
                        format_func=lambda x: {
                            "female_gentle": "温柔女声",
                            "female_lively": "活泼女声",
                            "female_intellectual": "知性女声",
                            "male_steady": "沉稳男声",
                            "male_young": "年轻男声",
                            "male_magnetic": "磁性男声"
                        }[x]
                    )
                
                speed = st.slider("语速", 0.5, 2.0, 1.0, 0.1)
                pitch = st.slider("音调", 0.5, 2.0, 1.0, 0.1)
                volume = st.slider("音量", 0.5, 2.0, 1.0, 0.1)
            
            # 开始处理
            if st.button("🚀 开始完整处理", type="primary"):
                with st.spinner("正在处理..."):
                    try:
                        # 准备表单数据
                        files = {"video_file": (video_file.name, video_file.getvalue(), video_file.type)}
                        data = {
                            "style": style,
                            "target_audience": target_audience,
                            "narration_length": narration_length,
                            "voice_style": voice_style,
                            "speed": speed,
                            "pitch": pitch,
                            "volume": volume
                        }
                        
                        # 提交完整处理任务
                        response = requests.post(
                            f"{API_BASE_URL}/process/complete",
                            files=files,
                            data=data
                        )
                        response.raise_for_status()
                        task_info = response.json()
                        task_id = task_info["task_id"]
                        
                        st.success(f"任务已启动: {task_id}")
                        
                        # 显示进度
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # 等待任务完成
                        final_status = wait_for_task(task_id, progress_bar, status_text)
                        
                        if final_status and final_status.get("status") == "completed":
                            st.success("🎉 处理完成!")
                            
                            result = final_status.get("result", {})
                            
                            # 显示结果
                            if "final_video" in result:
                                st.subheader("📹 生成的解说视频")
                                video_url = f"{API_BASE_URL}/files/download/output/{Path(result['final_video']).name}"
                                st.markdown(f"[下载视频]({video_url})")
                            
                            # 显示详细信息
                            with st.expander("查看详细结果"):
                                st.json(result)
                        
                        elif final_status and final_status.get("status") == "failed":
                            st.error(f"处理失败: {final_status.get('error', '未知错误')}")
                        
                        else:
                            st.error("任务状态异常")
                    
                    except Exception as e:
                        st.error(f"处理失败: {e}")
    
    # ==========================================
    # 视频分析
    # ==========================================
    with tab2:
        st.header("🔍 视频内容分析")
        
        # 文件选择
        uploaded_file = st.file_uploader(
            "上传视频进行分析",
            type=['mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv'],
            key="analysis_upload"
        )
        
        if uploaded_file:
            # 上传文件
            upload_result = upload_video(uploaded_file)
            if upload_result:
                video_path = upload_result["file_path"]
                
                if st.button("开始分析"):
                    try:
                        # 提交分析任务
                        response = requests.post(
                            f"{API_BASE_URL}/analyze/video",
                            json={"video_path": video_path}
                        )
                        response.raise_for_status()
                        task_info = response.json()
                        task_id = task_info["task_id"]
                        
                        # 显示进度
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # 等待分析完成
                        final_status = wait_for_task(task_id, progress_bar, status_text)
                        
                        if final_status and final_status.get("status") == "completed":
                            st.success("分析完成!")
                            
                            result = final_status.get("result", {})
                            
                            # 显示分析结果
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.subheader("📊 视频信息")
                                video_info = result.get("video_info", {})
                                st.write(f"时长: {video_info.get('duration', 0):.1f}秒")
                                st.write(f"分辨率: {video_info.get('resolution', [0, 0])[0]}x{video_info.get('resolution', [0, 0])[1]}")
                                st.write(f"帧率: {video_info.get('fps', 0):.1f}")
                                
                                audio_info = result.get("audio_analysis", {})
                                st.write(f"音频: {'有' if audio_info.get('has_audio') else '无'}")
                            
                            with col2:
                                st.subheader("🎯 分析摘要")
                                summary = result.get("summary", {})
                                st.write(f"分析帧数: {summary.get('total_frames_analyzed', 0)}")
                                
                                scene_types = summary.get("scene_types", {})
                                if scene_types:
                                    st.write("场景类型:")
                                    for scene, count in scene_types.items():
                                        st.write(f"  - {scene}: {count}帧")
                            
                            # 关键时刻
                            key_moments = summary.get("key_moments", [])
                            if key_moments:
                                st.subheader("⭐ 关键时刻")
                                for i, moment in enumerate(key_moments[:5], 1):
                                    timestamp = moment["timestamp"]
                                    description = moment["description"]
                                    confidence = moment["confidence"]
                                    st.write(f"{i}. {timestamp:.1f}秒: {description} (置信度: {confidence:.2f})")
                            
                            # 保存分析结果到session state
                            st.session_state.video_analysis = result
                            st.session_state.video_path = video_path
                        
                        elif final_status and final_status.get("status") == "failed":
                            st.error(f"分析失败: {final_status.get('error', '未知错误')}")
                    
                    except Exception as e:
                        st.error(f"分析失败: {e}")
    
    # ==========================================
    # 解说生成
    # ==========================================
    with tab3:
        st.header("📝 智能解说生成")
        
        if "video_analysis" in st.session_state:
            st.success("✅ 已有视频分析结果")
            
            col1, col2 = st.columns(2)
            
            with col1:
                style = st.selectbox(
                    "解说风格",
                    ["professional", "humorous", "emotional", "suspenseful"],
                    format_func=lambda x: {
                        "professional": "专业严肃",
                        "humorous": "幽默风趣",
                        "emotional": "情感丰富", 
                        "suspenseful": "悬疑紧张"
                    }[x],
                    key="narration_style"
                )
                
                target_audience = st.selectbox(
                    "目标观众",
                    ["general", "young", "professional", "children"],
                    format_func=lambda x: {
                        "general": "普通大众",
                        "young": "年轻观众",
                        "professional": "专业人士",
                        "children": "儿童观众"
                    }[x],
                    key="narration_audience"
                )
            
            with col2:
                narration_length = st.selectbox(
                    "解说长度",
                    ["short", "medium", "long"],
                    index=1,
                    format_func=lambda x: {
                        "short": "简短",
                        "medium": "中等",
                        "long": "详细"
                    }[x],
                    key="narration_length"
                )
            
            if st.button("生成解说"):
                try:
                    # 提交解说生成任务
                    response = requests.post(
                        f"{API_BASE_URL}/narration/generate",
                        json={
                            "video_analysis": st.session_state.video_analysis,
                            "style": style,
                            "target_audience": target_audience,
                            "narration_length": narration_length
                        }
                    )
                    response.raise_for_status()
                    task_info = response.json()
                    task_id = task_info["task_id"]
                    
                    # 显示进度
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # 等待生成完成
                    final_status = wait_for_task(task_id, progress_bar, status_text)
                    
                    if final_status and final_status.get("status") == "completed":
                        st.success("解说生成完成!")
                        
                        result = final_status.get("result", {})
                        
                        # 显示解说文本
                        st.subheader("📄 生成的解说词")
                        narration_text = result.get("narration_text", "")
                        st.text_area("解说内容", narration_text, height=300)
                        
                        # 显示段落信息
                        segments = result.get("segments", [])
                        if segments:
                            st.subheader("📋 解说段落")
                            for i, segment in enumerate(segments, 1):
                                timestamp = segment["timestamp"]
                                content = segment["content"]
                                duration = segment["duration"]
                                st.write(f"{i}. [{timestamp:.1f}s] {content} (时长: {duration}s)")
                        
                        # 保存解说结果
                        st.session_state.narration_result = result
                    
                    elif final_status and final_status.get("status") == "failed":
                        st.error(f"解说生成失败: {final_status.get('error', '未知错误')}")
                
                except Exception as e:
                    st.error(f"解说生成失败: {e}")
        
        else:
            st.warning("⚠️ 请先在'视频分析'选项卡中分析视频")
    
    # ==========================================
    # 语音合成
    # ==========================================
    with tab4:
        st.header("🎤 语音合成")
        
        # 语音测试
        st.subheader("🔊 语音测试")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 获取可用语音
            try:
                response = requests.get(f"{API_BASE_URL}/tts/voices")
                voices_data = response.json()
                
                voice_options = []
                voice_mapping = {}
                
                for gender, voices in voices_data.items():
                    for voice in voices:
                        display_name = f"{voice['name']} ({gender})"
                        voice_options.append(display_name)
                        voice_mapping[display_name] = voice['id']
                
                selected_voice_display = st.selectbox("选择语音", voice_options, key="test_voice")
                test_voice_style = voice_mapping[selected_voice_display]
                
            except:
                test_voice_style = st.selectbox(
                    "选择语音",
                    ["female_gentle", "female_lively", "female_intellectual",
                     "male_steady", "male_young", "male_magnetic"],
                    format_func=lambda x: {
                        "female_gentle": "温柔女声",
                        "female_lively": "活泼女声", 
                        "female_intellectual": "知性女声",
                        "male_steady": "沉稳男声",
                        "male_young": "年轻男声",
                        "male_magnetic": "磁性男声"
                    }[x],
                    key="test_voice"
                )
            
            test_text = st.text_area(
                "测试文本",
                "这是一段测试语音，用来试听不同的声音效果。",
                key="test_text"
            )
        
        with col2:
            test_speed = st.slider("语速", 0.5, 2.0, 1.0, 0.1, key="test_speed")
            test_pitch = st.slider("音调", 0.5, 2.0, 1.0, 0.1, key="test_pitch")
            test_volume = st.slider("音量", 0.5, 2.0, 1.0, 0.1, key="test_volume")
        
        if st.button("🎵 试听语音"):
            try:
                # 提交测试请求
                data = {
                    "voice_style": test_voice_style,
                    "test_text": test_text,
                    "speed": test_speed,
                    "pitch": test_pitch,
                    "volume": test_volume
                }
                
                response = requests.post(f"{API_BASE_URL}/tts/test", data=data)
                response.raise_for_status()
                
                # 播放音频
                st.audio(response.content, format="audio/wav")
                st.success("语音测试完成!")
            
            except Exception as e:
                st.error(f"语音测试失败: {e}")
        
        # 批量合成
        if "narration_result" in st.session_state:
            st.subheader("🎼 批量语音合成")
            st.success("✅ 已有解说文本")
            
            col1, col2 = st.columns(2)
            
            with col1:
                batch_voice_style = st.selectbox(
                    "语音风格",
                    ["female_gentle", "female_lively", "female_intellectual",
                     "male_steady", "male_young", "male_magnetic"],
                    format_func=lambda x: {
                        "female_gentle": "温柔女声",
                        "female_lively": "活泼女声",
                        "female_intellectual": "知性女声", 
                        "male_steady": "沉稳男声",
                        "male_young": "年轻男声",
                        "male_magnetic": "磁性男声"
                    }[x],
                    key="batch_voice"
                )
            
            with col2:
                batch_speed = st.slider("语速", 0.5, 2.0, 1.0, 0.1, key="batch_speed")
                batch_pitch = st.slider("音调", 0.5, 2.0, 1.0, 0.1, key="batch_pitch")
                batch_volume = st.slider("音量", 0.5, 2.0, 1.0, 0.1, key="batch_volume")
            
            if st.button("🎵 批量合成语音"):
                try:
                    # 提交批量合成任务
                    response = requests.post(
                        f"{API_BASE_URL}/tts/batch",
                        json={
                            "segments": st.session_state.narration_result["segments"],
                            "voice_style": batch_voice_style,
                            "speed": batch_speed,
                            "pitch": batch_pitch,
                            "volume": batch_volume
                        }
                    )
                    response.raise_for_status()
                    task_info = response.json()
                    task_id = task_info["task_id"]
                    
                    # 显示进度
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # 等待合成完成
                    final_status = wait_for_task(task_id, progress_bar, status_text)
                    
                    if final_status and final_status.get("status") == "completed":
                        st.success("批量语音合成完成!")
                        
                        result = final_status.get("result", {})
                        synthesized_segments = result.get("segments", [])
                        
                        # 显示合成结果
                        st.subheader("🎵 合成的语音段落")
                        for i, segment in enumerate(synthesized_segments, 1):
                            timestamp = segment["timestamp"]
                            content = segment["content"]
                            audio_path = segment.get("audio_path", "")
                            
                            st.write(f"{i}. [{timestamp:.1f}s] {content}")
                            
                            if audio_path:
                                # 播放音频
                                try:
                                    audio_url = f"{API_BASE_URL}/files/download/temp/{Path(audio_path).name}"
                                    st.audio(audio_url)
                                except:
                                    st.caption("音频文件不可用")
                        
                        # 保存合成结果
                        st.session_state.synthesized_segments = synthesized_segments
                    
                    elif final_status and final_status.get("status") == "failed":
                        st.error(f"批量合成失败: {final_status.get('error', '未知错误')}")
                
                except Exception as e:
                    st.error(f"批量合成失败: {e}")
        
        else:
            st.info("💡 请先在'解说生成'选项卡中生成解说词")
    
    # ==========================================
    # 文件管理
    # ==========================================
    with tab5:
        st.header("📁 文件管理")
        
        # 文件列表
        try:
            response = requests.get(f"{API_BASE_URL}/files/list")
            response.raise_for_status()
            files_data = response.json()
            files = files_data.get("files", [])
            
            if files:
                # 按类型分组显示
                input_files = [f for f in files if f["type"] == "input"]
                output_files = [f for f in files if f["type"] == "output"]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📥 输入文件")
                    for file in input_files:
                        st.write(f"📄 {file['name']}")
                        st.caption(f"大小: {file['size'] / (1024*1024):.1f}MB")
                        download_url = f"{API_BASE_URL}/files/download/input/{file['name']}"
                        st.markdown(f"[下载]({download_url})")
                        st.divider()
                
                with col2:
                    st.subheader("📤 输出文件")
                    for file in output_files:
                        st.write(f"📄 {file['name']}")
                        st.caption(f"大小: {file['size'] / (1024*1024):.1f}MB")
                        download_url = f"{API_BASE_URL}/files/download/output/{file['name']}"
                        st.markdown(f"[下载]({download_url})")
                        st.divider()
            
            else:
                st.info("📂 暂无文件")
        
        except Exception as e:
            st.error(f"获取文件列表失败: {e}")
        
        # 清理临时文件
        st.subheader("🧹 文件清理")
        if st.button("清理临时文件"):
            try:
                response = requests.delete(f"{API_BASE_URL}/files/cleanup")
                response.raise_for_status()
                result = response.json()
                st.success(result["message"])
            except Exception as e:
                st.error(f"清理失败: {e}")

if __name__ == "__main__":
    main() 