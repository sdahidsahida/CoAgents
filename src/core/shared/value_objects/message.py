"""
消息值对象
定义LLM交互的消息格式
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum


class MessageRole(Enum):
    """消息角色"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class Message:
    """消息对象"""
    role: MessageRole
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    created_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    @classmethod
    def system(cls, content: str, **kwargs) -> "Message":
        """创建系统消息"""
        return cls(role=MessageRole.SYSTEM, content=content, **kwargs)
    
    @classmethod
    def user(cls, content: str, **kwargs) -> "Message":
        """创建用户消息"""
        return cls(role=MessageRole.USER, content=content, **kwargs)
    
    @classmethod
    def assistant(cls, content: str, **kwargs) -> "Message":
        """创建助手消息"""
        return cls(role=MessageRole.ASSISTANT, content=content, **kwargs)
    
    @classmethod
    def tool(cls, content: str, tool_call_id: str, **kwargs) -> "Message":
        """创建工具消息"""
        return cls(
            role=MessageRole.TOOL,
            content=content,
            tool_call_id=tool_call_id,
            **kwargs
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "role": self.role.value,
            "content": self.content
        }
        
        if self.name:
            result["name"] = self.name
        
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls
        
        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id
        
        if self.metadata:
            result["metadata"] = self.metadata
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """从字典创建消息对象"""
        return cls(
            role=MessageRole(data["role"]),
            content=data["content"],
            name=data.get("name"),
            tool_calls=data.get("tool_calls"),
            tool_call_id=data.get("tool_call_id"),
            metadata=data.get("metadata")
        )
    
    def copy(self, **kwargs) -> "Message":
        """创建消息副本"""
        import copy
        new_data = self.to_dict()
        new_data.update(kwargs)
        return cls.from_dict(new_data)
    
    def truncate(self, max_length: int) -> "Message":
        """截断消息内容"""
        if len(self.content) <= max_length:
            return self
        
        return self.copy(
            content=self.content[:max_length-3] + "...",
            metadata={
                **(self.metadata or {}),
                "original_length": len(self.content),
                "truncated": True
            }
        )
    
    def count_tokens(self) -> int:
        """估算token数量（简单实现）"""
        # 这是一个简化的估算，实际应该使用tiktoken
        # 中文字符平均每个约1.5个token
        # 英文单词平均每个约1.3个token
        chinese_chars = len([c for c in self.content if '\u4e00' <= c <= '\u9fff'])
        non_chinese = len(self.content) - chinese_chars
        
        return int(chinese_chars * 1.5 + non_chinese / 4)
    
    def is_long(self, threshold: int = 1000) -> bool:
        """判断是否为长消息"""
        return len(self.content) > threshold
    
    def extract_keywords(self, num_keywords: int = 5) -> List[str]:
        """提取关键词（简单实现）"""
        import re
        
        # 简单的关键词提取：移除标点，分割，去重
        words = re.findall(r'\w+', self.content)
        # 过滤停用词（这里只是示例）
        stopwords = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你'}
        words = [w for w in words if len(w) > 1 and w not in stopwords]
        
        # 计算词频
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # 按频率排序
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, freq in sorted_words[:num_keywords]]