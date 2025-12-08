"""
Config 模块测试

测试配置类的功能。
"""
import pytest
import tempfile
import os
from pathlib import Path
import yaml
from config.config import Config, get_config


class TestConfig:
    """Config 类测试"""

    def test_config_singleton(self):
        """测试 Config 单例模式"""
        config1 = Config.get_instance()
        config2 = Config.get_instance()
        assert config1 is config2

    def test_get_config_function(self):
        """测试 get_config 便捷函数"""
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2

    def test_config_with_custom_path(self):
        """测试使用自定义配置文件路径"""
        # 创建临时配置文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            test_config = {
                'chat_model': 'test-chat-model',
                'reasoner_model': 'test-reasoner-model'
            }
            yaml.dump(test_config, f)
            temp_path = f.name

        try:
            # 重置单例以测试新配置
            Config._instance = None
            Config._initialized = False
            
            config = Config.get_instance(temp_path)
            assert config.chat_model == 'test-chat-model'
            assert config.reasoner_model == 'test-reasoner-model'
        finally:
            # 清理
            os.unlink(temp_path)
            Config._instance = None
            Config._initialized = False

    def test_config_dict_access(self):
        """测试字典式访问配置"""
        config = get_config()
        # 测试 __getitem__
        chat_model = config['chat_model']
        assert chat_model is not None
        
        # 测试 get 方法
        value = config.get('chat_model', 'default')
        assert value is not None
        
        # 测试不存在的键
        default_value = config.get('non_existent_key', 'default')
        assert default_value == 'default'

    def test_config_reload(self):
        """测试重新加载配置"""
        config = get_config()
        original_chat_model = config.chat_model
        
        # 创建新的临时配置文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            test_config = {
                'chat_model': 'reloaded-chat-model',
                'reasoner_model': 'reloaded-reasoner-model'
            }
            yaml.dump(test_config, f)
            temp_path = f.name

        try:
            config.reload(temp_path)
            assert config.chat_model == 'reloaded-chat-model'
        finally:
            os.unlink(temp_path)

