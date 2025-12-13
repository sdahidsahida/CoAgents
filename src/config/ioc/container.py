"""
IoC容器实现
提供依赖注入和生命周期管理
"""

from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union
from abc import ABC, abstractmethod
from enum import Enum
import inspect
from dataclasses import dataclass

from ..shared.exceptions import ConfigurationError

T = TypeVar('T')


class LifetimeScope(Enum):
    """生命周期范围"""
    TRANSIENT = "transient"  # 每次请求创建新实例
    SINGLETON = "singleton"  # 单例模式
    SCOPED = "scoped"       # 作用域内单例


@dataclass
class ServiceDescriptor:
    """服务描述符"""
    service_type: Type
    implementation_type: Optional[Type] = None
    factory: Optional[Callable] = None
    instance: Optional[Any] = None
    lifetime: LifetimeScope = LifetimeScope.TRANSIENT
    
    def __post_init__(self):
        # 确保只有一个实现方式
        impl_count = sum([
            self.implementation_type is not None,
            self.factory is not None,
            self.instance is not None
        ])
        if impl_count > 1:
            raise ValueError("Only one of implementation_type, factory, or instance can be specified")


class IServiceProvider(ABC):
    """服务提供者接口"""
    
    @abstractmethod
    def get_service(self, service_type: Type[T]) -> T:
        """获取服务实例
        
        Args:
            service_type: 服务类型
            
        Returns:
            服务实例
        """
        pass
    
    @abstractmethod
    def get_required_service(self, service_type: Type[T]) -> T:
        """获取必需的服务实例
        
        Args:
            service_type: 服务类型
            
        Returns:
            服务实例
        """
        pass
    
    @abstractmethod
    def get_services(self, service_type: Type[T]) -> list[T]:
        """获取所有匹配的服务实例
        
        Args:
            service_type: 服务类型
            
        Returns:
            服务实例列表
        """
        pass
    
    def __getitem__(self, service_type: Type[T]) -> T:
        """支持字典语法"""
        return self.get_required_service(service_type)
    
    def get(self, service_type: Type[T], default: Optional[T] = None) -> Optional[T]:
        """获取服务，支持默认值"""
        return self.get_service(service_type) or default


class DIContainer(IServiceProvider):
    """依赖注入容器"""
    
    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._singletons: Dict[Type, Any] = {}
        self._scoped_instances: Dict[Type, Any] = {}
        self._building: set = set()  # 防止循环依赖
    
    def register_transient(
        self, 
        service_type: Type[T], 
        implementation_type: Optional[Type[T]] = None,
        factory: Optional[Callable[[], T]] = None
    ) -> "DIContainer":
        """注册瞬态服务
        
        Args:
            service_type: 服务接口类型
            implementation_type: 实现类型
            factory: 工厂函数
            
        Returns:
            容器实例，支持链式调用
        """
        self._services[service_type] = ServiceDescriptor(
            service_type=service_type,
            implementation_type=implementation_type,
            factory=factory,
            lifetime=LifetimeScope.TRANSIENT
        )
        return self
    
    def register_singleton(
        self,
        service_type: Type[T],
        implementation_type: Optional[Type[T]] = None,
        factory: Optional[Callable[[], T]] = None,
        instance: Optional[T] = None
    ) -> "DIContainer":
        """注册单例服务
        
        Args:
            service_type: 服务接口类型
            implementation_type: 实现类型
            factory: 工厂函数
            instance: 实例
            
        Returns:
            容器实例，支持链式调用
        """
        descriptor = ServiceDescriptor(
            service_type=service_type,
            implementation_type=implementation_type,
            factory=factory,
            instance=instance,
            lifetime=LifetimeScope.SINGLETON
        )
        
        self._services[service_type] = descriptor
        
        # 如果提供了实例，直接存储
        if instance is not None:
            self._singletons[service_type] = instance
        
        return self
    
    def register_scoped(
        self,
        service_type: Type[T],
        implementation_type: Optional[Type[T]] = None,
        factory: Optional[Callable[[], T]] = None
    ) -> "DIContainer":
        """注册作用域服务
        
        Args:
            service_type: 服务接口类型
            implementation_type: 实现类型
            factory: 工厂函数
            
        Returns:
            容器实例，支持链式调用
        """
        self._services[service_type] = ServiceDescriptor(
            service_type=service_type,
            implementation_type=implementation_type,
            factory=factory,
            lifetime=LifetimeScope.SCOPED
        )
        return self
    
    def register_instance(self, service_type: Type[T], instance: T) -> "DIContainer":
        """注册实例（作为单例）
        
        Args:
            service_type: 服务类型
            instance: 实例
            
        Returns:
            容器实例，支持链式调用
        """
        return self.register_singleton(service_type, instance=instance)
    
    def auto_register(self, implementation_type: Type, 
                     interface_types: Optional[list[Type]] = None) -> "DIContainer":
        """自动注册服务
        
        Args:
            implementation_type: 实现类型
            interface_types: 接口类型列表
            
        Returns:
            容器实例，支持链式调用
        """
        if interface_types is None:
            # 自动检测接口
            interface_types = [
                base for base in implementation_type.__bases__
                if hasattr(base, '__abstractmethods__') and base.__abstractmethods__
            ]
        
        # 如果没有接口，注册为具体类型
        if not interface_types:
            interface_types = [implementation_type]
        
        for service_type in interface_types:
            self.register_transient(service_type, implementation_type)
        
        return self
    
    def get_service(self, service_type: Type[T]) -> Optional[T]:
        """获取服务实例"""
        # 检查是否已经注册
        if service_type not in self._services:
            # 尝试自动注册
            if inspect.isabstract(service_type):
                return None
            self.register_transient(service_type, service_type)
        
        descriptor = self._services[service_type]
        
        # 处理不同生命周期
        if descriptor.lifetime == LifetimeScope.SINGLETON:
            if service_type in self._singletons:
                return self._singletons[service_type]
            
            instance = self._create_instance(service_type)
            self._singletons[service_type] = instance
            return instance
        
        elif descriptor.lifetime == LifetimeScope.SCOPED:
            if service_type in self._scoped_instances:
                return self._scoped_instances[service_type]
            
            instance = self._create_instance(service_type)
            self._scoped_instances[service_type] = instance
            return instance
        
        else:  # TRANSIENT
            return self._create_instance(service_type)
    
    def get_required_service(self, service_type: Type[T]) -> T:
        """获取必需的服务实例"""
        service = self.get_service(service_type)
        if service is None:
            raise ConfigurationError(
                f"service_{service_type.__name__}",
                f"Required service {service_type.__name__} is not registered"
            )
        return service
    
    def get_services(self, service_type: Type[T]) -> list[T]:
        """获取所有匹配的服务实例"""
        # 这里简化处理，实际应该支持注册多个实现
        service = self.get_service(service_type)
        return [service] if service else []
    
    def _create_instance(self, service_type: Type[T]) -> T:
        """创建服务实例"""
        descriptor = self._services[service_type]
        
        # 防止循环依赖
        if service_type in self._building:
            raise ValueError(f"Circular dependency detected for {service_type.__name__}")
        
        self._building.add(service_type)
        
        try:
            # 如果有实例，直接返回
            if descriptor.instance is not None:
                return descriptor.instance
            
            # 如果有工厂函数，调用工厂
            if descriptor.factory is not None:
                return descriptor.factory()
            
            # 如果有实现类型，创建实例
            if descriptor.implementation_type is not None:
                impl_type = descriptor.implementation_type
                
                # 检查是否需要依赖注入
                signature = inspect.signature(impl_type.__init__)
                kwargs = {}
                
                for param_name, param in signature.parameters.items():
                    if param_name == 'self':
                        continue
                    
                    # 检查是否有类型注解
                    if param.annotation != inspect.Parameter.empty:
                        param_type = param.annotation
                        
                        # 尝试从容器获取依赖
                        dependency = self.get_service(param_type)
                        if dependency is not None:
                            kwargs[param_name] = dependency
                        elif param.default == inspect.Parameter.empty:
                            raise ConfigurationError(
                                f"dependency_{param_type.__name__}",
                                f"Required dependency {param_type.__name__} for {impl_type.__name__} is not registered"
                            )
                
                return impl_type(**kwargs)
            
            # 默认尝试直接实例化
            return service_type()
        
        finally:
            self._building.discard(service_type)
    
    def clear_scope(self) -> None:
        """清除作用域实例"""
        self._scoped_instances.clear()
    
    def is_registered(self, service_type: Type) -> bool:
        """检查服务是否已注册"""
        return service_type in self._services
    
    def create_scope(self) -> "DIScope":
        """创建新的作用域"""
        return DIScope(self)


class DIScope:
    """依赖注入作用域"""
    
    def __init__(self, container: DIContainer):
        self.container = container
        self.old_scoped = None
    
    def __enter__(self) -> "DIScope":
        # 保存当前作用域实例
        self.old_scoped = self.container._scoped_instances.copy()
        self.container._scoped_instances.clear()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # 恢复作用域实例
        self.container._scoped_instances.clear()
        if self.old_scoped:
            self.container._scoped_instances.update(self.old_scoped)


# 全局容器实例
global_container = DIContainer()


def register_global(container_config: Callable[[DIContainer], None]) -> None:
    """注册全局服务
    
    Args:
        container_config: 配置函数
    """
    container_config(global_container)


def get_service(service_type: Type[T]) -> Optional[T]:
    """从全局容器获取服务
    
    Args:
        service_type: 服务类型
        
    Returns:
        服务实例
    """
    return global_container.get_service(service_type)


def get_required_service(service_type: Type[T]) -> T:
    """从全局容器获取必需的服务
    
    Args:
        service_type: 服务类型
        
    Returns:
        服务实例
    """
    return global_container.get_required_service(service_type)


def inject(service_type: Type[T]):
    """依赖注入装饰器
    
    用于自动注入依赖到函数参数中
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 获取函数签名
            signature = inspect.signature(func)
            
            # 为每个有类型注解的参数注入依赖
            for param_name, param in signature.parameters.items():
                if param_name in kwargs:
                    continue  # 已提供参数
                
                if param.annotation != inspect.Parameter.empty:
                    service = global_container.get_service(param.annotation)
                    if service is not None:
                        kwargs[param_name] = service
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator