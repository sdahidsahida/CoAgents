"""
LLM提供商接口
定义LLM服务的标准接口
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, AsyncIterator
from dataclasses import dataclass
from datetime import datetime

from ..value_objects.message import Message
from ..exceptions import ProviderError, AuthenticationError, RateLimitError, TimeoutError


@dataclass
class ModelInfo:
    """模型信息"""
    name: str
    max_tokens: int
    supports_streaming: bool
    pricing: Optional[Dict[str, float]] = None


@dataclass
class Usage:
    """使用量统计"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    
    def get_cost(self, pricing: Dict[str, float]) -> float:
        """计算费用"""
        return (self.prompt_tokens * pricing.get("prompt", 0) + 
                self.completion_tokens * pricing.get("completion", 0))


@dataclass
class LLMResponse:
    """LLM响应"""
    content: str
    model: str
    usage: Usage
    finish_reason: Optional[str] = None
    reasoning_content: Optional[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class LLMProvider(ABC):
    """LLM提供商接口"""
    
    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self._config = kwargs
    
    @abstractmethod
    async def chat(
        self, 
        messages: List[Message], 
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """聊天接口
        
        Args:
            messages: 消息列表
            model: 模型名称
            max_tokens: 最大token数
            temperature: 温度参数
            **kwargs: 其他参数
            
        Returns:
            LLM响应对象
        """
        pass
    
    @abstractmethod
    async def chat_stream(
        self, 
        messages: List[Message],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncIterator[str]:
        """流式聊天接口
        
        Args:
            messages: 消息列表
            model: 模型名称
            max_tokens: 最大token数
            temperature: 温度参数
            **kwargs: 其他参数
            
        Yields:
            响应文本片段
        """
        pass
    
    @abstractmethod
    def get_model_info(self, model: Optional[str] = None) -> ModelInfo:
        """获取模型信息
        
        Args:
            model: 模型名称
            
        Returns:
            模型信息对象
        """
        pass
    
    @abstractmethod
    async def validate_api_key(self) -> bool:
        """验证API密钥有效性
        
        Returns:
            是否有效
        """
        pass
    
    def get_provider_name(self) -> str:
        """获取提供商名称"""
        return self.__class__.__name__.replace("Provider", "").lower()
    
    async def chat_with_retry(
        self,
        messages: List[Message],
        max_retries: int = 3,
        backoff_factor: float = 1.0,
        **kwargs
    ) -> LLMResponse:
        """带重试的聊天请求
        
        Args:
            messages: 消息列表
            max_retries: 最大重试次数
            backoff_factor: 退避因子
            **kwargs: 其他参数
            
        Returns:
            LLM响应对象
        """
        import asyncio
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return await self.chat(messages, **kwargs)
            except AuthenticationError as e:
                # 认证错误不重试
                raise e
            except RateLimitError as e:
                # 速率限制错误，等待后重试
                if attempt < max_retries:
                    wait_time = e.retry_after or (backoff_factor * (2 ** attempt))
                    await asyncio.sleep(wait_time)
                    continue
                raise e
            except TimeoutError as e:
                # 超时错误重试
                last_exception = e
                if attempt < max_retries:
                    continue
                raise e
            except Exception as e:
                # 其他错误
                last_exception = e
                if attempt < max_retries:
                    continue
                raise ProviderError(
                    self.get_provider_name(),
                    f"Failed after {max_retries} retries: {str(e)}"
                )
        
        # 不应该到达这里
        raise last_exception