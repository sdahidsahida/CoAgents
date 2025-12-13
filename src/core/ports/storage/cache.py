"""
缓存接口
定义缓存存储的标准接口
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List, Union
from datetime import timedelta
from dataclasses import dataclass

from ...shared.exceptions import ResourceNotFoundError, TimeoutError


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    ttl: Optional[float] = None  # 生存时间（秒）
    created_at: Optional[float] = None  # 创建时间戳
    
    def __post_init__(self):
        import time
        if self.created_at is None:
            self.created_at = time.time()
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.ttl is None:
            return False
        import time
        return time.time() - self.created_at > self.ttl


class CacheProvider(ABC):
    """缓存提供者接口"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在或已过期返回None
        """
        pass
    
    @abstractmethod
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[Union[float, timedelta]] = None
    ) -> None:
        """设置缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 生存时间（秒或timedelta对象）
        """
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """删除缓存
        
        Args:
            key: 缓存键
            
        Returns:
            是否删除成功
        """
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """检查缓存是否存在
        
        Args:
            key: 缓存键
            
        Returns:
            是否存在且未过期
        """
        pass
    
    @abstractmethod
    async def clear(self, pattern: Optional[str] = None) -> int:
        """清除缓存
        
        Args:
            pattern: 匹配模式，None表示清除所有
            
        Returns:
            清除的键数量
        """
        pass
    
    @abstractmethod
    async def get_ttl(self, key: str) -> Optional[float]:
        """获取剩余生存时间
        
        Args:
            key: 缓存键
            
        Returns:
            剩余生存时间（秒），-1表示永不过期，-2表示不存在
        """
        pass
    
    @abstractmethod
    async def expire(self, key: str, ttl: Union[float, timedelta]) -> bool:
        """设置过期时间
        
        Args:
            key: 缓存键
            ttl: 生存时间（秒或timedelta对象）
            
        Returns:
            是否设置成功
        """
        pass
    
    async def get_or_set(
        self,
        key: str,
        factory,
        ttl: Optional[Union[float, timedelta]] = None
    ) -> Any:
        """获取缓存，如果不存在则通过factory创建并缓存
        
        Args:
            key: 缓存键
            factory: 值工厂函数或协程函数
            ttl: 生存时间
            
        Returns:
            缓存值
        """
        value = await self.get(key)
        if value is not None:
            return value
        
        # 创建新值
        if asyncio.iscoroutinefunction(factory):
            value = await factory()
        else:
            value = factory()
        
        # 设置缓存
        await self.set(key, value, ttl)
        return value
    
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """批量获取
        
        Args:
            keys: 缓存键列表
            
        Returns:
            键值对字典
        """
        results = {}
        for key in keys:
            value = await self.get(key)
            if value is not None:
                results[key] = value
        return results
    
    async def set_many(
        self, 
        items: Dict[str, Any], 
        ttl: Optional[Union[float, timedelta]] = None
    ) -> None:
        """批量设置
        
        Args:
            items: 键值对字典
            ttl: 生存时间
        """
        for key, value in items.items():
            await self.set(key, value, ttl)
    
    async def delete_many(self, keys: List[str]) -> int:
        """批量删除
        
        Args:
            keys: 缓存键列表
            
        Returns:
            删除成功的数量
        """
        count = 0
        for key in keys:
            if await self.delete(key):
                count += 1
        return count
    
    def normalize_ttl(self, ttl: Union[float, timedelta]) -> float:
        """标准化TTL值
        
        Args:
            ttl: 生存时间
            
        Returns:
            秒数
        """
        if isinstance(ttl, timedelta):
            return ttl.total_seconds()
        return ttl
    
    def generate_key(self, *parts: str) -> str:
        """生成缓存键
        
        Args:
            *parts: 键的组成部分
            
        Returns:
            格式化的缓存键
        """
        return ":".join(str(p) for p in parts)


class MemoryCache(CacheProvider):
    """内存缓存实现（用于测试）"""
    
    def __init__(self):
        self._cache: Dict[str, CacheEntry] = {}
    
    async def get(self, key: str) -> Optional[Any]:
        entry = self._cache.get(key)
        if entry is None or entry.is_expired():
            return None
        return entry.value
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[Union[float, timedelta]] = None
    ) -> None:
        if ttl is not None:
            ttl = self.normalize_ttl(ttl)
        self._cache[key] = CacheEntry(key, value, ttl)
    
    async def delete(self, key: str) -> bool:
        return self._cache.pop(key, None) is not None
    
    async def exists(self, key: str) -> bool:
        entry = self._cache.get(key)
        return entry is not None and not entry.is_expired()
    
    async def clear(self, pattern: Optional[str] = None) -> int:
        if pattern is None:
            count = len(self._cache)
            self._cache.clear()
            return count
        
        import fnmatch
        to_delete = []
        for key in self._cache:
            if fnmatch.fnmatch(key, pattern):
                to_delete.append(key)
        
        for key in to_delete:
            del self._cache[key]
        
        return len(to_delete)
    
    async def get_ttl(self, key: str) -> Optional[float]:
        entry = self._cache.get(key)
        if entry is None:
            return -2
        if entry.ttl is None:
            return -1
        remaining = entry.ttl - (entry.created_at - entry.created_at)
        return max(0, remaining)
    
    async def expire(self, key: str, ttl: Union[float, timedelta]) -> bool:
        entry = self._cache.get(key)
        if entry is None:
            return False
        entry.ttl = self.normalize_ttl(ttl)
        return True