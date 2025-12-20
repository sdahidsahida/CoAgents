# 快速启动指南

## 1. 安装依赖

首先确保已安装所有依赖：

```bash
pip install -r requirements.txt
```

主要依赖包括：
- `fastapi`: Web框架
- `uvicorn`: ASGI服务器
- `requests`: HTTP客户端（用于测试）

## 2. 配置环境变量（如果需要）

确保已配置 `config/.env` 文件，包含必要的API密钥：

```bash
# 创建配置文件（如果不存在）
mkdir -p config
cat > config/.env << EOF
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
EOF
```

## 3. 启动API服务

### 方式1：使用启动脚本（推荐）

```bash
python api/run.py
```

### 方式2：直接使用uvicorn

```bash
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
```

启动成功后，你会看到类似输出：

```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## 4. 访问API文档

服务启动后，在浏览器中访问：

- **Swagger UI（交互式文档）**: http://localhost:8000/docs
- **ReDoc（文档）**: http://localhost:8000/redoc

## 5. 测试API

### 方式1：使用测试脚本（推荐）

```bash
python api/test_api.py
```

这会运行一系列自动化测试，包括：
- 健康检查
- 根路径测试
- 参数验证测试
- 最小化请求测试
- 完整分析测试

### 方式2：使用curl命令

#### 健康检查
```bash
curl http://localhost:8000/health
```

#### 命理分析
```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "year": "2002",
    "month": "5",
    "day": "15",
    "hour": "14",
    "minute": "00",
    "gender": "man",
    "location": {
      "lat": "39n54",
      "lon": "116e23"
    }
  }'
```

### 方式3：使用Python requests

```python
import requests
import json

url = "http://localhost:8000/api/v1/analyze"
data = {
    "year": "2002",
    "month": "5",
    "day": "15",
    "hour": "14",
    "minute": "00",
    "gender": "man",
    "location": {
        "lat": "39n54",
        "lon": "116e23"
    }
}

response = requests.post(url, json=data)
print(json.dumps(response.json(), ensure_ascii=False, indent=2))
```

### 方式4：在Swagger UI中测试

1. 访问 http://localhost:8000/docs
2. 找到 `/api/v1/analyze` 端点
3. 点击 "Try it out"
4. 填写请求参数
5. 点击 "Execute"

## 6. 请求参数说明

### 必填参数

- `year`: 出生年份（4位数字，如："2002"）
- `month`: 出生月份（1-12，如："5" 或 "05"）
- `day`: 出生日期（1-31，如："15" 或 "05"）
- `hour`: 出生小时（0-23，如："14" 或 "06"）
- `gender`: 性别（"man" 或 "woman"）

### 可选参数

- `minute`: 出生分钟（0-59，默认为"00"）
- `location`: 出生地点（占星需要）
  ```json
  {
    "lat": "39n54",  // 纬度，格式：度+方向+分
    "lon": "116e23"  // 经度，格式：度+方向+分
  }
  ```
- `model`: 使用的模型名称（默认："deepseek-chat"）

## 7. 响应格式

成功响应示例：

```json
{
  "success": true,
  "message": "分析完成",
  "reports": {
    "bazi": {
      "content": "八字命理分析报告...",
      "total_tokens": 1500,
      "elapsed_time": 3.5
    },
    "ziwei": {
      "content": "紫微斗数分析报告...",
      "total_tokens": 1800,
      "elapsed_time": 4.2
    },
    "xingpan": {
      "content": "星盘占星分析报告...",
      "total_tokens": 1600,
      "elapsed_time": 3.8
    }
  },
  "statistics": {
    "total_tokens": 15000,
    "total_time": 35.5,
    "layers": {
      "layer1": {"tokens": 5000, "time": 12.0},
      "layer2": {"tokens": 5000, "time": 11.5},
      "layer3": {"tokens": 5000, "time": 12.0}
    }
  },
  "error": null
}
```

## 8. 常见问题

### Q: 服务启动失败，提示端口被占用？

A: 修改端口：
```bash
export API_PORT=8080
python api/run.py
```

或直接指定：
```bash
uvicorn api.app:app --host 0.0.0.0 --port 8080
```

### Q: 请求超时？

A: 命理分析需要调用LLM，可能需要30-60秒。可以增加超时时间：
```python
response = requests.post(url, json=data, timeout=300)  # 5分钟
```

### Q: 如何查看日志？

A: 日志会输出到控制台。如果需要保存到文件，可以重定向：
```bash
python api/run.py > api.log 2>&1
```

### Q: 如何停止服务？

A: 在运行服务的终端按 `Ctrl+C`

## 9. 下一步

- 查看完整API文档：`api/README.md`
- 查看项目结构：`PROJECT_STRUCTURE.md`
- 查看工具集成指南：`TOOLS_INTEGRATION_GUIDE.md`


