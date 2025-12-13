# 新项目架构设计

## 整体架构原则

1. **依赖倒置**：高层模块不依赖低层模块，都依赖抽象
2. **单一职责**：每个类只有一个改变的理由
3. **开闭原则**：对扩展开放，对修改关闭
4. **接口隔离**：使用小而专一的接口
5. **依赖注入**：通过容器管理依赖关系

## 目录结构

```
project/
├── src/                              # 源代码目录
│   ├── core/                         # 核心领域层
│   │   ├── domain/                   # 领域模型
│   │   │   ├── models/              # 领域模型
│   │   │   │   ├── birth_info.py    # 出生信息值对象
│   │   │   │   ├── chart.py         # 命盘实体
│   │   │   │   └── analysis.py      # 分析结果实体
│   │   │   ├── services/            # 领域服务
│   │   │   │   ├── chart_service.py # 命盘服务接口
│   │   │   │   └── validation.py    # 验证服务
│   │   │   └── repositories/        # 仓储接口
│   │   │       └── analysis_repo.py # 分析结果仓储接口
│   │   ├── ports/                   # 端口（接口）
│   │   │   ├── llm/                # LLM端口
│   │   │   │   └── provider.py      # LLM提供商接口
│   │   │   ├── tools/              # 工具端口
│   │   │   │   └── calculator.py   # 算命工具接口
│   │   │   └── storage/            # 存储端口
│   │   │       └── cache.py        # 缓存接口
│   │   └── shared/                 # 共享内核
│   │       ├── value_objects/      # 值对象
│   │       ├── exceptions/         # 异常定义
│   │       └── utils/              # 工具函数
│   ├── infrastructure/              # 基础设施层
│   │   ├── llm/                   # LLM实现
│   │   │   ├── deepseek_client.py # DeepSeek实现
│   │   │   ├── gemini_client.py  # Gemini实现
│   │   │   └── factory.py        # 客户端工厂
│   │   ├── tools/                 # 算命工具实现
│   │   │   ├── bazi/             # 八字工具
│   │   │   ├── ziwei/            # 紫微工具
│   │   │   └── astrology/        # 占星工具
│   │   ├── storage/              # 存储实现
│   │   │   ├── redis_cache.py    # Redis缓存
│   │   │   └── file_storage.py   # 文件存储
│   │   └── external/             # 外部服务
│   │       └── http_client.py    # HTTP客户端
│   ├── application/              # 应用层
│   │   ├── services/            # 应用服务
│   │   │   ├── moa_service.py   # MOA分析服务
│   │   │   ├── chart_service.py # 命盘服务
│   │   │   └── report_service.py # 报告服务
│   │   ├── use_cases/           # 用例
│   │   │   ├── analyze_birth.py # 分析用例
│   │   │   └── generate_report.py # 生成报告用例
│   │   └── commands/            # 命令模式
│   │       ├── analyze_command.py
│   │       └── base_command.py
│   ├── interfaces/              # 接口层
│   │   ├── api/                 # REST API
│   │   │   ├── routes/
│   │   │   └── middleware/
│   │   ├── cli/                 # 命令行接口
│   │   │   └── commands/
│   │   └── grpc/                # gRPC接口
│   └── config/                  # 配置
│       ├── settings/            # 环境配置
│       │   ├── development.py
│       │   ├── production.py
│       │   └── test.py
│       ├── ioc/                 # IoC容器
│       │   └── container.py
│       └── dependencies.py      # 依赖注入
├── tests/                       # 测试目录
│   ├── unit/                    # 单元测试
│   ├── integration/             # 集成测试
│   ├── e2e/                     # 端到端测试
│   └── fixtures/                # 测试数据
├── docs/                        # 文档
├── scripts/                     # 脚本
└── requirements/                # 依赖管理
    ├── base.txt
    ├── dev.txt
    └── prod.txt
```

## 核心设计模式

### 1. 依赖注入容器
```python
from src.config.ioc import container

# 注册依赖
container.register('llm_provider', DeepSeekClient, factory=deepseek_factory)
container.register('chart_service', ChartService)

# 解析依赖
llm_provider = container.resolve('llm_provider')
```

### 2. 仓储模式
```python
# 接口定义在领域层
class AnalysisRepository(ABC):
    @abstractmethod
    def save(self, analysis: Analysis) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, id: str) -> Optional[Analysis]:
        pass

# 实现在基础设施层
class RedisAnalysisRepository(AnalysisRepository):
    def save(self, analysis: Analysis) -> None:
        # Redis实现
        pass
```

### 3. 策略模式
```python
# LLM提供商策略
class LLMProviderStrategy(ABC):
    @abstractmethod
    def chat(self, messages: List[Message]) -> Response:
        pass

class DeepSeekStrategy(LLMProviderStrategy):
    def chat(self, messages: List[Message]) -> Response:
        # DeepSeek实现
        pass
```

### 4. 工厂模式
```python
# 命盘工厂
class ChartFactory:
    @staticmethod
    def create(chart_type: str, birth_info: BirthInfo) -> Chart:
        if chart_type == "bazi":
            return BaziChartFactory.create(birth_info)
        elif chart_type == "ziwei":
            return ZiweiChartFactory.create(birth_info)
        # ...
```

### 5. 命令查询职责分离（CQRS）
```python
# 命令端
class AnalyzeBirthCommandHandler:
    def handle(self, command: AnalyzeBirthCommand) -> AnalysisResult:
        # 处理分析命令
        pass

# 查询端
class AnalysisQueryHandler:
    def find_by_id(self, query: FindAnalysisQuery) -> Optional[Analysis]:
        # 查询分析结果
        pass
```

## 核心接口设计

### 1. LLM提供商接口
```python
from abc import ABC, abstractmethod
from typing import List, Optional
from src.core.shared.value_objects.message import Message
from src.core.shared.value_objects.response import LLMResponse

class LLMProvider(ABC):
    """LLM提供商接口"""
    
    @abstractmethod
    async def chat(
        self, 
        messages: List[Message], 
        **kwargs
    ) -> LLMResponse:
        """聊天接口"""
        pass
    
    @abstractmethod
    async def chat_stream(
        self, 
        messages: List[Message], 
        **kwargs
    ) -> AsyncIterator[str]:
        """流式聊天接口"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> ModelInfo:
        """获取模型信息"""
        pass
```

### 2. 算命工具接口
```python
from abc import ABC, abstractmethod
from src.core.domain.models.birth_info import BirthInfo
from src.core.domain.models.chart import Chart

class AstrologyTool(ABC):
    """算命工具接口"""
    
    @abstractmethod
    async def calculate(self, birth_info: BirthInfo) -> Chart:
        """计算命盘"""
        pass
    
    @abstractmethod
    def get_tool_name(self) -> str:
        """获取工具名称"""
        pass
    
    @abstractmethod
    def validate_input(self, birth_info: BirthInfo) -> ValidationResult:
        """验证输入"""
        pass
```

### 3. 配置接口
```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class ConfigProvider(ABC):
    """配置提供者接口"""
    
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        pass
    
    @abstractmethod
    def get_section(self, section: str) -> Dict[str, Any]:
        """获取配置节"""
        pass
    
    @abstractmethod
    def reload(self) -> None:
        """重新加载配置"""
        pass
```

## 值对象设计

### 1. 出生信息值对象
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class BirthInfo:
    """出生信息值对象"""
    year: int
    month: int
    day: int
    hour: int
    minute: int
    gender: Gender  # 枚举
    location: Optional[Location] = None
    
    def __post_init__(self):
        self.validate()
    
    def validate(self) -> None:
        """验证数据有效性"""
        if not (1900 <= self.year <= 2100):
            raise ValueError("Invalid year")
        if not (1 <= self.month <= 12):
            raise ValueError("Invalid month")
        # ...
    
    def to_datetime(self) -> datetime:
        """转换为datetime对象"""
        return datetime(
            self.year, self.month, self.day, 
            self.hour, self.minute
        )
```

### 2. 性别枚举
```python
from enum import Enum

class Gender(Enum):
    MALE = "男"
    FEMALE = "女"
    
    @classmethod
    def from_string(cls, value: str) -> "Gender":
        for gender in cls:
            if gender.value == value:
                return gender
        raise ValueError(f"Invalid gender: {value}")
```

## 异常处理体系

```python
# 基础异常
class AstrologyException(Exception):
    """算命领域基础异常"""
    pass

# 具体异常
class CalculationError(AstrologyException):
    """计算错误"""
    pass

class ValidationError(AstrologyException):
    """验证错误"""
    pass

class ProviderError(AstrologyException):
    """提供商错误"""
    pass

class ConfigurationError(AstrologyException):
    """配置错误"""
    pass
```

## 测试策略

### 1. 单元测试
```python
# 使用Test Double
class MockLLMProvider(LLMProvider):
    def __init__(self, response: str):
        self.response = response
    
    async def chat(self, messages: List[Message], **kwargs) -> LLMResponse:
        return LLMResponse(content=self.response)

# 测试示例
class TestChartService(unittest.TestCase):
    def setUp(self):
        self.mock_llm = MockLLMProvider("test response")
        self.service = ChartService(self.mock_llm)
    
    def test_calculate_chart(self):
        # 测试逻辑
        pass
```

### 2. 集成测试
```python
class TestIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 使用测试数据库和配置
        cls.container = TestContainer()
    
    def test_end_to_end_analysis(self):
        # 端到端测试
        pass
```

## 部署架构

### 1. Docker化
```dockerfile
# 多阶段构建
FROM python:3.9-slim as base
# 设置工作目录
WORKDIR /app

# 构建阶段
FROM base as builder
COPY requirements/ requirements/
RUN pip install -r requirements/prod.txt

# 运行阶段
FROM base
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY src/ /app/src/
EXPOSE 8000
CMD ["gunicorn", "src.interfaces.api.app:app"]
```

### 2. Kubernetes部署
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: astrology-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: astrology-api
  template:
    spec:
      containers:
      - name: api
        image: astrology-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: CONFIG_ENV
          value: "production"
```

这个新架构的优势：
1. **高度解耦**：通过接口和依赖注入实现松耦合
2. **易于测试**：每个层都可以独立测试
3. **灵活扩展**：通过策略模式轻松添加新的提供商和工具
4. **关注分离**：每层只关心自己的职责
5. **配置灵活**：支持多环境配置
6. **错误处理**：统一的异常处理体系