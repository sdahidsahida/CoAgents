"""
核心异常定义
定义领域特定的异常类
"""

from typing import Optional, Any


class AstrologyException(Exception):
    """算命领域基础异常"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Any] = None):
        self.message = message
        self.error_code = error_code
        self.details = details
        super().__init__(message)
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


class ValidationError(AstrologyException):
    """数据验证错误"""
    
    def __init__(self, field: str, value: Any, reason: str):
        message = f"Validation failed for field '{field}': {reason}"
        super().__init__(message, "VALIDATION_ERROR", {"field": field, "value": value})
        self.field = field
        self.value = value


class CalculationError(AstrologyException):
    """计算错误"""
    
    def __init__(self, tool_name: str, reason: str):
        message = f"Calculation error in {tool_name}: {reason}"
        super().__init__(message, "CALCULATION_ERROR", {"tool": tool_name})
        self.tool_name = tool_name


class ProviderError(AstrologyException):
    """服务提供商错误"""
    
    def __init__(self, provider: str, message: str, status_code: Optional[int] = None):
        full_message = f"Provider '{provider}' error: {message}"
        super().__init__(full_message, "PROVIDER_ERROR", {
            "provider": provider,
            "status_code": status_code
        })
        self.provider = provider
        self.status_code = status_code


class ConfigurationError(AstrologyException):
    """配置错误"""
    
    def __init__(self, key: str, reason: str):
        message = f"Configuration error for key '{key}': {reason}"
        super().__init__(message, "CONFIG_ERROR", {"key": key})
        self.key = key


class AuthenticationError(AstrologyException):
    """认证错误"""
    
    def __init__(self, provider: str):
        message = f"Authentication failed for provider '{provider}'"
        super().__init__(message, "AUTH_ERROR", {"provider": provider})
        self.provider = provider


class RateLimitError(AstrologyException):
    """速率限制错误"""
    
    def __init__(self, provider: str, retry_after: Optional[int] = None):
        message = f"Rate limit exceeded for provider '{provider}'"
        super().__init__(message, "RATE_LIMIT_ERROR", {
            "provider": provider,
            "retry_after": retry_after
        })
        self.provider = provider
        self.retry_after = retry_after


class TimeoutError(AstrologyException):
    """超时错误"""
    
    def __init__(self, operation: str, timeout: int):
        message = f"Operation '{operation}' timed out after {timeout} seconds"
        super().__init__(message, "TIMEOUT_ERROR", {
            "operation": operation,
            "timeout": timeout
        })
        self.operation = operation
        self.timeout = timeout


class ResourceNotFoundError(AstrologyException):
    """资源未找到错误"""
    
    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} with id '{resource_id}' not found"
        super().__init__(message, "NOT_FOUND", {
            "resource_type": resource_type,
            "resource_id": resource_id
        })
        self.resource_type = resource_type
        self.resource_id = resource_id