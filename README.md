# APITest

API 测试项目，用于测试 DeepSeek API 和其他相关功能。

## 项目结构

```
APITest/
├── config/                 # 配置模块
│   ├── __init__.py
│   ├── config.py          # 全局配置类（单例模式）
│   └── config.yaml        # 配置文件
├── llm/                    # LLM 客户端模块
│   ├── __init__.py
│   ├── client.py          # LLM 客户端封装
│   └── response.py        # LLM 响应类
├── framework/              # 框架代码
│   └── moa/               # MOA (Mixture of Agents) 相关
│       ├── __init__.py
│       └── moa_layers.py  # 三层 MOA 架构
├── prompt/                 # Prompt 模板
│   ├── __init__.py
│   └── moa/               # MOA 架构相关的 Prompt
│       ├── __init__.py
│       ├── bazi.py        # 八字命理师角色（三层提示词）
│       ├── ziwei.py       # 紫微斗数命理师角色（三层提示词）
│       └── xingpan.py     # 星盘占星师角色（三层提示词）
├── tests/                  # 测试目录（标准位置）
│   ├── __init__.py
│   ├── conftest.py        # pytest 共享配置和 fixtures
│   ├── llm/               # LLM 客户端测试
│   │   └── test_client.py
│   └── framework/         # 框架测试
│       └── moa/
│           └── test_moa_layers.py
├── examples/               # 使用示例（展示实际使用场景）
│   └── moa_example.py     # MOA 架构使用示例
├── main.py                # 主程序入口
├── requirements.txt       # 项目依赖
├── pytest.ini            # pytest 配置文件
└── README.md             # 项目说明文档
```

## Tests vs Examples

### Tests（`tests/` 目录）
- **目的**：验证代码功能正确性，确保代码质量
- **特点**：
  - 使用断言验证结果
  - 快速执行，不打印详细输出
  - 测试边界情况和错误处理
  - 可以自动化运行（CI/CD）
- **运行方式**：`pytest tests/ -v`

### Examples（`examples/` 目录）
- **目的**：展示如何使用代码，作为使用文档和参考
- **特点**：
  - 展示完整的使用场景
  - 打印详细的输出，让用户看到实际效果
  - 展示最佳实践
  - 可以作为演示和教学材料
- **运行方式**：`python examples/moa_example.py`

## 安装依赖

```bash
pip install -r requirements.txt
```

## 环境配置

创建 `config/.env` 文件：

```
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

## 运行测试

### 运行所有测试

```bash
pytest
```

### 运行特定测试文件

```bash
pytest tests/llm/test_client.py
```

### 运行特定测试类或函数

```bash
pytest tests/llm/test_client.py::TestLLMClient::test_chat_basic
```

### 带详细输出

```bash
pytest -v -s
```

## 运行示例

### MOA 三层架构示例

```bash
python examples/moa_example.py
```

这将展示完整的三层 MOA 架构处理流程，包括：
- 第一层：三个独立的命理师分别分析
- 第二层：参考第一层报告的综合分析
- 第三层：参考第二层报告和用户输入的最终报告

## 开发指南

### 添加新测试

1. 在 `tests/` 目录下创建对应的测试文件
2. 测试文件命名：`test_*.py`
3. 使用 `conftest.py` 中定义的 fixtures
4. 测试目录结构应镜像源代码结构
5. **重要**：测试应该专注于验证功能，避免打印大量输出

### 添加新示例

1. 在 `examples/` 目录下创建示例文件
2. 展示完整的使用场景
3. 打印详细的输出，让用户看到实际效果
4. 包含清晰的注释和说明

### 配置管理

- 配置文件：`config/config.yaml`
- 配置类：`config/config.py`（单例模式）
- 使用方式：`from config.config import get_config`

## 最佳实践

1. **测试隔离**：每个测试应该是独立的，不依赖其他测试的执行顺序
2. **使用 Fixtures**：充分利用 pytest fixtures 来共享测试资源
3. **清晰的命名**：测试函数名应该清晰描述测试内容
4. **适当的断言**：使用有意义的断言消息
5. **测试文档**：为测试类和函数添加文档字符串
6. **区分测试和示例**：测试验证功能，示例展示使用

## 许可证

[添加许可证信息]
# CoAgents
