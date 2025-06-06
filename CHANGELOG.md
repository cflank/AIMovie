# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial cloud-based architecture
- Support for multiple cloud AI services
- Web-based user interface with Streamlit
- RESTful API with FastAPI
- Docker containerization
- GitHub Actions CI/CD pipeline

### Changed
- Migrated from GPU-based processing to cloud APIs
- Simplified deployment process
- Improved cost transparency and control

### Removed
- GPU dependencies (CUDA, PyTorch GPU support)
- Local AI model requirements
- Hardware-specific optimizations

## [1.0.0] - 2024-01-XX

### Added
- **Cloud AI Integration**
  - Qwen (通义千问) for narration generation
  - Aliyun TTS for speech synthesis
  - Baidu AI for video analysis
  - OpenAI GPT as backup option
  - Tencent Cloud TTS as backup option

- **Core Features**
  - Intelligent video content analysis
  - Automatic narration generation with multiple styles
  - Multi-voice TTS synthesis
  - Video editing and subtitle generation
  - Batch processing capabilities

- **Web Interface**
  - Streamlit-based user interface
  - Real-time progress tracking
  - File upload and download
  - Configuration management
  - Cost estimation tools

- **API Services**
  - RESTful API with FastAPI
  - OpenAPI documentation
  - Health check endpoints
  - File management endpoints
  - Task management system

- **Development Tools**
  - Docker support
  - GitHub Actions CI/CD
  - Code quality tools (Black, Flake8, MyPy)
  - Comprehensive testing framework
  - Development documentation

- **Documentation**
  - Comprehensive README
  - Detailed usage guide
  - API documentation
  - Contributing guidelines
  - Cost optimization guide

### Technical Details
- **Languages**: Python 3.8+
- **Frameworks**: FastAPI, Streamlit
- **Cloud Services**: Alibaba Cloud, Baidu AI, Tencent Cloud, OpenAI
- **Deployment**: Docker, Docker Compose
- **Testing**: Pytest
- **CI/CD**: GitHub Actions

### Cost Optimization
- Pay-per-use pricing model
- Multiple service provider options
- Configurable quality settings
- Batch processing discounts
- Free tier utilization

### Security
- API key management
- Environment variable configuration
- Secure file handling
- Input validation
- Rate limiting

---

## Release Notes

### Version 1.0.0 Highlights

This is the first major release of AIMovie Cloud, representing a complete transformation from a GPU-dependent application to a cloud-native solution. Key improvements include:

1. **Zero Hardware Requirements**: No need for expensive GPU hardware
2. **Scalable Architecture**: Handle multiple videos simultaneously
3. **Cost Transparency**: Clear pricing for all operations
4. **Easy Deployment**: One-command Docker deployment
5. **Professional Quality**: Enterprise-grade AI services

### Migration from GPU Version

Users migrating from the GPU version should note:
- All GPU-related configurations have been removed
- New cloud API keys are required
- Processing costs are now transparent and predictable
- Performance is no longer limited by local hardware

### Getting Started

```bash
# Clone the repository
git clone https://github.com/aimovie/aimovie-cloud.git
cd aimovie-cloud

# Configure environment
cp env_template.txt .env
# Edit .env with your API keys

# Start the application
python start.py
```

For detailed instructions, see [README.md](README.md) and [USAGE_GUIDE.md](USAGE_GUIDE.md). 