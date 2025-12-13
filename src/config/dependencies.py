"""
依赖注入配置
配置和管理项目的依赖关系
"""

from typing import Optional
import logging

from ..config.ioc.container import DIContainer, global_container, register_global
from ..config.config_manager import get_config
from ..core.ports.llm.provider import LLMProvider
from ..core.ports.tools.calculator import AstrologyTool
from ..core.ports.storage.cache import CacheProvider
from ..core.ports.storage.config import ConfigProvider

logger = logging.getLogger(__name__)


def setup_dependencies(
    container: Optional[DIContainer] = None
) -> DIContainer:
    """设置依赖关系
    
    Args:
        container: 容器实例，None则使用全局容器
        
    Returns:
        配置好的容器
    """
    if container is None:
        container = global_container
    
    config = get_config()
    
    # 注册配置提供者
    container.register_singleton(ConfigProvider, instance=config)
    
    # 注册缓存提供者
    cache_type = config.get_str("cache.type", "memory")
    if cache_type == "redis":
        # TODO: 实现Redis缓存
        from ..core.ports.storage.cache import MemoryCache
        logger.warning("Redis cache not implemented yet, using memory cache")
        container.register_singleton(CacheProvider, MemoryCache)
    else:
        from ..core.ports.storage.cache import MemoryCache
        container.register_singleton(CacheProvider, MemoryCache)
    
    # 注册LLM提供商
    def create_llm_provider() -> LLMProvider:
        """LLM提供商工厂函数"""
        provider_name = config.get_str("llm.provider", "deepseek")
        api_key = config.get_str(f"llm.{provider_name}.api_key")
        if not api_key:
            raise ValueError(f"LLM API key not configured for provider: {provider_name}")
        
        if provider_name == "deepseek":
            from ..infrastructure.llm.deepseek_client import DeepSeekProvider
            return DeepSeekProvider(
                api_key=api_key,
                base_url=config.get_str(f"llm.{provider_name}.base_url"),
                timeout=config.get_int(f"llm.{provider_name}.timeout", 30)
            )
        elif provider_name == "gemini":
            from ..infrastructure.llm.gemini_client import GeminiProvider
            return GeminiProvider(
                api_key=api_key,
                model=config.get_str(f"llm.{provider_name}.model", "gemini-2.0-flash-exp")
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider_name}")
    
    container.register_singleton(LLMProvider, factory=create_llm_provider)
    
    # 注册算命工具
    def create_bazi_tool() -> AstrologyTool:
        """八字工具工厂函数"""
        from ..infrastructure.tools.bazi_tool import BaziTool
        return BaziTool()
    
    def create_ziwei_tool() -> AstrologyTool:
        """紫微斗数工具工厂函数"""
        from ..infrastructure.tools.ziwei_tool import ZiweiTool
        return ZiweiTool()
    
    def create_astrology_tool() -> AstrologyTool:
        """西方占星工具工厂函数"""
        from ..infrastructure.tools.astrology_tool import WesternAstrologyTool
        return WesternAstrologyTool()
    
    # 注册为字典形式，支持按名称获取
    container.register_singleton(
        dict[str, AstrologyTool],
        factory=lambda: {
            "bazi": create_bazi_tool(),
            "ziwei": create_ziwei_tool(),
            "astrology": create_astrology_tool()
        }
    )
    
    # 注册工具管理器
    from ..application.services.tool_service import ToolService
    container.register_singleton(ToolService)
    
    # 注册应用服务
    from ..application.services.moa_service import MOAService
    container.register_singleton(MOAService)
    
    from ..application.services.chart_service import ChartService
    container.register_singleton(ChartService)
    
    from ..application.services.report_service import ReportService
    container.register_singleton(ReportService)
    
    logger.info("Dependencies configured successfully")
    
    return container


# 自动注册到全局容器
register_global(setup_dependencies)


def get_provider(service_type: type):
    """获取服务的便捷函数"""
    return global_container.get_required_service(service_type)


def inject_dependencies(func):
    """依赖注入装饰器"""
    from ..config.ioc.container import inject
    return inject(func)