"""
配置接口
定义配置管理的标准接口
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, TypeVar, Type
from pathlib import Path
import os
from dataclasses import dataclass

from ...shared.exceptions import ConfigurationError

T = TypeVar('T')


@dataclass
class ConfigValue:
    """配置值"""
    key: str
    value: Any
    source: str  # 配置来源
    is_required: bool = False
    default: Any = None
    validator: Optional[callable] = None


class ConfigProvider(ABC):
    """配置提供者接口"""
    
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        pass
    
    @abstractmethod
    def get_typed(self, key: str, type_hint: Type[T], default: Optional[T] = None) -> T:
        """获取带类型的配置值
        
        Args:
            key: 配置键
            type_hint: 类型提示
            default: 默认值
            
        Returns:
            转换后的配置值
        """
        pass
    
    @abstractmethod
    def get_section(self, prefix: str) -> Dict[str, Any]:
        """获取配置节
        
        Args:
            prefix: 配置节前缀
            
        Returns:
            配置字典
        """
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """设置配置值
        
        Args:
            key: 配置键
            value: 配置值
        """
        pass
    
    @abstractmethod
    def has(self, key: str) -> bool:
        """检查配置是否存在
        
        Args:
            key: 配置键
            
        Returns:
            是否存在
        """
        pass
    
    @abstractmethod
    def reload(self) -> None:
        """重新加载配置"""
        pass
    
    @abstractmethod
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置
        
        Returns:
            完整配置字典
        """
        pass
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """获取布尔值配置
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            布尔值
        """
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on', 'enabled')
        return bool(value)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """获取整数配置
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            整数值
        """
        value = self.get(key, default)
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """获取浮点数配置
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            浮点数值
        """
        value = self.get(key, default)
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def get_str(self, key: str, default: str = "") -> str:
        """获取字符串配置
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            字符串值
        """
        value = self.get(key, default)
        return str(value)
    
    def get_list(self, key: str, default: List[str] = None, separator: str = ",") -> List[str]:
        """获取列表配置
        
        Args:
            key: 配置键
            default: 默认值
            separator: 分隔符
            
        Returns:
            列表值
        """
        if default is None:
            default = []
        
        value = self.get(key)
        if value is None:
            return default
        
        if isinstance(value, list):
            return [str(v) for v in value]
        
        if isinstance(value, str):
            return [v.strip() for v in value.split(separator) if v.strip()]
        
        return [str(value)]
    
    def get_path(self, key: str, default: Optional[Union[str, Path]] = None) -> Path:
        """获取路径配置
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            Path对象
        """
        value = self.get(key, default)
        if value is None:
            raise ConfigurationError(key, "Path configuration is required")
        
        path = Path(value)
        if not path.is_absolute():
            # 相对于项目根目录
            path = Path.cwd() / path
        
        return path
    
    def get_url(self, key: str, default: str = "") -> str:
        """获取URL配置
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            URL字符串
        """
        url = self.get_str(key, default)
        if url and not url.startswith(('http://', 'https://', 'file://')):
            # 默认添加http://
            url = 'http://' + url
        return url
    
    def validate_required(self, keys: List[str]) -> None:
        """验证必需的配置项
        
        Args:
            keys: 必需的配置键列表
            
        Raises:
            ConfigurationError: 如果缺少必需的配置
        """
        missing = []
        for key in keys:
            if not self.has(key) or self.get(key) is None:
                missing.append(key)
        
        if missing:
            raise ConfigurationError(
                "required_config",
                f"Missing required configuration: {', '.join(missing)}"
            )
    
    def get_child(self, prefix: str) -> "ConfigProvider":
        """获取子配置提供者
        
        Args:
            prefix: 配置前缀
            
        Returns:
            子配置提供者
        """
        return ChildConfigProvider(self, prefix)


class ChildConfigProvider(ConfigProvider):
    """子配置提供者"""
    
    def __init__(self, parent: ConfigProvider, prefix: str):
        self.parent = parent
        self.prefix = prefix.rstrip('.') + '.'
    
    def _get_key(self, key: str) -> str:
        """获取完整的配置键"""
        return self.prefix + key
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.parent.get(self._get_key(key), default)
    
    def get_typed(self, key: str, type_hint: Type[T], default: Optional[T] = None) -> T:
        return self.parent.get_typed(self._get_key(key), type_hint, default)
    
    def get_section(self, prefix: str) -> Dict[str, Any]:
        return self.parent.get_section(self.prefix + prefix)
    
    def set(self, key: str, value: Any) -> None:
        self.parent.set(self._get_key(key), value)
    
    def has(self, key: str) -> bool:
        return self.parent.has(self._get_key(key))
    
    def reload(self) -> None:
        self.parent.reload()
    
    def get_all(self) -> Dict[str, Any]:
        all_config = self.parent.get_all()
        prefix_len = len(self.prefix)
        return {
            key[prefix_len:]: value
            for key, value in all_config.items()
            if key.startswith(self.prefix)
        }


class EnvironmentConfigProvider(ConfigProvider):
    """环境变量配置提供者"""
    
    def __init__(self, prefix: str = ""):
        self.prefix = prefix
    
    def _get_env_key(self, key: str) -> str:
        """获取环境变量键名"""
        if self.prefix:
            return f"{self.prefix}_{key}".upper()
        return key.upper()
    
    def get(self, key: str, default: Any = None) -> Any:
        return os.getenv(self._get_env_key(key), default)
    
    def get_typed(self, key: str, type_hint: Type[T], default: Optional[T] = None) -> T:
        value = self.get(key, default)
        if value is None:
            return default
        
        if type_hint is bool:
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'on')
            return bool(value)
        
        try:
            return type_hint(value)
        except (ValueError, TypeError):
            return default
    
    def get_section(self, prefix: str) -> Dict[str, Any]:
        env_prefix = self._get_env_key(prefix)
        return {
            key[len(env_prefix) + 1:]: value
            for key, value in os.environ.items()
            if key.startswith(env_prefix + '_')
        }
    
    def set(self, key: str, value: Any) -> None:
        os.environ[self._get_env_key(key)] = str(value)
    
    def has(self, key: str) -> bool:
        return self._get_env_key(key) in os.environ
    
    def reload(self) -> None:
        # 环境变量无需重新加载
        pass
    
    def get_all(self) -> Dict[str, Any]:
        return dict(os.environ)