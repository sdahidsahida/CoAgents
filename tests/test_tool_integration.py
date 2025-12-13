"""
测试集成后的算命工具功能
"""

import pytest
import sys
import os

# 添加项目根目录到path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from framework.tools import tool_manager
from framework.moa.moa_layers import MOALayers


class TestToolIntegration:
    """测试算命工具集成功能"""
    
    def test_bazi_tool_calculation(self):
        """测试八字工具计算"""
        result = tool_manager.calculate(
            tool_type="bazi",
            year=1990,
            month=5,
            day=15,
            hour=14,
            gender="男"
        )
        
        assert result.get("success"), f"八字计算失败: {result.get('error')}"
        assert result.get("birth_time") == "1990-05-15 14:00"
        assert result.get("gender") == "男"
        assert result.get("bazi_pillars") is not None
        print(f"\n八字计算结果: {result.get('bazi_pillars')}")
    
    def test_ziwei_tool_calculation(self):
        """测试紫微斗数工具计算"""
        result = tool_manager.calculate(
            tool_type="ziwei",
            year=2000,
            month=8,
            day=16,
            hour=2,
            gender="女"
        )
        
        assert result.get("success"), f"紫微斗数计算失败: {result.get('error')}"
        assert result.get("solar_date") == "2000-08-16"
        assert result.get("gender") == "女"
        assert result.get("soul_palace") is not None
        assert result.get("body_palace") is not None
        print(f"\n紫微斗数命宫: {result.get('soul_palace', {}).get('star')}")
    
    def test_astrology_tool_calculation(self):
        """测试西方占星工具计算"""
        result = tool_manager.calculate(
            tool_type="astrology",
            year=2024,
            month=6,
            day=21,
            hour=12,
            location={"lat": "51n30", "lon": "0w07"}  # 伦敦
        )
        
        assert result.get("success"), f"占星计算失败: {result.get('error')}"
        assert result.get("birth_time") == "2024-06-21 12:00"
        assert result.get("planets") is not None
        assert result.get("angles") is not None
        assert "太阳" in result.get("planets", {})
        print(f"\n占星太阳位置: {result.get('planets', {}).get('太阳', {}).get('sign')}")
    
    def test_format_bazi_for_prompt(self):
        """测试八字结果格式化"""
        # 先计算八字
        result = tool_manager.calculate(
            tool_type="bazi",
            year=1990,
            month=5,
            day=15,
            hour=14,
            gender="男"
        )
        
        # 格式化为prompt
        prompt_text = tool_manager.format_for_prompt("bazi", result)
        
        assert "八字排盘结果" in prompt_text
        assert "四柱：" in prompt_text
        assert "五行分析：" in prompt_text
        print(f"\n八字Prompt片段: {prompt_text[:200]}...")
    
    def test_format_ziwei_for_prompt(self):
        """测试紫微斗数结果格式化"""
        # 先计算紫微斗数
        result = tool_manager.calculate(
            tool_type="ziwei",
            year=2000,
            month=8,
            day=16,
            hour=2,
            gender="女"
        )
        
        # 格式化为prompt
        prompt_text = tool_manager.format_for_prompt("ziwei", result)
        
        assert "紫微斗数排盘结果" in prompt_text
        assert "命宫主星：" in prompt_text
        assert "十二宫位" in prompt_text
        print(f"\n紫微斗数Prompt片段: {prompt_text[:200]}...")
    
    def test_format_astrology_for_prompt(self):
        """测试占星结果格式化"""
        # 先计算占星
        result = tool_manager.calculate(
            tool_type="astrology",
            year=2024,
            month=6,
            day=21,
            hour=12,
            location={"lat": "51n30", "lon": "0w07"}
        )
        
        # 格式化为prompt
        prompt_text = tool_manager.format_for_prompt("astrology", result)
        
        assert "西方占星星盘结果" in prompt_text
        assert "行星位置：" in prompt_text
        assert "四角：" in prompt_text
        print(f"\n占星Prompt片段: {prompt_text[:200]}...")
    
    def test_calculate_all_tools(self):
        """测试同时调用所有工具"""
        results = tool_manager.calculate_all(
            year=1990,
            month=5,
            day=15,
            hour=14,
            gender="男",
            location={"lat": "39n54", "lon": "116e23"}  # 北京
        )
        
        assert "bazi" in results
        assert "ziwei" in results
        assert "astrology" in results
        assert "summary" in results
        
        # 检查每个工具的结果
        for tool_type in ["bazi", "ziwei", "astrology"]:
            assert results[tool_type].get("success"), f"{tool_type}工具失败"
        
        successful_tools = results["summary"]["successful_tools"]
        assert len(successful_tools) == 3
        print(f"\n成功运行的工具: {successful_tools}")
    
    def test_moa_layers_with_tools(self):
        """测试MOA layers集成工具"""
        # 创建MOA实例（不需要实际调用LLM）
        moa = MOALayers(model="test")
        
        # 测试调用工具（模拟）
        # 由于需要实际的LLM调用，这里只测试工具调用部分
        tool_results = {}
        
        for role_type in ['bazi', 'ziwei', 'xingpan']:
            tool_type = {
                'bazi': 'bazi',
                'ziwei': 'ziwei',
                'xingpan': 'astrology'
            }[role_type]
            
            result = tool_manager.calculate(
                tool_type=tool_type,
                year=1990,
                month=5,
                day=15,
                hour=14,
                gender="男",
                location={"lat": "39n54", "lon": "116e23"}
            )
            
            tool_results[role_type] = result
            
            # 检查工具结果
            assert result.get("success"), f"{tool_type}工具计算失败"
            
            # 格式化prompt
            prompt_text = tool_manager.format_for_prompt(tool_type, result)
            assert len(prompt_text) > 100, "生成的prompt太短"
        
        print(f"\nMOA工具集成测试成功！")
        for tool_type, result in tool_results.items():
            print(f"- {tool_type}: {result.get('success')}")


if __name__ == "__main__":
    # 运行测试
    import logging
    
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    test = TestToolIntegration()
    
    print("=" * 80)
    print("测试算命工具集成")
    print("=" * 80)
    
    try:
        print("\n1. 测试八字工具...")
        test.test_bazi_tool_calculation()
        
        print("\n2. 测试紫微斗数工具...")
        test.test_ziwei_tool_calculation()
        
        print("\n3. 测试占星工具...")
        test.test_astrology_tool_calculation()
        
        print("\n4. 测试格式化功能...")
        test.test_format_bazi_for_prompt()
        test.test_format_ziwei_for_prompt()
        test.test_format_astrology_for_prompt()
        
        print("\n5. 测试全部工具调用...")
        test.test_calculate_all_tools()
        
        print("\n6. 测试MOA集成...")
        test.test_moa_layers_with_tools()
        
        print("\n" + "=" * 80)
        print("所有测试通过！✅")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()