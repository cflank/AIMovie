"""
Basic tests for AIMovie Cloud
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_imports():
    """Test that basic imports work"""
    try:
        from config.cloud_settings import CloudSettings
        from agents.cloud_video_analysis_agent import CloudVideoAnalysisAgent
        from agents.cloud_narration_agent import CloudNarrationAgent
        from agents.cloud_tts_agent import CloudTTSAgent
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")


def test_cloud_settings():
    """Test CloudSettings configuration"""
    from config.cloud_settings import CloudSettings
    
    settings = CloudSettings()
    
    # Test basic attributes exist
    assert hasattr(settings, 'DEBUG')
    assert hasattr(settings, 'API_HOST')
    assert hasattr(settings, 'API_PORT')
    assert hasattr(settings, 'MAX_FILE_SIZE')
    
    # Test methods exist
    assert hasattr(settings, 'get_config_dict')
    assert hasattr(settings, 'validate_config')
    assert hasattr(settings, 'get_available_services')


def test_config_dict():
    """Test configuration dictionary generation"""
    from config.cloud_settings import CloudSettings
    
    settings = CloudSettings()
    config = settings.get_config_dict()
    
    assert isinstance(config, dict)
    assert 'debug' in config
    assert 'api' in config
    assert 'file' in config
    assert 'llm' in config
    assert 'tts' in config


def test_validate_config():
    """Test configuration validation"""
    from config.cloud_settings import CloudSettings
    
    settings = CloudSettings()
    errors, warnings = settings.validate_config()
    
    assert isinstance(errors, list)
    assert isinstance(warnings, list)


def test_available_services():
    """Test available services detection"""
    from config.cloud_settings import CloudSettings
    
    settings = CloudSettings()
    services = settings.get_available_services()
    
    assert isinstance(services, dict)
    assert 'llm' in services
    assert 'tts' in services
    assert 'vision' in services


if __name__ == "__main__":
    pytest.main([__file__]) 