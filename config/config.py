import yaml
import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv
load_dotenv()

class Config:
    """
    全局配置类，使用单例模式确保整个应用中只有一个配置实例。
    """
    _instance: Optional['Config'] = None
    _initialized: bool = False

    def __new__(cls, config_path: Optional[str] = None):
        """
        单例模式实现：确保只创建一个实例。
        
        Args:
            config_path: 配置文件路径，仅在首次创建时有效
            
        Returns:
            Config实例
        """
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置。如果已经初始化过，则跳过重复初始化。
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        if self._initialized:
            return

        if config_path is None:
            # 默认配置文件路径：项目根目录下的 config/config.yaml
            current_file = Path(__file__)
            config_path = current_file.parent / 'config.yaml'
            if not config_path.exists():
                # 如果不存在，尝试项目根目录
                config_path = current_file.parent.parent / 'config' / 'config.yaml'

        self._load_config(config_path)
        Config._initialized = True

    def _load_config(self, config_path: str) -> None:
        """
        加载配置文件。
        
        Args:
            config_path: 配置文件路径
            
        Raises:
            FileNotFoundError: 配置文件不存在
            yaml.YAMLError: YAML解析错误
            KeyError: 缺少必需的配置项
        """
        config_path = Path(config_path)
        
        # 确保加载 config 目录下的 .env 文件
        config_dir = config_path.parent
        env_path = config_dir / '.env'
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=True)
        
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.data: Dict[str, Any] = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"YAML解析错误: {e}")

        # 加载配置项
        self.chat_model: str = self.data.get('chat_model', '')
        self.reasoner_model: str = self.data.get('reasoner_model', '')
        
        # 从配置文件或环境变量读取 API 凭证（优先使用环境变量）
        self._api_key: str = os.environ.get('DEEPSEEK_API_KEY') or self.data.get('api_key', '')
        self._base_url: str = os.environ.get('DEEPSEEK_BASE_URL') or self.data.get('base_url', '')

        # 验证必需的配置项
        if not self.chat_model:
            raise ValueError("配置文件中缺少必需的配置项: chat_model")
        if not self.reasoner_model:
            raise ValueError("配置文件中缺少必需的配置项: reasoner_model")
        if not self.api_key:
            raise ValueError("API Key 未设置，请在配置文件中设置 api_key 或设置环境变量 DEEPSEEK_API_KEY")
        if not self.base_url:
            raise ValueError("Base URL 未设置，请在配置文件中设置 base_url 或设置环境变量 DEEPSEEK_BASE_URL")

    @classmethod
    def get_instance(cls, config_path: Optional[str] = None) -> 'Config':
        """
        获取配置实例（推荐使用此方法）。
        
        Args:
            config_path: 配置文件路径，仅在首次调用时有效
            
        Returns:
            Config实例
        """
        if cls._instance is None:
            cls._instance = cls(config_path)
        return cls._instance

    def reload(self, config_path: Optional[str] = None) -> None:
        """
        重新加载配置文件。
        
        Args:
            config_path: 配置文件路径，如果为None则使用当前配置路径
        """
        Config._initialized = False
        self.__init__(config_path)

    def __getitem__(self, key: str) -> Any:
        """支持字典式访问配置项。"""
        return self.data.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """支持字典式设置配置项。"""
        self.data[key] = value
        # 同步更新属性
        if key == 'chat_model':
            self.chat_model = value
        elif key == 'reasoner_model':
            self.reasoner_model = value

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项，如果不存在则返回默认值。"""
        return self.data.get(key, default)

    def __repr__(self) -> str:
        """返回配置对象的字符串表示。"""
        return f"Config(chat_model='{self.chat_model}', reasoner_model='{self.reasoner_model}')"
    
    @property
    def api_key(self) -> str:
        """获取 API Key。"""
        return self._api_key
    
    @api_key.setter
    def api_key(self, value: str) -> None:
        """设置 API Key。"""
        self._api_key = value
    
    @property
    def base_url(self) -> str:
        """获取 Base URL。"""
        return self._base_url
    
    @base_url.setter
    def base_url(self, value: str) -> None:
        """设置 Base URL。"""
        self._base_url = value


# 全局配置实例（延迟初始化）
_config: Optional[Config] = None


def get_config(config_path: Optional[str] = None) -> Config:
    """
    获取全局配置实例的便捷函数。
    
    Args:
        config_path: 配置文件路径，仅在首次调用时有效
        
    Returns:
        Config实例
        
    Example:
        >>> config = get_config('config/config.yaml')
        >>> print(config.chat_model)
    """
    global _config
    if _config is None:
        _config = Config.get_instance(config_path)
    return _config


# 默认全局配置实例（在导入时自动初始化，使用默认路径）
# 如果需要自定义路径，请使用 get_config(config_path) 或 Config.get_instance(config_path)
config = Config.get_instance()


