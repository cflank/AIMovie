"""
配置选择界面组件
让用户可以选择不同的大模型组合预设
"""

import streamlit as st
import os
import sys
from typing import Dict, Any, Optional

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.preset_configs import preset_manager, PresetType, get_cost_comparison
from src.config.cloud_settings import get_cloud_settings


def render_preset_selector() -> Optional[str]:
    """渲染预设配置选择器"""
    st.subheader("🎯 选择大模型组合方案")
    
    # 获取所有预设配置
    presets = preset_manager.list_presets()
    cost_comparison = get_cost_comparison()
    
    # 创建选项卡
    tabs = st.tabs([preset["name"] for preset in presets])
    
    selected_preset = None
    
    for i, (tab, preset) in enumerate(zip(tabs, presets)):
        with tab:
            preset_type = preset["type"]
            cost_info = cost_comparison[preset_type]
            
            # 显示预设信息
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**{preset['name']}**")
                st.write(preset["description"])
                
                # 显示服务数量
                st.write(f"📊 **服务配置**: {preset['llm_count']}个LLM + {preset['tts_count']}个TTS + {preset['vision_count']}个视觉服务")
                
                # 显示主要服务
                st.write(f"🤖 **主要LLM**: {cost_info['primary_llm']}")
                st.write(f"🎙️ **主要TTS**: {cost_info['primary_tts']}")
                st.write(f"👁️ **主要视觉**: {cost_info['primary_vision']}")
            
            with col2:
                # 成本信息
                st.metric("单视频成本", cost_info["cost_per_5min"])
                st.metric("月度成本(100视频)", cost_info["cost_per_100_videos"])
                
                # 选择按钮
                if st.button(f"选择此方案", key=f"select_{preset_type}", type="primary" if i == 0 else "secondary"):
                    selected_preset = preset_type
                    st.success(f"已选择: {preset['name']}")
    
    return selected_preset


def render_service_status():
    """渲染服务状态"""
    st.subheader("🔧 服务状态检查")
    
    settings = get_cloud_settings()
    
    # 获取当前预设信息
    preset_info = settings.get_preset_info()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("当前配置", preset_info["name"])
        st.metric("可用LLM服务", f"{preset_info['available_llm']}/{preset_info['llm_services']}")
    
    with col2:
        st.metric("预估成本", preset_info["estimated_cost"])
        st.metric("可用TTS服务", f"{preset_info['available_tts']}/{preset_info['tts_services']}")
    
    with col3:
        st.metric("配置状态", "✅ 正常" if preset_info['available_llm'] > 0 else "❌ 需要配置")
        st.metric("可用视觉服务", f"{preset_info['available_vision']}/{preset_info['vision_services']}")


def render_detailed_service_info():
    """渲染详细服务信息"""
    st.subheader("📋 详细服务配置")
    
    settings = get_cloud_settings()
    
    # LLM服务
    with st.expander("🤖 LLM服务 (解说生成)", expanded=False):
        llm_services = settings.get_llm_services()
        if llm_services:
            for i, service in enumerate(llm_services):
                priority_icon = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
                st.write(f"{priority_icon} **{service['name']}** - {service['cost_per_unit']}{service['unit']}")
                st.write(f"   {service['description']}")
        else:
            st.warning("没有可用的LLM服务，请检查API密钥配置")
    
    # TTS服务
    with st.expander("🎙️ TTS服务 (语音合成)", expanded=False):
        tts_services = settings.get_tts_services()
        if tts_services:
            for i, service in enumerate(tts_services):
                priority_icon = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
                cost_text = "免费" if service['cost_per_unit'] == 0 else f"{service['cost_per_unit']}{service['unit']}"
                st.write(f"{priority_icon} **{service['name']}** - {cost_text}")
                st.write(f"   {service['description']}")
        else:
            st.warning("没有可用的TTS服务")
    
    # 视觉服务
    with st.expander("👁️ 视觉服务 (视频分析)", expanded=False):
        vision_services = settings.get_vision_services()
        if vision_services:
            for i, service in enumerate(vision_services):
                priority_icon = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
                st.write(f"{priority_icon} **{service['name']}** - {service['cost_per_unit']}{service['unit']}")
                st.write(f"   {service['description']}")
        else:
            st.warning("没有可用的视觉服务，请检查API密钥配置")


def render_cost_calculator():
    """渲染成本计算器"""
    st.subheader("💰 成本计算器")
    
    settings = get_cloud_settings()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**输入参数**")
        text_length = st.slider("解说文本长度 (字符)", 100, 2000, 500, 50)
        audio_length = st.slider("语音长度 (字符)", 100, 2000, 500, 50)
        frame_count = st.slider("分析帧数", 10, 100, 50, 5)
    
    with col2:
        st.write("**成本估算**")
        cost_estimate = settings.estimate_cost(text_length, audio_length, frame_count)
        
        st.metric("总成本", f"¥{cost_estimate['total_cost']:.4f}")
        
        # 详细分解
        for service_type, cost_info in cost_estimate['breakdown'].items():
            st.write(f"• {cost_info}")
    
    # 成本限制检查
    cost_check = settings.check_cost_limits(cost_estimate['total_cost'])
    
    if not cost_check['within_limits']:
        st.error("⚠️ 成本超限")
        for block in cost_check['blocks']:
            st.error(f"• {block}")
    
    if cost_check['warnings']:
        st.warning("⚠️ 成本预警")
        for warning in cost_check['warnings']:
            st.warning(f"• {warning}")


def render_configuration_guide():
    """渲染配置指南"""
    st.subheader("📖 配置指南")
    
    # 获取当前预设
    settings = get_cloud_settings()
    preset_info = settings.get_preset_info()
    
    if preset_info['available_llm'] == 0:
        st.error("❌ 没有可用的LLM服务，请配置API密钥")
        
        st.write("**推荐配置步骤:**")
        st.write("1. 编辑项目根目录下的 `.env` 文件")
        st.write("2. 根据选择的预设配置，添加对应的API密钥")
        st.write("3. 重启应用以加载新配置")
        
        # 显示当前预设的推荐配置
        preset_config = preset_manager.get_preset(PresetType(preset_info['type']))
        
        st.write("**当前预设推荐的API密钥:**")
        for service in preset_config.llm_services:
            st.code(f"# {service.description}\n" + "\n".join([f"{key}=your_{key.lower()}" for key in service.required_keys]))
        
        st.write("**申请链接:**")
        links = {
            "通义千问": "https://dashscope.aliyuncs.com/",
            "文心一言": "https://cloud.baidu.com/product/wenxinworkshop",
            "OpenAI": "https://platform.openai.com/",
            "Claude": "https://console.anthropic.com/",
            "智谱AI": "https://open.bigmodel.cn/",
            "月之暗面": "https://platform.moonshot.cn/"
        }
        
        for service in preset_config.llm_services:
            if service.name in links:
                st.write(f"• [{service.name}]({links[service.name]})")
    else:
        st.success("✅ 配置正常，可以开始使用")


def render_preset_comparison():
    """渲染预设对比"""
    st.subheader("📊 方案对比")
    
    cost_comparison = get_cost_comparison()
    
    # 创建对比表格
    comparison_data = []
    for preset_type, info in cost_comparison.items():
        comparison_data.append({
            "方案": info["name"],
            "单视频成本": info["cost_per_5min"],
            "月度成本(100视频)": info["cost_per_100_videos"],
            "主要LLM": info["primary_llm"],
            "主要TTS": info["primary_tts"],
            "主要视觉": info["primary_vision"]
        })
    
    st.table(comparison_data)
    
    # 推荐说明
    st.write("**选择建议:**")
    st.write("• 🏆 **最高性价比**: 适合大多数用户，平衡质量与成本")
    st.write("• 💎 **质量最高**: 适合对质量要求极高的专业用户")
    st.write("• 💰 **最经济**: 适合预算有限或大批量处理的用户")


def main():
    """主函数 - 用于测试"""
    st.set_page_config(
        page_title="AIMovie Cloud - 配置选择",
        page_icon="🎬",
        layout="wide"
    )
    
    st.title("🎬 AIMovie Cloud - 配置选择")
    
    # 渲染各个组件
    selected_preset = render_preset_selector()
    
    if selected_preset:
        st.write(f"您选择了: {selected_preset}")
    
    st.divider()
    render_service_status()
    
    st.divider()
    render_detailed_service_info()
    
    st.divider()
    render_cost_calculator()
    
    st.divider()
    render_configuration_guide()
    
    st.divider()
    render_preset_comparison()


if __name__ == "__main__":
    main() 