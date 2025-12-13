"""
性别值对象
"""

from enum import Enum
from typing import Any

from ..exceptions import ValidationError


class Gender(Enum):
    """性别枚举"""
    MALE = "男"
    FEMALE = "女"
    
    @classmethod
    def from_string(cls, value: str) -> "Gender":
        """从字符串创建性别枚举"""
        if not isinstance(value, str):
            raise ValidationError("gender", value, "must be a string")
        
        value = value.strip()
        for gender in cls:
            if gender.value == value:
                return gender
        
        raise ValidationError(
            "gender", 
            value, 
            f"must be one of: {', '.join(g.value for g in cls)}"
        )
    
    @classmethod
    def from_int(cls, value: int) -> "Gender":
        """从数字创建性别枚举"""
        if value == 1:
            return cls.MALE
        elif value == 0 or value == 2:
            return cls.FEMALE
        else:
            raise ValidationError("gender", value, "must be 0, 1, or 2")
    
    def to_int(self) -> int:
        """转换为整数表示"""
        return 1 if self == Gender.MALE else 2
    
    @property
    def pronoun(self) -> str:
        """获取代词"""
        return "他" if self == Gender.MALE else "她"
    
    @property
    def possessive(self) -> str:
        """获取物主代词"""
        return "他的" if self == Gender.MALE else "她的"