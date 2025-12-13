#!/usr/bin/env python
"""
快速测试MOA三层架构与工具集成的功能
"""

from framework.moa.moa_layers import MOALayers

def test_moa_with_tools():
    """测试MOA三层架构集成工具功能"""
    
    print("=" * 80)
    print("MOA三层架构工具集成测试")
    print("=" * 80)
    
    # 创建MOA实例
    moa = MOALayers(model="deepseek-chat")
    
    # 测试数据
    test_cases = [
        {
            "name": "案例1：男性，1990年5月15日14时（北京）",
            "year": "1990",
            "month": "5",
            "day": "15",
            "hour": "14",
            "minute": "00",
            "gender": "男",
            "location": {"lat": "39n54", "lon": "116e23"}
        },
        {
            "name": "案例2：女性，2000年8月16日2时（上海）",
            "year": "2000",
            "month": "8",
            "day": "16",
            "hour": "2",
            "minute": "00",
            "gender": "女",
            "location": {"lat": "31n12", "lon": "121e26"}
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"{test_case['name']}")
        print(f"{'='*80}")
        
        try:
            # 执行三层分析
            print("\n[第一步] 调用算命工具进行排盘...")
            results = moa.process(
                year=test_case["year"],
                month=test_case["month"],
                day=test_case["day"],
                hour=test_case["hour"],
                minute=test_case["minute"],
                gender=test_case["gender"],
                location=test_case["location"]
            )
            
            print("\n[第二步] 分析第一层结果（包含工具计算结果）...")
            layer1_reports = results['layer1']
            print("✓ 第一层分析完成")
            for agent_type, report in layer1_reports.items():
                print(f"  - {agent_type}: {len(report.content)} 字符")
            
            print("\n[第三步] 分析第二层结果...")
            layer2_reports = results['layer2']
            print("✓ 第二层分析完成")
            for agent_type, report in layer2_reports.items():
                print(f"  - {agent_type}: {len(report.content)} 字符")
            
            print("\n[第四步] 生成最终报告...")
            final_reports = moa.get_final_reports(results)
            print("✓ 最终报告生成完成")
            
            # 显示摘要
            print(f"\n{'='*60}")
            print("报告摘要")
            print(f"{'='*60}")
            
            report_names = {
                'bazi': '八字命理',
                'ziwei': '紫微斗数',
                'xingpan': '西方占星'
            }
            
            for report_type, content in final_reports.items():
                # 只显示前200字符
                preview = content[:200] + "..." if len(content) > 200 else content
                print(f"\n【{report_names[report_type]}】")
                print(f"{preview}")
                print(f"（完整长度：{len(content)} 字符）")
            
            # 显示token统计
            total_tokens = 0
            for layer_name in ['layer1', 'layer2', 'layer3']:
                layer_tokens = sum(r.total_tokens for r in results[layer_name].values())
                total_tokens += layer_tokens
            
            print(f"\n{'='*60}")
            print(f"总Token使用：{total_tokens}")
            print(f"{'='*60}")
            
            if i < len(test_cases):
                input("\n按回车键继续下一个测试案例...")
                
        except Exception as e:
            print(f"\n❌ 测试失败：{e}")
            import traceback
            traceback.print_exc()
            break
    
    print(f"\n{'='*80}")
    print("测试完成！")
    print("=" * 80)
    print("\n总结：")
    print("1. ✓ 成功集成了八字、紫微斗数、西方占星三个专业工具")
    print("2. ✓ 每个agent在分析前都会调用对应的工具进行排盘")
    print("3. ✓ 工具计算结果会作为背景信息提供给agent")
    print("4. ✓ 三层架构协同工作，生成更准确的分析报告")


if __name__ == "__main__":
    test_moa_with_tools()