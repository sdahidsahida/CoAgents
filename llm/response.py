"""
LLM 响应类

封装 LLM API 的所有返回信息。
"""
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class LLMResponse:
    """
    LLM 响应类，包含所有返回信息。
    
    Attributes:
        content: 响应文本内容
        reasoning_content: 思考过程（仅推理模型有）
        model: 使用的模型名称
        usage: Token 使用统计
        id: 响应 ID
        created: 创建时间戳
        finish_reason: 完成原因
        elapsed_time: 请求耗时（秒）
        retry_count: 重试次数
        raw_response: 原始 API 响应对象（可选）
    """
    content: str
    model: str
    usage: Dict[str, int]
    id: str
    created: int
    finish_reason: Optional[str] = None
    reasoning_content: Optional[str] = None
    elapsed_time: float = 0.0
    retry_count: int = 0
    raw_response: Optional[Any] = None
    
    def __str__(self) -> str:
        """返回响应内容的字符串表示。"""
        return self.content
    
    def __repr__(self) -> str:
        """返回响应对象的详细表示。"""
        return (
            f"LLMResponse("
            f"model='{self.model}', "
            f"content_length={len(self.content)}, "
            f"elapsed_time={self.elapsed_time:.2f}s, "
            f"retry_count={self.retry_count}"
            f")"
        )
    
    @property
    def has_reasoning(self) -> bool:
        """检查是否包含思考过程。"""
        return self.reasoning_content is not None and len(self.reasoning_content) > 0
    
    @property
    def full_content(self) -> str:
        """获取包含思考过程的完整内容。"""
        if self.has_reasoning:
            return f"{self.reasoning_content}\n\n{self.content}"
        return self.content
    
    @property
    def prompt_tokens(self) -> int:
        """获取 prompt token 数量。"""
        return self.usage.get('prompt_tokens', 0)
    
    @property
    def completion_tokens(self) -> int:
        """获取 completion token 数量。"""
        return self.usage.get('completion_tokens', 0)
    
    @property
    def total_tokens(self) -> int:
        """获取总 token 数量。"""
        return self.usage.get('total_tokens', 0)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式。"""
        return {
            'content': self.content,
            'reasoning_content': self.reasoning_content,
            'model': self.model,
            'usage': self.usage,
            'id': self.id,
            'created': self.created,
            'finish_reason': self.finish_reason,
            'elapsed_time': self.elapsed_time,
            'retry_count': self.retry_count,
        }
    
    def to_json(self) -> str:
        """转换为 JSON 字符串格式。"""
        import json
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

