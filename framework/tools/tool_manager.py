"""
工具管理器
统一管理所有算命工具的调用
"""

from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import logging
import json

from .bazi_tool import calculate_bazi, format_bazi_for_prompt
from .ziwei_tool import calculate_ziwei, format_ziwei_for_prompt
from .astrology_tool import calculate_astrology_chart, format_astrology_for_prompt

logger = logging.getLogger(__name__)


class ToolManager:
    """工具管理器类，负责管理所有算命工具的调用"""
    
    def __init__(self):
        """初始化工具管理器"""
        self.tools = {
            "bazi": {
                "name": "八字算命",
                "calculate": calculate_bazi,
                "format": format_bazi_for_prompt,
                "description": "基于生辰八字的命理分析"
            },
            "ziwei": {
                "name": "紫微斗数",
                "calculate": calculate_ziwei,
                "format": format_ziwei_for_prompt,
                "description": "基于紫微斗数排盘的命理分析"
            },
            "astrology": {
                "name": "西方占星",
                "calculate": calculate_astrology_chart,
                "format": format_astrology_for_prompt,
                "description": "基于西方占星术的星盘分析"
            }
        }
    
    def calculate(
        self,
        tool_type: str,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int = 0,
        gender: str = "女",
        location: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        调用指定的工具进行计算
        
        Args:
            tool_type: 工具类型 ("bazi", "ziwei", "astrology")
            year: 出生年份
            month: 出生月份
            day: 出生日期
            hour: 出生小时
            minute: 出生分钟
            gender: 性别
            location: 出生地点（仅占星需要）
            
        Returns:
            计算结果字典
        """
        if tool_type not in self.tools:
            return {
                "success": False,
                "error": f"未知的工具类型: {tool_type}"
            }
        
        try:
            # 记录调用信息
            logger.info(f"Calling {tool_type} tool for {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}")
            
            # 调用对应的计算函数
            calculate_func = self.tools[tool_type]["calculate"]
            
            if tool_type == "astrology":
                # 占星需要位置信息
                result = calculate_func(year, month, day, hour, minute, location or {"lat": "39n54", "lon": "116e23"})
            elif tool_type == "bazi":
                # 八字需要所有参数
                result = calculate_func(year, month, day, hour, minute, gender)
            else:
                # 紫微只需要基本参数
                result = calculate_func(year, month, day, hour, gender)
            
            # 记录结果
            if result.get("success"):
                logger.info(f"{tool_type} calculation completed successfully")
            else:
                logger.error(f"{tool_type} calculation failed: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error calling {tool_type} tool: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def format_for_prompt(self, tool_type: str, data: Dict[str, Any]) -> str:
        """
        将计算结果格式化为适合prompt的文本
        
        Args:
            tool_type: 工具类型
            data: 计算结果
            
        Returns:
            格式化后的文本
        """
        if tool_type not in self.tools:
            return f"未知的工具类型: {tool_type}"
        
        format_func = self.tools[tool_type]["format"]
        return format_func(data)
    
    def calculate_all(
        self,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int = 0,
        gender: str = "女",
        location: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        调用所有工具进行计算
        
        Args:
            year: 出生年份
            month: 出生月份
            day: 出生日期
            hour: 出生小时
            minute: 出生分钟
            gender: 性别
            location: 出生地点
            
        Returns:
            包含所有工具结果的字典
        """
        results = {}
        
        for tool_type in self.tools.keys():
            results[tool_type] = self.calculate(
                tool_type=tool_type,
                year=year,
                month=month,
                day=day,
                hour=hour,
                minute=minute,
                gender=gender,
                location=location
            )
        
        # 添加总体信息
        results["summary"] = {
            "birth_info": {
                "year": year,
                "month": month,
                "day": day,
                "hour": hour,
                "minute": minute,
                "gender": gender,
                "location": location or {"lat": "39n54", "lon": "116e23"}
            },
            "successful_tools": [t for t, r in results.items() if r.get("success")]
        }
        
        return results
    
    def get_tool_info(self, tool_type: str) -> Optional[Dict[str, str]]:
        """
        获取工具信息
        
        Args:
            tool_type: 工具类型
            
        Returns:
            工具信息字典
        """
        return self.tools.get(tool_type)
    
    def list_tools(self) -> Dict[str, Dict[str, str]]:
        """
        列出所有可用工具
        
        Returns:
            工具列表字典
        """
        return {
            tool_type: {
                "name": info["name"],
                "description": info["description"]
            }
            for tool_type, info in self.tools.items()
        }


# 创建全局工具管理器实例
tool_manager = ToolManager()


def extract_birth_info(text: str) -> Optional[Tuple[int, int, int, int, int, str]]:
    """
    从文本中提取出生信息
    
    Args:
        text: 包含出生信息的文本
        
    Returns:
        (year, month, day, hour, minute, gender) 或 None
    """
    import re
    
    # 匹配日期格式
    date_patterns = [
        r'(\d{4})[年\-/](\d{1,2})[月\-/](\d{1,2})日?',
        r'(\d{4})-(\d{1,2})-(\d{1,2})',
    ]
    
    # 匹配时间格式
    time_patterns = [
        r'(\d{1,2})[点时](\d{0,2})分?',
        r'(\d{1,2}):(\d{0,2})',
    ]
    
    # 匹配性别
    gender_patterns = [
        r'(男|女)'
    ]
    
    year = month = day = hour = minute = gender = None
    
    # 提取日期
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            year, month, day = map(int, match.groups())
            break
    
    # 提取时间
    for pattern in time_patterns:
        match = re.search(pattern, text)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2)) if match.group(2) else 0
            break
    
    # 提取性别
    for pattern in gender_patterns:
        match = re.search(pattern, text)
        if match:
            gender = match.group(1)
            break
    
    # 如果都有值，返回
    if all([year, month, day, hour is not None, gender]):
        return year, month, day, hour, minute, gender
    
    return None