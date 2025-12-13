"""
LLM 客户端封装

提供简洁易用的 LLM API 接口，支持多个模型商（DeepSeek、Gemini等）。
"""
import os
import time
from typing import Optional, List, Dict, Any, Iterator, Union
from openai import OpenAI
from dotenv import load_dotenv

from config.config import get_config  # type: ignore
from llm.response import LLMResponse  # type: ignore

# 加载环境变量
load_dotenv()


class LLMClient:
    """
    LLM 客户端类，支持多个模型商（DeepSeek、Gemini等）。
    
    提供简洁的 API 接口用于与 LLM 进行交互。
    
    Example:
        >>> # 使用 DeepSeek 聊天模型
        >>> client = LLMClient(model="deepseek-chat")
        >>> response = client.chat("Hello, how are you?")
        >>> print(response)
        
        >>> # 使用 Gemini 模型
        >>> gemini_client = LLMClient(model="gemini-2.5-flash")
        >>> response = gemini_client.chat("What is 2+2?")
        
        >>> # 使用配置中的默认模型
        >>> client = LLMClient()  # 使用配置中的 chat_model
        
        >>> # 流式响应
        >>> for chunk in client.chat_stream("Tell me a story"):
        ...     print(chunk, end='')
    """
    
    def __init__(
        self,
        model: Optional[str] = None,
        config_path: Optional[str] = None
    ):
        """
        初始化 LLM 客户端。
        
        Args:
            model: 模型名称，如 "deepseek-chat", "deepseek-reasoner", "gemini-2.5-flash"
                如果为 None，则使用配置中的 chat_model
            config_path: 配置文件路径，如果为 None 则使用默认路径
            
        Raises:
            ValueError: 如果模型名称无效或缺少必要的 API Key
        """
        # 加载配置（从 Config 类读取所有配置）
        self.config = get_config(config_path)
        
        # 使用指定的模型或配置中的默认模型
        if model is None:
            self.model_name = self.config.chat_model
        else:
            self.model_name = model
        
        self._model_type = "custom"
        
        # 根据模型名称判断使用哪个 API
        self._provider = self._detect_provider(self.model_name)
        
        # 初始化对应的客户端
        if self._provider == "deepseek":
            # DeepSeek 使用 OpenAI SDK
            api_key = self.config.api_key
            base_url = self.config.base_url
            self._client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
        elif self._provider == "gemini":
            # Gemini 使用 OpenAI SDK 兼容的 API，通过 GEMINI_BASE_URL
            gemini_api_key = os.environ.get('GEMINI_API_KEY')
            gemini_base_url = os.environ.get('GEMINI_BASE_URL')
            if not gemini_api_key:
                raise ValueError("GEMINI_API_KEY 环境变量未设置，请在 .env 文件中设置")
            if not gemini_base_url:
                raise ValueError("GEMINI_BASE_URL 环境变量未设置，请在 .env 文件中设置")
            # base_url 应该指向基础 URL，OpenAI SDK 会自动添加 /chat/completions
            # 如果 GEMINI_BASE_URL 已经包含 /chat/completions，需要移除它
            gemini_base_url = gemini_base_url.rstrip('/')
            # 移除 /chat/completions（如果存在），让 SDK 自动添加
            if gemini_base_url.endswith('/chat/completions'):
                gemini_base_url = gemini_base_url[:-len('/chat/completions')]
            # 现在 base_url 是基础 URL，SDK 会自动添加 /chat/completions
            # 最终的调用 URL 将是 GEMINI_BASE_URL/chat/completions
            self._client = OpenAI(
                api_key=gemini_api_key,
                base_url=gemini_base_url
            )
        else:
            raise ValueError(f"不支持的模型: {model}")
    
    @staticmethod
    def _detect_provider(model_name: str) -> str:
        """
        根据模型名称检测提供商。
        
        Args:
            model_name: 模型名称
            
        Returns:
            提供商名称："deepseek" 或 "gemini"
        """
        model_lower = model_name.lower()
        if model_lower.startswith("gemini"):
            return "gemini"
        elif model_lower.startswith("deepseek"):
            return "deepseek"
        else:
            # 默认使用 DeepSeek（向后兼容）
            return "deepseek"
    
    def chat(
        self,
        message: Union[str, List[Dict[str, str]]],
        system_message: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        max_retries: int = 0,
        **kwargs
    ) -> LLMResponse:
        """
        发送聊天消息并获取响应。
        
        Args:
            message: 用户消息（字符串）或消息列表
            system_message: 系统消息，如果为 None 则不设置
            model: 模型名称，如果为 None 则使用初始化时指定的模型
            temperature: 温度参数，控制输出的随机性 (0.0-2.0)
            max_tokens: 最大 token 数
            max_retries: 最大重试次数
            **kwargs: 其他传递给 API 的参数
            
        Returns:
            LLMResponse 对象，包含所有响应信息
            
        Example:
            >>> client = LLMClient(model="deepseek-chat")
            >>> response = client.chat("Hello!")
            >>> print(response.content)
            >>> print(f"耗时: {response.elapsed_time:.2f}秒")
            
            >>> # 使用推理模型时，会包含思考过程
            >>> reasoner = LLMClient(model="deepseek-reasoner")
            >>> response = reasoner.chat("What is 2+2?")
            >>> if response.has_reasoning:
            ...     print(f"思考过程: {response.reasoning_content}")
            >>> print(f"答案: {response.content}")
        """
        # 使用指定的模型或初始化时设置的模型
        model = model or self.model_name
        
        # 记录开始时间
        start_time = time.time()
        retry_count = 0
        last_exception = None
        
        # 重试逻辑
        while retry_count <= max_retries:
            try:
                # 所有提供商都使用 OpenAI SDK 兼容的 API，保持完全一致的使用方式
                messages = self._build_messages(message, system_message)
                api_response = self._client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=False,
                    **kwargs
                )
                    
                # 计算耗时
                elapsed_time = time.time() - start_time
                
                # 解析响应
                if not hasattr(api_response, 'choices') or not api_response.choices:
                    raise ValueError("API 响应中没有 choices")
                
                choice = api_response.choices[0]
                message_obj = choice.message if hasattr(choice, 'message') else None
                
                if message_obj is None:
                    raise ValueError("API 响应中没有 message")
                
                # 获取内容
                content = getattr(message_obj, 'content', None) or ""
                
                # 获取 usage 信息
                usage_info = {}
                if hasattr(api_response, 'usage') and api_response.usage:
                    usage_info = {
                        'prompt_tokens': getattr(api_response.usage, 'prompt_tokens', 0),
                        'completion_tokens': getattr(api_response.usage, 'completion_tokens', 0),
                        'total_tokens': getattr(api_response.usage, 'total_tokens', 0),
                    }
                else:
                    usage_info = {
                        'prompt_tokens': 0,
                        'completion_tokens': 0,
                        'total_tokens': 0,
                    }
                
                # 构建 LLMResponse 对象
                response = LLMResponse(
                    content=content,
                    model=getattr(api_response, 'model', model),
                    usage=usage_info,
                    id=getattr(api_response, 'id', ''),
                    created=getattr(api_response, 'created', int(time.time())),
                    finish_reason=getattr(choice, 'finish_reason', None),
                    reasoning_content=getattr(message_obj, 'reasoning_content', None),
                    elapsed_time=elapsed_time,
                    retry_count=retry_count,
                    raw_response=api_response,
                )
                
                return response
                
            except Exception as e:
                last_exception = e
                retry_count += 1
                if retry_count > max_retries:
                    raise
                # 等待后重试（简单的指数退避）
                time.sleep(min(2 ** retry_count, 10))
        
        # 如果所有重试都失败，抛出最后一个异常
        raise last_exception  # type: ignore
    
    def chat_stream(
        self,
        message: Union[str, List[Dict[str, str]]],
        system_message: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Iterator[str]:
        """
        发送聊天消息并获取流式响应。
        
        Args:
            message: 用户消息（字符串）或消息列表
            system_message: 系统消息，如果为 None 则不设置
            model: 模型名称，如果为 None 则使用初始化时指定的模型
            temperature: 温度参数，控制输出的随机性 (0.0-2.0)
            max_tokens: 最大 token 数
            **kwargs: 其他传递给 API 的参数
            
        Yields:
            响应文本的各个片段
            
        Example:
            >>> client = LLMClient(model="deepseek-chat")
            >>> for chunk in client.chat_stream("Tell me a story"):
            ...     print(chunk, end='', flush=True)
        """
        # 使用指定的模型或初始化时设置的模型
        model = model or self.model_name
        
        # 所有提供商都使用 OpenAI SDK 兼容的 API
        messages = self._build_messages(message, system_message)
        response = self._client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )
        
        # 生成响应片段
        for chunk in response:
            # 检查 choices 是否存在且不为空
            if not hasattr(chunk, 'choices') or not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            # 输出思考过程（如果有）
            if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                yield delta.reasoning_content
            # 输出内容
            if hasattr(delta, 'content') and delta.content:
                yield delta.content
    def reason(
        self,
        message: Union[str, List[Dict[str, str]]],
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        max_retries: int = 0,
        **kwargs
    ) -> LLMResponse:
        """
        使用推理模型进行推理。
        
        注意：此方法会使用配置中的 reasoner_model。
        
        Args:
            message: 用户消息（字符串）或消息列表
            system_message: 系统消息，如果为 None 则不设置
            temperature: 温度参数，控制输出的随机性 (0.0-2.0)
            max_tokens: 最大 token 数
            max_retries: 最大重试次数
            **kwargs: 其他传递给 API 的参数
            
        Returns:
            LLMResponse 对象，包含所有响应信息（包括思考过程）
            
        Example:
            >>> client = LLMClient(model="deepseek-reasoner")
            >>> response = client.reason("What is 2+2? Think step by step.")
            >>> print(response.content)
            >>> if response.has_reasoning:
            ...     print(f"思考过程: {response.reasoning_content}")
        """
        # 使用配置中的 reasoner_model
        model = self.config.reasoner_model
        return self.chat(
            message=message,
            system_message=system_message,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            max_retries=max_retries,
            **kwargs
        )
    
    def reason_stream(
        self,
        message: Union[str, List[Dict[str, str]]],
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Iterator[str]:
        """
        使用推理模型进行流式推理。
        
        注意：此方法会使用配置中的 reasoner_model。
        
        Args:
            message: 用户消息（字符串）或消息列表
            system_message: 系统消息，如果为 None 则不设置
            temperature: 温度参数，控制输出的随机性 (0.0-2.0)
            max_tokens: 最大 token 数
            **kwargs: 其他传递给 API 的参数
            
        Yields:
            响应文本的各个片段
            
        Example:
            >>> client = LLMClient(model="deepseek-reasoner")
            >>> for chunk in client.reason_stream("Solve this problem step by step"):
            ...     print(chunk, end='', flush=True)
        """
        # 使用配置中的 reasoner_model
        model = self.config.reasoner_model
        yield from self.chat_stream(
            message=message,
            system_message=system_message,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def chat_with_response(
        self,
        message: Union[str, List[Dict[str, str]]],
        system_message: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        max_retries: int = 0,
        **kwargs
    ) -> LLMResponse:
        """
        发送聊天消息并获取完整响应对象（与 chat() 方法相同，保留以保持兼容性）。
        
        Args:
            message: 用户消息（字符串）或消息列表
            system_message: 系统消息，如果为 None 则不设置
            model: 模型名称，如果为 None 则使用初始化时指定的模型
            temperature: 温度参数，控制输出的随机性 (0.0-2.0)
            max_tokens: 最大 token 数
            max_retries: 最大重试次数
            **kwargs: 其他传递给 API 的参数
            
        Returns:
            LLMResponse 对象，包含所有响应信息
            
        Example:
            >>> client = LLMClient(model="deepseek-chat")
            >>> response = client.chat_with_response("Hello!")
            >>> print(f"内容: {response.content}")
            >>> print(f"Token 使用: {response.total_tokens}")
            >>> print(f"耗时: {response.elapsed_time:.2f}秒")
            
            >>> # 推理模型的响应包含思考过程
            >>> reasoner = LLMClient(model="deepseek-reasoner")
            >>> response = reasoner.chat_with_response("What is 2+2?")
            >>> if response.has_reasoning:
            ...     print(f"思考过程: {response.reasoning_content}")
            >>> print(f"最终答案: {response.content}")
        """
        return self.chat(
            message=message,
            system_message=system_message,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            max_retries=max_retries,
            **kwargs
        )
    
    def _build_messages(
        self,
        message: Union[str, List[Dict[str, str]]],
        system_message: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        构建消息列表。
        
        Args:
            message: 用户消息（字符串）或消息列表
            system_message: 系统消息
            
        Returns:
            格式化的消息列表
        """
        messages = []
        
        # 添加系统消息
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        # 处理用户消息
        if isinstance(message, str):
            messages.append({"role": "user", "content": message})
        elif isinstance(message, list):
            messages.extend(message)
        else:
            raise ValueError(f"不支持的消息类型: {type(message)}")
        
        return messages
    
    @property
    def model(self) -> str:
        """获取当前使用的模型名称。"""
        return self.model_name
    
    @property
    def model_type(self) -> str:
        """获取模型类型（已废弃，保留用于兼容性）。"""
        return self._model_type
    
    @model_type.setter
    def model_type(self, value: str) -> None:
        """设置模型类型（已废弃，保留用于兼容性）。"""
        self._model_type = value
    
    def __repr__(self) -> str:
        """返回客户端对象的字符串表示。"""
        return f"LLMClient(model='{self.model_name}')"


# 全局客户端实例（延迟初始化）
_client: Optional[LLMClient] = None


def get_client(
    model: Optional[str] = None,
    config_path: Optional[str] = None
) -> LLMClient:
    """
    获取全局 LLM 客户端实例的便捷函数。
    
    Args:
        model: 模型名称，如 "deepseek-chat", "deepseek-reasoner", "gemini-2.5-flash"
            如果为 None，则使用配置中的 chat_model
        config_path: 配置文件路径，如果为 None 则使用默认路径
        
    Returns:
        LLMClient 实例
        
    Example:
        >>> client = get_client(model="deepseek-chat")
        >>> response = client.chat("Hello!")
    """
    global _client
    if _client is None:
        _client = LLMClient(model=model, config_path=config_path)
    return _client

