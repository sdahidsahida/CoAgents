"""
MOA 三层架构使用示例

展示如何使用三层 MOA 架构进行命理分析。
"""
from framework.moa.moa_layers import MOALayers


def get_user_input():
    """获取用户输入的生日信息"""
    print("=" * 80)
    print("请输入公历生日信息")
    print("=" * 80)
    
    # 获取年份
    while True:
        year = input("\n请输入年份（如：2002）: ").strip()
        if year.isdigit() and len(year) == 4:
            break
        print("请输入4位数字的年份：")
    
    # 获取月份
    while True:
        month = input("请输入月份（1-12）: ").strip()
        if month.isdigit():
            month_num = int(month)
            if 1 <= month_num <= 12:
                # 保持用户输入格式（支持前导零）
                break
        print("请输入1-12之间的数字")
    
    # 获取日期
    while True:
        day = input("请输入日期（1-31）: ").strip()
        if day.isdigit():
            day_num = int(day)
            if 1 <= day_num <= 31:
                # 保持用户输入格式（支持前导零）
                break
        print("请输入1-31之间的数字")
    
    # 获取小时
    while True:
        hour = input("请输入小时（0-23）: ").strip()
        if hour.isdigit():
            hour_num = int(hour)
            if 0 <= hour_num <= 23:
                # 保持用户输入格式（支持前导零）
                break
        print("请输入0-23之间的数字")
    
    # 获取分钟
    while True:
        minute = input("请输入分钟（0-59）: ").strip()
        if minute.isdigit():
            minute_num = int(minute)
            if 0 <= minute_num <= 59:
                # 保持用户输入格式（支持前导零）
                break
        print("请输入0-59之间的数字")
    
    # 获取性别
    while True:
        gender = input("请输入性别（男/女）: ").strip()
        if gender in ["男", "女"]:
            break
        print("请输入：男 或 女")
    
    # 获取出生地点（可选）
    print("\n出生地点（选填，不输入则使用北京）")
    print("格式：纬度+经度，如：39n54（北纬39度54分） 116e23（东经116度23分）")
    
    lat_input = input("请输入纬度（如：39n54）: ").strip()
    lon_input = input("请输入经度（如：116e23）: ").strip()
    
    location = None
    if lat_input and lon_input:
        location = {"lat": lat_input, "lon": lon_input}
        print(f"已设置出生地点：纬度{lat_input}，经度{lon_input}")
    else:
        print("使用默认出生地点：北京")
    
    return year, month, day, hour, minute, gender, location


def main():
    """主函数"""
    # 创建 MOA 架构实例
    moa = MOALayers(model="deepseek-chat")
    
    # 获取用户输入：公历生日（年月日时分）和性别
    # 所有输入都是字符串格式，支持前导零，如 "05" 表示 5
    year, month, day, hour, minute, gender, location = get_user_input()
    
    print("=" * 80)
    print("三层 MOA 架构 - 命理分析（已集成专业算命工具）")
    print("=" * 80)
    print(f"\n用户输入：{year}年{month}月{day}日{hour}时{minute}分，性别：{gender}")
    if location:
        print(f"出生地点：纬度{location['lat']}，经度{location['lon']}")
    print()
    
    # 执行完整的三层处理流程
    # 现在每个agent会先调用对应的算命工具进行排盘
    print("正在调用算命工具进行排盘...")
    results = moa.process(
        year=year, 
        month=month, 
        day=day, 
        hour=hour, 
        minute=minute,
        gender=gender,
        location=location
    )
    
    # 获取最终报告
    final_reports = moa.get_final_reports(results)
    
    # 打印最终报告
    print("\n" + "=" * 80)
    print("最终命理分析报告（基于专业算命工具的计算结果）")
    print("=" * 80)
    print("\n说明：")
    print("- 八字报告：基于专业八字库计算的四柱、五行、神煞等")
    print("- 紫微斗数报告：基于专业紫微斗数库计算的十二宫位、星曜分布等")
    print("- 星盘报告：基于专业占星库计算的行星位置、宫位系统等")
    print()
    
    report_names = {
        'bazi': '八字命理报告',
        'ziwei': '紫微斗数报告',
        'xingpan': '星盘占星报告'
    }
    
    for report_type, content in final_reports.items():
        print(f"\n{'=' * 80}")
        print(f"{report_names[report_type]}")
        print(f"{'=' * 80}")
        print(content)
        print(f"\n报告长度: {len(content)} 字符")
        print(f"Token 统计: {results['layer3'][report_type].total_tokens}")
        print(f"耗时: {results['layer3'][report_type].elapsed_time:.2f}秒")
    
    # 打印统计信息
    print("\n" + "=" * 80)
    print("处理统计")
    print("=" * 80)
    
    total_tokens = 0
    total_time = 0
    
    for layer_name in ['layer1', 'layer2', 'layer3']:
        layer_tokens = sum(r.total_tokens for r in results[layer_name].values())
        layer_time = sum(r.elapsed_time for r in results[layer_name].values())
        total_tokens += layer_tokens
        total_time += layer_time
        
        print(f"\n{layer_name}:")
        print(f"  Token 使用: {layer_tokens}")
        print(f"  耗时: {layer_time:.2f}秒")
    
    print(f"\n总计:")
    print(f"  Token 使用: {total_tokens}")
    print(f"  总耗时: {total_time:.2f}秒")


if __name__ == "__main__":
    main()

