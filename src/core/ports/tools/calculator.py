"""
算命工具接口
定义各种算命工具的标准接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from ...shared.value_objects.birth_info import BirthInfo
from ...shared.exceptions import ValidationError, CalculationError


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    errors: Dict[str, str]
    warnings: Optional[Dict[str, str]] = None
    
    @classmethod
    def success(cls) -> "ValidationResult":
        """创建成功的验证结果"""
        return cls(is_valid=True, errors={})
    
    @classmethod
    def failure(cls, errors: Dict[str, str]) -> "ValidationResult":
        """创建失败的验证结果"""
        return cls(is_valid=False, errors=errors)
    
    def add_error(self, field: str, message: str) -> None:
        """添加错误"""
        self.errors[field] = message
        self.is_valid = False
    
    def add_warning(self, field: str, message: str) -> None:
        """添加警告"""
        if self.warnings is None:
            self.warnings = {}
        self.warnings[field] = message


@dataclass
class ChartData:
    """命盘数据基类"""
    tool_name: str
    birth_info: BirthInfo
    calculation_time: datetime
    raw_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class AstrologyTool(ABC):
    """算命工具接口"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """工具名称"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """工具描述"""
        pass
    
    @abstractmethod
    async def calculate(self, birth_info: BirthInfo) -> ChartData:
        """计算命盘
        
        Args:
            birth_info: 出生信息
            
        Returns:
            命盘数据对象
        """
        pass
    
    @abstractmethod
    def validate_input(self, birth_info: BirthInfo) -> ValidationResult:
        """验证输入数据
        
        Args:
            birth_info: 出生信息
            
        Returns:
            验证结果
        """
        pass
    
    def format_for_prompt(self, chart_data: ChartData) -> str:
        """将计算结果格式化为适合LLM的prompt
        
        Args:
            chart_data: 命盘数据
            
        Returns:
            格式化的文本
        """
        # 默认实现，子类可以重写
        return f"=== {self.name}计算结果 ===\n{str(chart_data)}"
    
    async def calculate_with_validation(self, birth_info: BirthInfo) -> ChartData:
        """带验证的计算
        
        Args:
            birth_info: 出生信息
            
        Returns:
            命盘数据对象
        """
        # 验证输入
        validation = self.validate_input(birth_info)
        if not validation.is_valid:
            raise ValidationError(
                f"{self.name}_input",
                birth_info,
                f"Validation failed: {validation.errors}"
            )
        
        try:
            # 执行计算
            return await self.calculate(birth_info)
        except Exception as e:
            raise CalculationError(self.name, str(e))
    
    def get_required_fields(self) -> Dict[str, str]:
        """获取必需的字段
        
        Returns:
            字段名和描述的字典
        """
        return {
            "year": "出生年份",
            "month": "出生月份",
            "day": "出生日期",
            "hour": "出生小时",
            "minute": "出生分钟",
            "gender": "性别"
        }
    
    def get_optional_fields(self) -> Dict[str, str]:
        """获取可选的字段
        
        Returns:
            字段名和描述的字典
        """
        return {
            "location": "出生地点（经纬度）"
        }