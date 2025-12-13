"""
配置管理系统
支持多环境配置和配置合并
"""

import os
import yaml
import json
from pathlib import Path
from typing import Any, Dict, Optional, Union, List
import logging

from ..core.ports.storage.config import ConfigProvider, EnvironmentConfigProvider
from ..core.shared.exceptions import ConfigurationError

logger = logging.getLogger(__name__)


class FileConfigProvider(ConfigProvider):
    """文件配置提供者"""
    
    def __init__(self, file_path: Union[str, Path], format: str = "auto"):
        self.file_path = Path(file_path)
        self.format = format
        self._config: Dict[str, Any] = {}
        self._load()
    
    def _load(self) -> None:
        """加载配置文件"""
        if not self.file_path.exists():
            logger.warning(f"Config file not found: {self.file_path}")
            self._config = {}
            return
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 自动检测格式
            if self.format == "auto":
                if self.file_path.suffix.lower() in ['.yml', '.yaml']:
                    self.format = "yaml"
                elif self.file_path.suffix.lower() == '.json':
                    self.format = "json"
                else:
                    # 尝试解析为YAML
                    try:
                        self._config = yaml.safe_load(content) or {}
                        self.format = "yaml"
                    except yaml.YAMLError:
                        # 尝试解析为JSON
                        try:
                            self._config = json.loads(content) or {}
                            self.format = "json"
                        except json.JSONDecodeError:
                            raise ConfigurationError(
                                "config_format",
                                f"Unable to determine format for {self.file_path}"
                            )
            
            # 解析配置
            if self.format == "yaml":
                self._config = yaml.safe_load(content) or {}
            elif self.format == "json":
                self._config = json.loads(content) or {}
            
            logger.debug(f"Loaded config from {self.file_path} with {len(self._config)} keys")
            
        except Exception as e:
            raise ConfigurationError(
                "config_load",
                f"Failed to load config from {self.file_path}: {str(e)}"
            )
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_typed(self, key: str, type_hint: type, default: Optional[Any] = None) -> Any:
        """获取带类型的配置值"""
        value = self.get(key, default)
        
        if value is None:
            return default
        
        if type_hint is bool:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'on', 'enabled')
            return bool(value)
        
        try:
            return type_hint(value)
        except (ValueError, TypeError):
            return default
    
    def get_section(self, prefix: str) -> Dict[str, Any]:
        """获取配置节"""
        keys = prefix.split('.')
        section = self._config
        
        for k in keys:
            if isinstance(section, dict) and k in section:
                section = section[k]
            else:
                return {}
        
        return section if isinstance(section, dict) else {}
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def has(self, key: str) -> bool:
        """检查配置是否存在"""
        return self.get(key) is not None
    
    def reload(self) -> None:
        """重新加载配置"""
        self._load()
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self._config.copy()


class CompositeConfigProvider(ConfigProvider):
    """组合配置提供者"""
    
    def __init__(self, providers: List[ConfigProvider]):
        self.providers = providers
    
    def get(self, key: str, default: Any = None) -> Any:
        """按优先级获取配置值"""
        for provider in self.providers:
            if provider.has(key):
                return provider.get(key, default)
        return default
    
    def get_typed(self, key: str, type_hint: type, default: Optional[Any] = None) -> Any:
        """按优先级获取带类型的配置值"""
        for provider in self.providers:
            if provider.has(key):
                return provider.get_typed(key, type_hint, default)
        return default
    
    def get_section(self, prefix: str) -> Dict[str, Any]:
        """合并所有提供者的配置节"""
        result = {}
        for provider in reversed(self.providers):
            section = provider.get_section(prefix)
            result.update(section)
        return result
    
    def set(self, key: str, value: Any) -> None:
        """设置到第一个提供者"""
        if self.providers:
            self.providers[0].set(key, value)
    
    def has(self, key: str) -> bool:
        """检查是否存在"""
        return any(provider.has(key) for provider in self.providers)
    
    def reload(self) -> None:
        """重新加载所有提供者"""
        for provider in self.providers:
            provider.reload()
    
    def get_all(self) -> Dict[str, Any]:
        """合并所有配置"""
        result = {}
        for provider in reversed(self.providers):
            result.update(provider.get_all())
        return result


class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.providers: List[ConfigProvider] = []
        self._env_prefix = None
    
    def add_file(self, file_path: Union[str, Path], format: str = "auto") -> "ConfigManager":
        """添加文件配置提供者"""
        provider = FileConfigProvider(file_path, format)
        self.providers.append(provider)
        return self
    
    def add_environment(self, prefix: str = "") -> "ConfigManager":
        """添加环境变量配置提供者"""
        provider = EnvironmentConfigProvider(prefix)
        self.providers.append(provider)
        self._env_prefix = prefix
        return self
    
    def add_memory(self, initial_config: Optional[Dict[str, Any]] = None) -> "ConfigManager":
        """添加内存配置提供者"""
        from ..core.ports.storage.cache import MemoryCache
        cache = MemoryCache()
        
        if initial_config:
            for key, value in initial_config.items():
                cache.set(key, value)
        
        self.providers.append(cache)
        return self
    
    def build(self) -> ConfigProvider:
        """构建配置提供者"""
        if not self.providers:
            raise ConfigurationError("config_build", "No configuration providers added")
        
        # 环境变量具有最高优先级
        env_provider = None
        other_providers = []
        
        for provider in self.providers:
            if isinstance(provider, EnvironmentConfigProvider):
                env_provider = provider
            else:
                other_providers.append(provider)
        
        if env_provider:
            # 环境变量覆盖其他配置
            providers = other_providers + [env_provider]
        else:
            providers = other_providers
        
        return CompositeConfigProvider(providers)


def load_config(
    config_dir: Optional[Union[str, Path]] = None,
    environment: Optional[str] = None,
    env_prefix: str = "ASTROLOGY"
) -> ConfigProvider:
    """加载配置
    
    Args:
        config_dir: 配置目录
        environment: 环境名称（development, production, test）
        env_prefix: 环境变量前缀
        
    Returns:
        配置提供者
    """
    manager = ConfigManager()
    
    # 配置目录
    if config_dir is None:
        config_dir = Path(__file__).parent / "settings"
    else:
        config_dir = Path(config_dir)
    
    # 加载基础配置
    base_config = config_dir / "base.yaml"
    if base_config.exists():
        manager.add_file(base_config)
    
    # 加载环境特定配置
    if environment is None:
        environment = os.getenv(f"{env_prefix}_ENV", "development")
    
    env_config = config_dir / f"{environment}.yaml"
    if env_config.exists():
        manager.add_file(env_config)
    
    # 加载本地配置（覆盖）
    local_config = config_dir / "local.yaml"
    if local_config.exists():
        manager.add_file(local_config)
    
    # 添加环境变量（最高优先级）
    manager.add_environment(env_prefix)
    
    return manager.build()


# 全局配置实例
_config_provider: Optional[ConfigProvider] = None


def get_config() -> ConfigProvider:
    """获取全局配置实例"""
    global _config_provider
    if _config_provider is None:
        # 默认配置加载
        config_dir = Path(__file__).parent.parent / "settings"
        environment = os.getenv("ENV", "development")
        _config_provider = load_config(config_dir, environment)
    return _config_provider


def reload_config() -> None:
    """重新加载全局配置"""
    global _config_provider
    if _config_provider is not None:
        _config_provider.reload()