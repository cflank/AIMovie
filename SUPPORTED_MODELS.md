# 🤖 支持的大模型服务

## 📋 概述

AIMovie Cloud 支持多种云端AI服务，用户可以根据需求选择不同的服务组合。我们提供三种预设方案，也支持自定义配置。

## 🎯 预设方案对比

| 方案 | 成本 | 质量 | 适用场景 | 推荐指数 |
|------|------|------|----------|----------|
| 🏆 最高性价比 | ⭐⭐⭐ | ⭐⭐⭐⭐ | 大多数用户 | ⭐⭐⭐⭐⭐ |
| 💎 质量最高 | ⭐ | ⭐⭐⭐⭐⭐ | 专业用户 | ⭐⭐⭐⭐ |
| 💰 最经济 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 预算有限 | ⭐⭐⭐ |

## 🤖 LLM服务 (解说生成)

### 🏆 推荐服务

#### 通义千问 (阿里云)
- **价格**: ¥0.0008/1K tokens
- **优势**: 性价比最高，中文优化好
- **模型**: qwen-turbo, qwen-plus, qwen-max
- **申请**: [https://dashscope.aliyuncs.com/](https://dashscope.aliyuncs.com/)
- **配置**:
  ```env
  QWEN_API_KEY=your_qwen_api_key
  QWEN_MODEL=qwen-plus
  ```

#### 文心一言 (百度)
- **价格**: ¥0.008/1K tokens
- **优势**: 中文理解强，免费额度大
- **模型**: ernie-lite-8k, ernie-3.5-8k, ernie-4.0-8k
- **申请**: [https://cloud.baidu.com/product/wenxinworkshop](https://cloud.baidu.com/product/wenxinworkshop)
- **配置**:
  ```env
  ERNIE_API_KEY=your_ernie_api_key
  ERNIE_SECRET_KEY=your_ernie_secret_key
  ERNIE_MODEL=ernie-3.5-8k
  ```

### 🌟 高端服务

#### OpenAI GPT (国际)
- **价格**: $0.002/1K tokens (约¥0.014)
- **优势**: 质量标杆，多语言支持
- **模型**: gpt-3.5-turbo, gpt-4, gpt-4-turbo
- **申请**: [https://platform.openai.com/](https://platform.openai.com/)
- **配置**:
  ```env
  OPENAI_API_KEY=your_openai_api_key
  OPENAI_BASE_URL=https://api.openai.com/v1
  OPENAI_MODEL=gpt-4
  ```

#### Claude (Anthropic)
- **价格**: $0.003/1K tokens (约¥0.021)
- **优势**: 安全性高，长文本处理好
- **模型**: claude-3-haiku, claude-3-sonnet, claude-3-opus
- **申请**: [https://console.anthropic.com/](https://console.anthropic.com/)
- **配置**:
  ```env
  CLAUDE_API_KEY=your_claude_api_key
  CLAUDE_MODEL=claude-3-opus-20240229
  ```

### 🇨🇳 国产服务

#### 智谱AI (清华)
- **价格**: ¥0.005/1K tokens
- **优势**: 国产自主，技术先进
- **模型**: glm-3-turbo, glm-4
- **申请**: [https://open.bigmodel.cn/](https://open.bigmodel.cn/)
- **配置**:
  ```env
  ZHIPU_API_KEY=your_zhipu_api_key
  ZHIPU_MODEL=glm-4
  ```

#### 月之暗面 (Kimi)
- **价格**: ¥0.012/1K tokens
- **优势**: 长文本处理，上下文理解强
- **模型**: moonshot-v1-8k, moonshot-v1-32k, moonshot-v1-128k
- **申请**: [https://platform.moonshot.cn/](https://platform.moonshot.cn/)
- **配置**:
  ```env
  MOONSHOT_API_KEY=your_moonshot_api_key
  MOONSHOT_MODEL=moonshot-v1-32k
  ```

## 🎙️ TTS服务 (语音合成)

### 🏆 推荐服务

#### 阿里云TTS
- **价格**: ¥0.00002/字符
- **优势**: 性价比最高，音质好
- **语音**: xiaoyun, xiaogang, xiaomeng等
- **申请**: [https://nls.console.aliyun.com/](https://nls.console.aliyun.com/)
- **配置**:
  ```env
  ALIYUN_ACCESS_KEY_ID=your_access_key_id
  ALIYUN_ACCESS_KEY_SECRET=your_access_key_secret
  ALIYUN_TTS_REGION=cn-shanghai
  ALIYUN_TTS_VOICE=xiaoyun
  ```

#### Edge-TTS (微软)
- **价格**: 完全免费
- **优势**: 无需配置，音质不错
- **语音**: zh-CN-XiaoxiaoNeural, zh-CN-YunxiNeural等
- **申请**: 无需申请
- **配置**:
  ```env
  EDGE_TTS_VOICE=zh-CN-XiaoxiaoNeural
  ```

### 🌟 高端服务

#### Azure TTS (微软)
- **价格**: $0.016/1K字符 (约¥0.11)
- **优势**: 音质最佳，语音最自然
- **语音**: zh-CN-XiaoxiaoNeural, zh-CN-YunyangNeural等
- **申请**: [https://azure.microsoft.com/cognitive-services/](https://azure.microsoft.com/cognitive-services/)
- **配置**:
  ```env
  AZURE_TTS_KEY=your_azure_tts_key
  AZURE_TTS_REGION=eastus
  AZURE_TTS_VOICE=zh-CN-XiaoxiaoNeural
  ```

#### 腾讯云TTS
- **价格**: ¥0.00015/字符
- **优势**: 质量稳定，语音丰富
- **语音**: 101001(女声), 101002(男声)等
- **申请**: [https://console.cloud.tencent.com/](https://console.cloud.tencent.com/)
- **配置**:
  ```env
  TENCENT_SECRET_ID=your_secret_id
  TENCENT_SECRET_KEY=your_secret_key
  TENCENT_TTS_REGION=ap-beijing
  TENCENT_TTS_VOICE=101001
  ```

### 💰 经济服务

#### 百度TTS
- **价格**: 免费5万字符/月
- **优势**: 免费额度大
- **语音**: 0(女声), 1(男声), 3(情感女声), 4(情感男声)
- **申请**: [https://ai.baidu.com/](https://ai.baidu.com/)
- **配置**:
  ```env
  BAIDU_TTS_API_KEY=your_baidu_tts_api_key
  BAIDU_TTS_SECRET_KEY=your_baidu_tts_secret_key
  BAIDU_TTS_VOICE=0
  ```

## 👁️ 视觉服务 (视频分析)

### 🏆 推荐服务

#### 百度AI
- **价格**: ¥0.002/图片
- **优势**: 识别准确，免费额度大
- **功能**: 场景识别、物体检测、人脸识别
- **申请**: [https://ai.baidu.com/](https://ai.baidu.com/)
- **配置**:
  ```env
  BAIDU_API_KEY=your_baidu_api_key
  BAIDU_SECRET_KEY=your_baidu_secret_key
  ```

#### 通义千问-VL (阿里云)
- **价格**: ¥0.008/图片
- **优势**: 多模态理解，中文优化
- **功能**: 图像理解、场景描述、内容分析
- **申请**: [https://dashscope.aliyuncs.com/](https://dashscope.aliyuncs.com/)
- **配置**:
  ```env
  QWEN_VL_API_KEY=your_qwen_vl_api_key
  QWEN_VL_MODEL=qwen-vl-plus
  ```

### 🌟 高端服务

#### GPT-4V (OpenAI)
- **价格**: $0.01/图片 (约¥0.07)
- **优势**: 视觉理解最强，描述详细
- **功能**: 图像理解、场景分析、内容描述
- **申请**: [https://platform.openai.com/](https://platform.openai.com/)
- **配置**:
  ```env
  OPENAI_VISION_API_KEY=your_openai_vision_api_key
  OPENAI_VISION_MODEL=gpt-4-vision-preview
  ```

### 🇨🇳 其他服务

#### 腾讯云视觉AI
- **价格**: ¥0.0015/图片
- **优势**: 服务稳定，功能丰富
- **功能**: 图像识别、内容审核、场景分析
- **申请**: [https://console.cloud.tencent.com/](https://console.cloud.tencent.com/)
- **配置**:
  ```env
  TENCENT_VISION_SECRET_ID=your_vision_secret_id
  TENCENT_VISION_SECRET_KEY=your_vision_secret_key
  ```

#### 阿里云视觉智能
- **价格**: ¥0.003/图片
- **优势**: 功能全面，技术成熟
- **功能**: 图像识别、视频分析、内容理解
- **申请**: [https://vision.console.aliyun.com/](https://vision.console.aliyun.com/)
- **配置**:
  ```env
  ALIYUN_VISION_ACCESS_KEY_ID=your_vision_access_key_id
  ALIYUN_VISION_ACCESS_KEY_SECRET=your_vision_access_key_secret
  ```

## 🎯 选择建议

### 🏆 最高性价比组合
**适合**: 大多数用户，平衡质量与成本
```env
PRESET_CONFIG=cost_effective
QWEN_API_KEY=your_qwen_api_key
ALIYUN_ACCESS_KEY_ID=your_aliyun_access_key_id
ALIYUN_ACCESS_KEY_SECRET=your_aliyun_access_key_secret
BAIDU_API_KEY=your_baidu_api_key
BAIDU_SECRET_KEY=your_baidu_secret_key
```

### 💎 质量最高组合
**适合**: 专业用户，追求最佳效果
```env
PRESET_CONFIG=premium
OPENAI_API_KEY=your_openai_api_key
AZURE_TTS_KEY=your_azure_tts_key
AZURE_TTS_REGION=eastus
OPENAI_VISION_API_KEY=your_openai_vision_api_key
```

### 💰 最经济组合
**适合**: 预算有限，大批量处理
```env
PRESET_CONFIG=budget
ERNIE_API_KEY=your_ernie_api_key
ERNIE_SECRET_KEY=your_ernie_secret_key
BAIDU_API_KEY=your_baidu_api_key
BAIDU_SECRET_KEY=your_baidu_secret_key
# Edge-TTS 无需配置
```

## 🔧 自定义配置

### 混合方案
您也可以混合使用不同服务商的服务：

```env
# 使用通义千问 + Azure TTS + 百度AI
QWEN_API_KEY=your_qwen_api_key
AZURE_TTS_KEY=your_azure_tts_key
AZURE_TTS_REGION=eastus
BAIDU_API_KEY=your_baidu_api_key
BAIDU_SECRET_KEY=your_baidu_secret_key
```

### 多服务备用
配置多个服务作为备用，系统会自动故障转移：

```env
# 主力 + 备用
QWEN_API_KEY=your_qwen_api_key
ERNIE_API_KEY=your_ernie_api_key
ERNIE_SECRET_KEY=your_ernie_secret_key

ALIYUN_ACCESS_KEY_ID=your_aliyun_access_key_id
ALIYUN_ACCESS_KEY_SECRET=your_aliyun_access_key_secret
# Edge-TTS 作为备用，无需配置

BAIDU_API_KEY=your_baidu_api_key
BAIDU_SECRET_KEY=your_baidu_secret_key
QWEN_VL_API_KEY=your_qwen_vl_api_key
```

## 📊 性能对比

### LLM服务性能对比

| 服务 | 中文质量 | 响应速度 | 成本 | 稳定性 | 推荐指数 |
|------|----------|----------|------|--------|----------|
| 通义千问 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 文心一言 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| GPT-4 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Claude | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 智谱AI | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |

### TTS服务性能对比

| 服务 | 音质 | 自然度 | 成本 | 语音选择 | 推荐指数 |
|------|------|--------|------|----------|----------|
| Azure TTS | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 阿里云TTS | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Edge-TTS | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 腾讯云TTS | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| 百度TTS | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |

## 🔗 申请链接汇总

### LLM服务
- [通义千问](https://dashscope.aliyuncs.com/) - 阿里云
- [文心一言](https://cloud.baidu.com/product/wenxinworkshop) - 百度
- [OpenAI](https://platform.openai.com/) - OpenAI
- [Claude](https://console.anthropic.com/) - Anthropic
- [智谱AI](https://open.bigmodel.cn/) - 清华大学
- [月之暗面](https://platform.moonshot.cn/) - Moonshot AI

### TTS服务
- [阿里云TTS](https://nls.console.aliyun.com/) - 阿里云
- [腾讯云TTS](https://console.cloud.tencent.com/) - 腾讯云
- [Azure TTS](https://azure.microsoft.com/cognitive-services/) - 微软
- [百度TTS](https://ai.baidu.com/) - 百度

### 视觉服务
- [百度AI](https://ai.baidu.com/) - 百度
- [通义千问-VL](https://dashscope.aliyuncs.com/) - 阿里云
- [OpenAI Vision](https://platform.openai.com/) - OpenAI
- [腾讯云视觉](https://console.cloud.tencent.com/) - 腾讯云
- [阿里云视觉](https://vision.console.aliyun.com/) - 阿里云

## 💡 使用建议

### 新手用户
1. 选择"最高性价比组合"
2. 先申请通义千问、阿里云TTS、百度AI
3. 配置完成后测试基本功能
4. 根据使用情况调整配置

### 专业用户
1. 选择"质量最高组合"
2. 申请OpenAI、Azure TTS、GPT-4V
3. 配置多个备用服务
4. 根据项目需求选择最佳服务

### 预算有限用户
1. 选择"最经济组合"
2. 优先使用免费服务 (Edge-TTS, 百度免费额度)
3. 合理控制API调用频率
4. 批量处理降低成本

---

**💡 提示**: 所有服务都支持自动故障转移，建议配置多个服务作为备用，确保系统稳定运行。 