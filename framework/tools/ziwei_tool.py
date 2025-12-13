"""
紫微斗数计算工具包装器
提供紫微斗数排盘功能的统一接口
"""

from typing import Dict, Any, Optional
from py_iztro import Astro
import json


def calculate_ziwei(year: int, month: int, day: int, hour: int, gender: str = "女") -> Dict[str, Any]:
    """
    计算紫微斗数排盘
    
    Args:
        year: 出生年份
        month: 出生月份
        day: 出生日期
        hour: 出生小时
        gender: 性别（男/女）
        
    Returns:
        包含紫微斗数排盘结果的字典
    """
    try:
        # 创建Astro对象
        astro = Astro()
        
        # 转换为日期字符串
        date_str = f"{year}-{month:02d}-{day:02d}"
        
        # 小时必须是1-12之间的整数（代表时辰）
        # 23-2点为1点子时，以此类推
        if hour >= 23 or hour < 2:
            hour_cn = 1  # 子时
        elif hour >= 2 and hour < 4:
            hour_cn = 2  # 丑时
        elif hour >= 4 and hour < 6:
            hour_cn = 3  # 寅时
        elif hour >= 6 and hour < 8:
            hour_cn = 4  # 卯时
        elif hour >= 8 and hour < 10:
            hour_cn = 5  # 辰时
        elif hour >= 10 and hour < 12:
            hour_cn = 6  # 巳时
        elif hour >= 12 and hour < 14:
            hour_cn = 7  # 午时
        elif hour >= 14 and hour < 16:
            hour_cn = 8  # 未时
        elif hour >= 16 and hour < 18:
            hour_cn = 9  # 申时
        elif hour >= 18 and hour < 20:
            hour_cn = 10  # 酉时
        elif hour >= 20 and hour < 22:
            hour_cn = 11  # 戌时
        else:  # 22-23点
            hour_cn = 12  # 亥时
        
        # 计算紫微斗数
        result = astro.by_solar(date_str, hour_cn, gender)
        
        # 提取关键信息
        ziwei_data = {
            "success": True,
            "gender": gender,
            "birth_time": f"{year}-{month:02d}-{day:02d} {hour:02d}:00",
            "solar_date": result.solar_date,
            "lunar_date": result.lunar_date,
            "chinese_date": result.chinese_date,
            "time_range": result.time_range,
            "zodiac": result.zodiac,
            "soul_palace": {
                "palace": None,
                "branch": result.earthly_branch_of_soul_palace,
                "star": result.soul
            },
            "body_palace": {
                "palace": None,
                "branch": result.earthly_branch_of_body_palace,
                "star": result.body
            },
            "five_elements": result.five_elements_class,
            "palaces": [],
            "major_stars": {},
            "minor_stars": {},
            "analysis": {},
            "raw_json": result.model_dump_json(by_alias=False, indent=2)
        }
        
        # 解析十二宫位
        palace_names = [
            "命宫", "兄弟", "夫妻", "子女", "财帛", "疾厄",
            "迁移", "仆役", "官禄", "田宅", "福德", "父母"
        ]
        
        for i, palace in enumerate(result.palaces):
            palace_info = {
                "index": i,
                "name": palace_names[i] if i < len(palace_names) else f"宫位{i}",
                "is_body_palace": palace.is_body_palace,
                "is_soul_palace": palace.is_original_palace,
                "heavenly_stem": palace.heavenly_stem,
                "earthly_branch": palace.earthly_branch,
                "major_stars": [],
                "minor_stars": [],
                "adjective_stars": [],
                "changsheng": palace.changsheng12,
                "ages": palace.ages
            }
            
            # 收集主星
            for star in palace.major_stars:
                palace_info["major_stars"].append({
                    "name": star.name,
                    "brightness": star.brightness,
                    "mutagen": star.mutagen
                })
                # 记录主星分布
                if star.name not in ziwei_data["major_stars"]:
                    ziwei_data["major_stars"][star.name] = []
                ziwei_data["major_stars"][star.name].append({
                    "palace": palace_info["name"],
                    "brightness": star.brightness
                })
            
            # 收集辅星
            for star in palace.minor_stars:
                palace_info["minor_stars"].append({
                    "name": star.name,
                    "brightness": star.brightness
                })
                if star.name not in ziwei_data["minor_stars"]:
                    ziwei_data["minor_stars"][star.name] = []
                ziwei_data["minor_stars"][star.name].append(palace_info["name"])
            
            # 收集杂耀星
            for star in palace.adjective_stars:
                palace_info["adjective_stars"].append({
                    "name": star.name,
                    "type": star.type
                })
            
            ziwei_data["palaces"].append(palace_info)
        
        # 分析特殊格局
        ziwei_data["special_patterns"] = analyze_special_patterns(ziwei_data)
        
        return ziwei_data
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "raw_json": ""
        }


def analyze_special_patterns(ziwei_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    分析紫微斗数特殊格局
    
    Args:
        ziwei_data: 紫微斗数数据
        
    Returns:
        特殊格局分析结果
    """
    patterns = {
        "紫府同宫": False,
        "杀破狼": False,
        "机月同梁": False,
        "阳梁昌禄": False,
        "火贪格": False,
        "铃贪格": False,
        "七杀朝斗": False,
        "紫微龙池": False
    }
    
    major_stars = ziwei_data.get("major_stars", {})
    
    # 紫府同宫格
    if "紫微" in major_stars and "天府" in major_stars:
        for palace_ziwei in major_stars.get("紫微", []):
            for palace_tianfu in major_stars.get("天府", []):
                if palace_ziwei["palace"] == palace_tianfu["palace"]:
                    patterns["紫府同宫"] = True
                    break
    
    # 杀破狼格
    soul_palace = ziwei_data.get("soul_palace", {})
    if soul_palace.get("star") in ["七杀", "破军", "贪狼"]:
        patterns["杀破狼"] = True
    
    # 检查同宫的星曜组合
    for palace in ziwei_data.get("palaces", []):
        palace_major_stars = [star["name"] for star in palace.get("major_stars", [])]
        
        if "天机" in palace_major_stars and "太阴" in palace_major_stars and "天同" in palace_major_stars and "天梁" in palace_major_stars:
            patterns["机月同梁"] = True
        
        if "太阳" in palace_major_stars and "天梁" in palace_major_stars and "文曲" in palace_major_stars and "禄存" in palace_major_stars:
            patterns["阳梁昌禄"] = True
        
        if "火星" in palace_major_stars and "贪狼" in palace_major_stars:
            patterns["火贪格"] = True
        
        if "铃星" in palace_major_stars and "贪狼" in palace_major_stars:
            patterns["铃贪格"] = True
    
    return patterns


def format_ziwei_for_prompt(ziwei_data: Dict[str, Any]) -> str:
    """
    将紫微斗数数据格式化为适合prompt的文本
    
    Args:
        ziwei_data: 紫微斗数计算结果
        
    Returns:
        格式化后的文本
    """
    if not ziwei_data.get("success"):
        return f"紫微斗数计算失败：{ziwei_data.get('error', '未知错误')}"
    
    prompt_text = f"""
=== 紫微斗数排盘结果 ===
性别：{ziwei_data.get('gender')}
出生时间：{ziwei_data.get('birth_time')}
公历：{ziwei_data.get('solar_date')}
农历：{ziwei_data.get('lunar_date')}
八字：{ziwei_data.get('chinese_date')}
生肖：{ziwei_data.get('zodiac')}
时辰：{ziwei_data.get('time_range')}
五行局：{ziwei_data.get('five_elements')}

命宫主星：{ziwei_data['soul_palace']['star']}（{ziwei_data['soul_palace']['branch']}）
身宫主星：{ziwei_data['body_palace']['star']}（{ziwei_data['body_palace']['branch']}）

十二宫位主星分布：
"""
    
    # 添加十二宫位信息
    for palace in ziwei_data.get("palaces", []):
        if palace.get("major_stars"):
            major_star_names = [s["name"] for s in palace["major_stars"]]
            prompt_text += f"\n{palace['name']}：{' '.join(major_star_names)}"
    
    # 添加特殊格局
    patterns = ziwei_data.get("special_patterns", {})
    active_patterns = [name for name, active in patterns.items() if active]
    if active_patterns:
        prompt_text += f"\n\n特殊格局：{', '.join(active_patterns)}"
    
    prompt_text += "\n\n请基于以上紫微斗数排盘结果进行分析..."
    
    return prompt_text.strip()