"""
西方占星（星盘）计算工具包装器
提供星盘计算功能的统一接口
"""

import sys
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# 添加flatlib库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib/flatlib'))

from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const
from flatlib.aspects import getAspect


def calculate_astrology_chart(
    year: int, 
    month: int, 
    day: int, 
    hour: int, 
    minute: int = 0,
    location: Dict[str, str] = None
) -> Dict[str, Any]:
    """
    计算西方占星星盘
    
    Args:
        year: 出生年份
        month: 出生月份
        day: 出生日期
        hour: 出生小时
        minute: 出生分钟（默认为0）
        location: 出生地点 {"lat": "纬度", "lon": "经度"}
        
    Returns:
        包含星盘计算结果的字典
    """
    try:
        # 默认位置（北京）
        if not location:
            location = {"lat": "39n54", "lon": "116e23"}
        
        # 创建日期时间对象
        date_str = f"{year}/{month:02d}/{day:02d}"
        time_str = f"{hour:02d}:{minute:02d}"
        datetime_obj = Datetime(date_str, time_str, '+08:00')
        
        # 创建地理位置对象
        pos = GeoPos(location["lat"], location["lon"])
        
        # 创建星盘
        chart = Chart(datetime_obj, pos)
        
        # 提取星体信息
        astrology_data = {
            "success": True,
            "birth_time": f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}",
            "location": location,
            "planets": {},
            "houses": {},
            "aspects": [],
            "angles": {},
            "elements": {},
            "modes": {},
            "analysis": {}
        }
        
        # 获取主要星体位置
        planets = [
            ("Sun", "太阳"),
            ("Moon", "月亮"),
            ("Mercury", "水星"),
            ("Venus", "金星"),
            ("Mars", "火星"),
            ("Jupiter", "木星"),
            ("Saturn", "土星"),
        ]
        
        # 尝试获取三王星
        try:
            planets.extend([
                ("Uranus", "天王星"),
                ("Neptune", "海王星"),
                ("Pluto", "冥王星")
            ])
        except:
            pass
        
        for planet_id, planet_name in planets:
            try:
                planet = chart.get(planet_id)
                if planet:
                    astrology_data["planets"][planet_name] = {
                        "sign": planet.sign,
                        "position": str(planet.lon),
                        "retrograde": hasattr(planet, 'retrograde') and planet.retrograde,
                        "house": None
                    }
            except Exception as e:
                logger.warning(f"Could not get planet {planet_name}: {e}")
                continue
        
        # 获取宫位信息
        for i in range(1, 13):
            house_id = f"House{i}"
            house = chart.get(house_id)
            if house:
                astrology_data["houses"][f"第{i}宫"] = {
                    "sign": house.sign,
                    "cusp": str(house.lon)
                }
        
        # 获取四角（简化版）
        try:
            asc = chart.get("Ascendant")
            if asc:
                astrology_data["angles"]["上升星座"] = {
                    "sign": asc.sign,
                    "position": str(asc.lon)
                }
        except:
            pass
        
        # 计算相位
        aspects = []
        planet_pairs = [
            ("Sun", "Moon"),
            ("Sun", "Mercury"),
            ("Sun", "Venus"),
            ("Sun", "Mars"),
            ("Sun", "Jupiter"),
            ("Sun", "Saturn"),
            ("Moon", "Mercury"),
            ("Moon", "Venus"),
            ("Moon", "Mars"),
            ("Mercury", "Venus"),
            ("Venus", "Mars"),
            ("Mars", "Jupiter"),
            ("Jupiter", "Saturn")
        ]
        
        for planet1_id, planet2_id in planet_pairs:
            planet1 = chart.get(planet1_id)
            planet2 = chart.get(planet2_id)
            if planet1 and planet2:
                aspect = getAspect(planet1, planet2, 10)  # 10度容许度
                if aspect:
                    planet1_name = next((name for pid, name in planets if pid == planet1_id), str(planet1_id))
                    planet2_name = next((name for pid, name in planets if pid == planet2_id), str(planet2_id))
                    aspects.append({
                        "planet1": planet1_name,
                        "planet2": planet2_name,
                        "aspect": aspect.name,
                        "orb": str(aspect.orb)
                    })
        
        astrology_data["aspects"] = aspects
        
        # 分析元素分布
        elements = {"火": 0, "土": 0, "风": 0, "水": 0}
        element_signs = {
            "火": ["白羊座", "狮子座", "射手座"],
            "土": ["金牛座", "处女座", "摩羯座"],
            "风": ["双子座", "天秤座", "水瓶座"],
            "水": ["巨蟹座", "天蝎座", "双鱼座"]
        }
        
        for planet_info in astrology_data["planets"].values():
            sign = planet_info["sign"]
            for element, signs in element_signs.items():
                if sign in signs:
                    elements[element] += 1
        
        astrology_data["elements"] = elements
        
        # 分析模式分布
        modes = {"基本": 0, "固定": 0, "变动": 0}
        mode_signs = {
            "基本": ["白羊座", "巨蟹座", "天秤座", "摩羯座"],
            "固定": ["金牛座", "狮子座", "天蝎座", "水瓶座"],
            "变动": ["双子座", "处女座", "射手座", "双鱼座"]
        }
        
        for planet_info in astrology_data["planets"].values():
            sign = planet_info["sign"]
            for mode, signs in mode_signs.items():
                if sign in signs:
                    modes[mode] += 1
        
        astrology_data["modes"] = modes
        
        return astrology_data
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def format_astrology_for_prompt(astrology_data: Dict[str, Any]) -> str:
    """
    将占星数据格式化为适合prompt的文本
    
    Args:
        astrology_data: 占星计算结果
        
    Returns:
        格式化后的文本
    """
    if not astrology_data.get("success"):
        return f"星盘计算失败：{astrology_data.get('error', '未知错误')}"
    
    prompt_text = f"""
=== 西方占星星盘结果 ===
出生时间：{astrology_data.get('birth_time')}
出生地点：{astrology_data.get('location')}

行星位置：
"""
    
    # 添加行星位置
    for planet_name, info in astrology_data.get("planets", {}).items():
        retrograde_text = "（逆行）" if info.get("retrograde") else ""
        prompt_text += f"\n{planet_name}：{info['sign']}{retrograde}"
    
    # 添加四角
    prompt_text += "\n\n四角："
    for angle_name, info in astrology_data.get("angles", {}).items():
        prompt_text += f"\n{angle_name}：{info['sign']}"
    
    # 添加元素分析
    elements = astrology_data.get("elements", {})
    if elements:
        prompt_text += f"\n\n元素分布：火{elements.get('火', 0)} 土{elements.get('土', 0)} 风{elements.get('风', 0)} 水{elements.get('水', 0)}"
    
    # 添加模式分析
    modes = astrology_data.get("modes", {})
    if modes:
        prompt_text += f"\n模式分布：基本{modes.get('基本', 0)} 固定{modes.get('固定', 0)} 变动{modes.get('变动', 0)}"
    
    # 添加主要相位
    aspects = astrology_data.get("aspects", [])[:10]  # 只显示前10个
    if aspects:
        prompt_text += "\n\n主要相位："
        for aspect in aspects:
            prompt_text += f"\n{aspect['planet1']}-{aspect['planet2']} {aspect['aspect']}（容许度{aspect['orb']}）"
    
    prompt_text += "\n\n请基于以上星盘结果进行分析..."
    
    return prompt_text.strip()