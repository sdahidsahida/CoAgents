"""
位置信息值对象
"""

from dataclasses import dataclass
from typing import Optional, Tuple
import re

from ..exceptions import ValidationError


@dataclass(frozen=True)
class Location:
    """位置信息值对象"""
    latitude: float
    longitude: float
    name: Optional[str] = None
    
    def __post_init__(self):
        """验证位置信息"""
        self._validate_coordinates()
    
    def _validate_coordinates(self) -> None:
        """验证坐标有效性"""
        if not (-90 <= self.latitude <= 90):
            raise ValidationError(
                "latitude", 
                self.latitude, 
                "must be between -90 and 90 degrees"
            )
        
        if not (-180 <= self.longitude <= 180):
            raise ValidationError(
                "longitude", 
                self.longitude, 
                "must be between -180 and 180 degrees"
            )
    
    @classmethod
    def from_string(cls, lat_str: str, lon_str: str, name: Optional[str] = None) -> "Location":
        """从字符串创建位置对象
        
        Args:
            lat_str: 纬度字符串，格式如 "39n54" (北纬39度54分)
            lon_str: 经度字符串，格式如 "116e23" (东经116度23分)
            name: 位置名称
        
        Returns:
            Location对象
        """
        lat = cls._parse_coordinate(lat_str, "latitude")
        lon = cls._parse_coordinate(lon_str, "longitude")
        
        return cls(latitude=lat, longitude=lon, name=name)
    
    @staticmethod
    def _parse_coordinate(coord_str: str, coord_type: str) -> float:
        """解析坐标字符串
        
        支持格式：
        - 度分格式：39n54 (北纬39度54分), 116e23 (东经116度23分)
        - 十进制格式：39.9042, 116.4074
        """
        try:
            # 检查是否是度分格式
            match = re.match(r'^(\d+)([nsewNSew])(\d+)$', coord_str.strip())
            if match:
                degrees = int(match.group(1))
                direction = match.group(2).upper()
                minutes = int(match.group(3))
                
                # 转换为十进制
                decimal = degrees + minutes / 60
                
                # 根据方向确定正负
                if coord_type == "latitude":
                    if direction == 'S':
                        decimal = -decimal
                else:  # longitude
                    if direction == 'W':
                        decimal = -decimal
                
                return decimal
            else:
                # 尝试解析为十进制
                return float(coord_str.strip())
                
        except ValueError:
            raise ValidationError(
                coord_type,
                coord_str,
                "invalid coordinate format. Use format like '39n54' or '39.9042'"
            )
    
    @classmethod
    def from_degrees_minutes(
        cls, 
        lat_deg: int, 
        lat_min: float, 
        lat_dir: str,
        lon_deg: int, 
        lon_min: float, 
        lon_dir: str,
        name: Optional[str] = None
    ) -> "Location":
        """从度分创建位置对象
        
        Args:
            lat_deg: 纬度度数
            lat_min: 纬度分数
            lat_dir: 纬度方向 (N/S)
            lon_deg: 经度度数
            lon_min: 经度分数
            lon_dir: 经度方向 (E/W)
            name: 位置名称
        """
        lat = lat_deg + lat_min / 60
        if lat_dir.upper() == 'S':
            lat = -lat
        
        lon = lon_deg + lon_min / 60
        if lon_dir.upper() == 'W':
            lon = -lon
        
        return cls(latitude=lat, longitude=lon, name=name)
    
    def to_string(self, format_type: str = "decimal") -> Tuple[str, str]:
        """转换为字符串
        
        Args:
            format_type: 格式类型 ("decimal" 或 "degrees")
            
        Returns:
            (纬度字符串, 经度字符串)
        """
        if format_type == "decimal":
            return (str(self.latitude), str(self.longitude))
        
        elif format_type == "degrees":
            # 转换为度分格式
            lat_abs = abs(self.latitude)
            lat_deg = int(lat_abs)
            lat_min = (lat_abs - lat_deg) * 60
            lat_dir = 'N' if self.latitude >= 0 else 'S'
            
            lon_abs = abs(self.longitude)
            lon_deg = int(lon_abs)
            lon_min = (lon_abs - lon_deg) * 60
            lon_dir = 'E' if self.longitude >= 0 else 'W'
            
            lat_str = f"{lat_deg}{lat_dir}{lat_min:.0f}"
            lon_str = f"{lon_deg}{lon_dir}{lon_min:.0f}"
            
            return (lat_str, lon_str)
        
        else:
            raise ValidationError("format_type", format_type, "must be 'decimal' or 'degrees'")
    
    def get_timezone_offset(self) -> Optional[float]:
        """获取时区偏移（粗略估算）
        
        Returns:
            时区偏移小时数，基于经度计算
        """
        # 每15度大约对应1小时时差
        offset = self.longitude / 15
        # 四舍五入到最近的0.5小时
        return round(offset * 2) / 2
    
    def distance_to(self, other: "Location") -> float:
        """计算到另一个位置的距离（公里）
        
        使用Haversine公式计算球面距离
        """
        from math import radians, sin, cos, sqrt, atan2
        
        # 地球半径（公里）
        R = 6371
        
        lat1, lon1 = radians(self.latitude), radians(self.longitude)
        lat2, lon2 = radians(other.latitude), radians(other.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c