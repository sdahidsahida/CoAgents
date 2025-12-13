#!/usr/bin/env python
"""
简单的工具集成验证测试
"""

import sys
import os

# 添加项目根目录到path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 测试导入
try:
    from framework.tools import tool_manager
    print("✓ 成功导入 tool_manager")
except ImportError as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)

# 测试八字工具
print("\n1. 测试八字工具...")
try:
    bazi_result = tool_manager.calculate(
        tool_type="bazi",
        year=1990,
        month=5,
        day=15,
        hour=14,
        gender="男"
    )
    
    if bazi_result.get("success"):
        print(f"✓ 八字计算成功")
        print(f"  出生时间: {bazi_result.get('birth_time')}")
        print(f"  四柱: {bazi_result.get('bazi_pillars')}")
        
        # 测试格式化
        bazi_prompt = tool_manager.format_for_prompt("bazi", bazi_result)
        print(f"  Prompt长度: {len(bazi_prompt)} 字符")
    else:
        print(f"✗ 八字计算失败: {bazi_result.get('error')}")
except Exception as e:
    print(f"✗ 八字测试出错: {e}")

# 测试紫微斗数工具
print("\n2. 测试紫微斗数工具...")
try:
    ziwei_result = tool_manager.calculate(
        tool_type="ziwei",
        year=2000,
        month=8,
        day=16,
        hour=2,
        gender="女"
    )
    
    if ziwei_result.get("success"):
        print(f"✓ 紫微斗数计算成功")
        print(f"  命宫主星: {ziwei_result.get('soul_palace', {}).get('star')}")
        print(f"  身宫主星: {ziwei_result.get('body_palace', {}).get('star')}")
        
        # 测试格式化
        ziwei_prompt = tool_manager.format_for_prompt("ziwei", ziwei_result)
        print(f"  Prompt长度: {len(ziwei_prompt)} 字符")
    else:
        print(f"✗ 紫微斗数计算失败: {ziwei_result.get('error')}")
except Exception as e:
    print(f"✗ 紫微斗数测试出错: {e}")

# 测试占星工具
print("\n3. 测试占星工具...")
try:
    astrology_result = tool_manager.calculate(
        tool_type="astrology",
        year=2024,
        month=6,
        day=21,
        hour=12,
        location={"lat": "51n30", "lon": "0w07"}  # 伦敦
    )
    
    if astrology_result.get("success"):
        print(f"✓ 占星计算成功")
        planets = astrology_result.get("planets", {})
        print(f"  太阳位置: {planets.get('太阳', {}).get('sign')}")
        print(f"  月亮位置: {planets.get('月亮', {}).get('sign')}")
        
        # 测试格式化
        astrology_prompt = tool_manager.format_for_prompt("astrology", astrology_result)
        print(f"  Prompt长度: {len(astrology_prompt)} 字符")
    else:
        print(f"✗ 占星计算失败: {astrology_result.get('error')}")
except Exception as e:
    print(f"✗ 占星测试出错: {e}")

# 测试全部工具调用
print("\n4. 测试全部工具调用...")
try:
    all_results = tool_manager.calculate_all(
        year=1990,
        month=5,
        day=15,
        hour=14,
        gender="男",
        location={"lat": "39n54", "lon": "116e23"}  # 北京
    )
    
    successful_tools = all_results.get("summary", {}).get("successful_tools", [])
    print(f"✓ 成功运行的工具: {successful_tools}")
    print(f"  八字: {'✓' if all_results.get('bazi', {}).get('success') else '✗'}")
    print(f"  紫微: {'✓' if all_results.get('ziwei', {}).get('success') else '✗'}")
    print(f"  占星: {'✓' if all_results.get('astrology', {}).get('success') else '✗'}")
except Exception as e:
    print(f"✗ 全部工具测试出错: {e}")

print("\n" + "=" * 80)
print("工具集成验证完成！")
print("=" * 80)