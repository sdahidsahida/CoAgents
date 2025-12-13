# 算命工具集成使用指南

## 概述

本项目已成功将三个专业算命工具集成到MOA三层架构中，每个agent现在都有自己的专业工具支持：

- **八字Agent** → 使用 `lib/bazi` 中的八字计算工具
- **紫微斗数Agent** → 使用 `py-iztro` 库进行排盘
- **西方占星Agent** → 使用 `lib/flatlib` 进行星盘计算

## 快速开始

### 1. 运行交互式示例

```bash
python -m example.moa_example
```

这个命令会启动一个交互式程序，引导您输入：
- 出生日期和时间
- 性别
- 出生地点（可选）

程序会自动：
1. 调用对应的算命工具进行排盘
2. 将排盘结果作为背景信息
3. 通过三层MOA架构生成综合分析报告

### 2. 运行测试案例

```bash
python -m test_moa_integration
```

这个命令会运行预设的测试案例，展示完整的工具集成流程。

## 代码使用示例

### 基本用法

```python
from framework.moa.moa_layers import MOALayers

# 创建MOA实例
moa = MOALayers(model="deepseek-chat")

# 执行分析（集成工具）
results = moa.process(
    year="1990",     # 出生年份
    month="5",       # 出生月份
    day="15",        # 出生日期
    hour="14",       # 出生小时
    minute="00",     # 出生分钟
    gender="男",     # 性别
    location={       # 出生地点（可选）
        "lat": "39n54",    # 纬度
        "lon": "116e23"    # 经度
    }
)

# 获取最终报告
final_reports = moa.get_final_reports(results)

# 查看报告
print("八字报告：", final_reports['bazi'])
print("紫微斗数报告：", final_reports['ziwei'])
print("占星报告：", final_reports['xingpan'])
```

### 直接使用工具

```python
from framework.tools import tool_manager

# 使用八字工具
bazi_result = tool_manager.calculate(
    tool_type="bazi",
    year=1990,
    month=5,
    day=15,
    hour=14,
    gender="男"
)

# 格式化为prompt
bazi_prompt = tool_manager.format_for_prompt("bazi", bazi_result)
print(bazi_prompt)
```

## 工具说明

### 1. 八字工具
- **功能**：计算四柱、五行、神煞、大运等
- **依赖**：lunar-python, colorama, bidict
- **输出**：完整的八字排盘信息

### 2. 紫微斗数工具
- **功能**：计算十二宫位、星曜分布、特殊格局
- **依赖**：py-iztro
- **输出**：详细的紫微斗数星盘

### 3. 西方占星工具
- **功能**：计算行星位置、宫位系统、相位
- **依赖**：pyswisseph
- **输出**：完整的西方星盘

## 架构说明

```
用户输入（生辰信息）
    ↓
[工具调用层]
    ├─ 八字工具 ─→ 四柱、五行等
    ├─ 紫微工具 ─→ 十二宫位、星曜等
    └─ 占星工具 ─→ 星盘、相位等
    ↓
[MOA第一层] - 三个独立agent基于工具结果分析
    ↓
[MOA第二层] - 参考第一层报告进行综合分析
    ↓
[MOA第三层] - 生成最终报告
```

## 日志记录

所有分析过程都会保存在 `log/` 目录下，包括：
- 工具计算结果
- Agent的输入输出
- 中间分析过程

## 注意事项

1. **时辰转换**：紫微斗数会自动将24小时制转换为12时辰
2. **地点格式**：经纬度格式如 `39n54`（北纬39度54分）
3. **错误处理**：即使工具计算失败，agent仍会基于原始信息进行分析

## 故障排除

### 1. 如果提示缺少依赖
```bash
pip install lunar-python colorama bidict pyswisseph py-iztro
```

### 2. 如果工具计算失败
- 检查输入的日期时间是否合理
- 确认性别参数为"男"或"女"
- 查看日志文件了解详细错误信息

### 3. 查看详细日志
```bash
# 日志保存在 log/moa_layers_<timestamp>/ 目录
ls log/moa_layers_*
```

## 更新日志

- **v1.0** - 完成三个算命工具的集成
- 每个agent现在都有专业工具支持
- 支持性别和出生地点参数
- 改进的分析准确性和可信度