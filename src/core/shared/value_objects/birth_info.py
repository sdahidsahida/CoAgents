"""
出生信息值对象
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .gender import Gender
from .location import Location
from ..exceptions import ValidationError


@dataclass(frozen=True)
class BirthInfo:
    """出生信息值对象"""
    year: int
    month: int
    day: int
    hour: int
    minute: int
    gender: Gender
    location: Optional[Location] = None
    
    def __post_init__(self):
        """验证数据有效性"""
        self._validate_date()
        self._validate_time()
        self._validate_chinese_calendar()
    
    def _validate_date(self) -> None:
        """验证日期有效性"""
        if not (1900 <= self.year <= 2100):
            raise ValidationError("year", self.year, "must be between 1900 and 2100")
        
        if not (1 <= self.month <= 12):
            raise ValidationError("month", self.month, "must be between 1 and 12")
        
        if not (1 <= self.day <= 31):
            raise ValidationError("day", self.day, "must be between 1 and 31")
        
        # 验证具体日期的有效性
        try:
            datetime(self.year, self.month, self.day)
        except ValueError as e:
            raise ValidationError("date", f"{self.year}-{self.month}-{self.day}", str(e))
    
    def _validate_time(self) -> None:
        """验证时间有效性"""
        if not (0 <= self.hour <= 23):
            raise ValidationError("hour", self.hour, "must be between 0 and 23")
        
        if not (0 <= self.minute <= 59):
            raise ValidationError("minute", self.minute, "must be between 0 and 59")
    
    def _validate_chinese_calendar(self) -> None:
        """验证农历日期的合理性（简单检查）"""
        # 这里可以添加更复杂的农历验证逻辑
        # 比如检查是否在某些特殊日期等
        pass
    
    def to_datetime(self) -> datetime:
        """转换为datetime对象"""
        return datetime(
            self.year, 
            self.month, 
            self.day, 
            self.hour, 
            self.minute
        )
    
    def to_chinese_time_period(self) -> str:
        """转换为中国古代时辰"""
        # 时辰对照表
        time_periods = [
            (23, 1, "子时"),   # 23:00-01:00
            (1, 3, "丑时"),    # 01:00-03:00
            (3, 5, "寅时"),    # 03:00-05:00
            (5, 7, "卯时"),    # 05:00-07:00
            (7, 9, "辰时"),    # 07:00-09:00
            (9, 11, "巳时"),   # 09:00-11:00
            (11, 13, "午时"),  # 11:00-13:00
            (13, 15, "未时"),  # 13:00-15:00
            (15, 17, "申时"),  # 15:00-17:00
            (17, 19, "酉时"),  # 17:00-19:00
            (19, 21, "戌时"),  # 19:00-21:00
            (21, 23, "亥时"),  # 21:00-23:00
        ]
        
        for start, end, period_name in time_periods:
            if self.hour >= start or (self.hour < end and start > end):
                return period_name
        
        return "子时"  # 默认
    
    def to_zodiac_animal(self) -> str:
        """获取生肖"""
        animals = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
        # 1900年是鼠年
        offset = (self.year - 1900) % 12
        return animals[offset]
    
    def to_western_zodiac(self) -> str:
        """获取西方星座"""
        # 星座日期范围
        zodiac_dates = [
            ((3, 21), (4, 19), "白羊座"),
            ((4, 20), (5, 20), "金牛座"),
            ((5, 21), (6, 21), "双子座"),
            ((6, 22), (7, 22), "巨蟹座"),
            ((7, 23), (8, 22), "狮子座"),
            ((8, 23), (9, 22), "处女座"),
            ((9, 23), (10, 23), "天秤座"),
            ((10, 24), (11, 22), "天蝎座"),
            ((11, 23), (12, 21), "射手座"),
            ((12, 22), (1, 19), "摩羯座"),
            ((1, 20), (2, 18), "水瓶座"),
            ((2, 19), (3, 20), "双鱼座"),
        ]
        
        for (start_month, start_day), (end_month, end_day), sign in zodiac_dates:
            if (self.month == start_month and self.day >= start_day) or \
               (self.month == end_month and self.day <= end_day):
                return sign
        
        return "摩羯座"  # 默认
    
    def get_age_at(self, reference_date: datetime) -> int:
        """计算在指定日期的年龄"""
        birth = self.to_datetime()
        age = reference_date.year - birth.year
        
        # 检查是否已经过了生日
        if (reference_date.month, reference_date.day) < (birth.month, birth.day):
            age -= 1
        
        return age
    
    def get_lunar_year_string(self) -> str:
        """获取农历年份字符串（天干地支）"""
        # 天干
        heavenly_stems = ["庚", "辛", "壬", "癸", "甲", "乙", "丙", "丁", "戊", "己"]
        # 地支
        earthly_branches = ["申", "酉", "戌", "亥", "子", "丑", "寅", "卯", "辰", "巳", "午", "未"]
        
        stem_idx = (self.year - 1900) % 10
        branch_idx = (self.year - 1900) % 12
        
        return heavenly_stems[stem_idx] + earthly_branches[branch_idx]
    
    def format_string(self, style: str = "chinese") -> str:
        """格式化输出字符串
        
        Args:
            style: 输出风格 ("chinese" 或 "western")
        """
        if style == "chinese":
            time_str = f"{self.year}年{self.month}月{self.day}日{self.hour}时{self.minute}分"
            if self.location:
                lat_str, lon_str = self.location.to_string("degrees")
                time_str += f"（{self.location.name or '未知地点'}，{lat_str}，{lon_str}）"
            return time_str
        else:
            dt = self.to_datetime()
            return dt.strftime("%Y-%m-%d %H:%M")
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "hour": self.hour,
            "minute": self.minute,
            "gender": self.gender.value,
            "location": self.location.to_dict() if self.location else None,
            "time_period": self.to_chinese_time_period(),
            "zodiac": self.to_western_zodiac(),
            "chinese_zodiac": self.to_zodiac_animal(),
            "lunar_year": self.get_lunar_year_string()
        }