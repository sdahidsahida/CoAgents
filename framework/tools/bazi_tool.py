"""
八字计算工具包装器
提供八字排盘功能的统一接口
"""

import os
import sys
import subprocess
import json
import re

from typing import Dict, Any, Optional
from datetime import datetime

# 添加bazi库路径
BAZI_PATH = os.path.join(os.path.dirname(__file__), '../../lib/bazi')


def calculate_bazi(year: int, month: int, day: int, hour: int, minute: int = 0, gender: str = "女") -> Dict[str, Any]:
    """
    计算八字排盘
    
    Args:
        year: 出生年份
        month: 出生月份
        day: 出生日期
        hour: 出生小时
        minute: 出生分钟（默认为0）
        gender: 性别（男/女）
        
    Returns:
        包含八字排盘结果的字典
    """
    try:
        # 构建命令
        cmd = [
            sys.executable,
            os.path.join(BAZI_PATH, "bazi.py"),
            "-g",  # 关键：公历
            str(year), str(month), str(day), str(hour)
        ]
        # 女命可选：如果 bazi.py 支持 -n
        if str(gender).strip() in ("女", "F", "f", "female"):
            cmd.insert(2, "-n")

        # 执行bazi计算
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=BAZI_PATH
        )
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": result.stderr,
                "raw_output": result.stdout
            }
        
        # 解析输出
        output_lines = result.stdout.split('\n')
        
        # 提取关键信息
        bazi_data = {
            "success": True,
            "gender": gender,
            "birth_time": f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}",
            "lunar_date": None,
            "bazi_pillars": {
                "year": None,
                "month": None,
                "day": None,
                "hour": None
            },
            "elements": {},
            "palaces": {},
            "analysis": {},
            "raw_output": result.stdout
        }

        # 解析八字四柱 + 农历日期
        for line in output_lines:
            if "公历:" in line and "农历:" in line:
                parts = line.split("农历:")
                if len(parts) > 1:
                    bazi_data["lunar_date"] = parts[1].split()[0]

            # 直接抓 “四柱：壬午 戊申 乙卯 壬午” 这种输出
            if "四柱" in line:
                m = re.search(
                    r"四柱[:：]\s*"
                    r"([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])\s+"
                    r"([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])\s+"
                    r"([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])\s+"
                    r"([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])",
                    line
                )
                if m:
                    bazi_data["bazi_pillars"]["year"] = m.group(1)
                    bazi_data["bazi_pillars"]["month"] = m.group(2)
                    bazi_data["bazi_pillars"]["day"] = m.group(3)
                    bazi_data["bazi_pillars"]["hour"] = m.group(4)
                    break  # 找到就退出循环，避免后面误覆盖

        # 解析五行
        for line in output_lines:
            if "金:" in line and "木:" in line and "水:" in line:
                # 提取五行分数
                elements = {}
                parts = line.split()
                for part in parts:
                    if "金:" in part:
                        elements["金"] = part.split("金:")[1]
                    elif "木:" in part:
                        elements["木"] = part.split("木:")[1]
                    elif "水:" in part:
                        elements["水"] = part.split("水:")[1]
                    elif "火:" in part:
                        elements["火"] = part.split("火:")[1]
                    elif "土:" in part:
                        elements["土"] = part.split("土:")[1]
                bazi_data["elements"] = elements
        
        # 解析神煞
        shensha = []
        for line in output_lines:
            if any(shen in line for shen in ["华盖", "天乙", "桃花", "将星", "孤辰", "劫煞"]):
                # 提取神煞名称
                for shen in ["华盖", "天乙", "桃花", "将星", "孤辰", "劫煞", "文昌", "文曲", "天德", "月德"]:
                    if shen in line and shen not in shensha:
                        shensha.append(shen)
        bazi_data["shensha"] = shensha
        
        # 解析大运
        dayun = []
        for line in output_lines:
            if "岁" in line and "大运:" in line:
                # 提取大运信息
                dayun.append(line.strip())
        bazi_data["dayun"] = dayun
        
        return bazi_data
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Calculation timeout",
            "raw_output": ""
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "raw_output": ""
        }


def format_bazi_for_prompt(bazi_data: Dict[str, Any]) -> str:
    """
    将八字数据格式化为适合prompt的文本
    
    Args:
        bazi_data: 八字计算结果
        
    Returns:
        格式化后的文本
    """
    if not bazi_data.get("success"):
        return f"八字计算失败：{bazi_data.get('error', '未知错误')}"
    
    prompt_text = f"""
=== 八字排盘结果 ===
性别：{bazi_data.get('gender')}
出生时间：{bazi_data.get('birth_time')}
农历日期：{bazi_data.get('lunar_date', '未知')}

四柱：
年柱：{bazi_data['bazi_pillars']['year']}
月柱：{bazi_data['bazi_pillars']['month']}
日柱：{bazi_data['bazi_pillars']['day']}
时柱：{bazi_data['bazi_pillars']['hour']}

五行分析：
{json.dumps(bazi_data.get('elements', {}), ensure_ascii=False, indent=2)}

神煞：
{', '.join(bazi_data.get('shensha', []))}

请基于以上八字排盘结果进行分析...
"""
    
    return prompt_text.strip()