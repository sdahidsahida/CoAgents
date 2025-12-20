# MOA 命理分析 API 使用文档

## 概述

本API提供了基于三层MOA架构的命理分析服务，集成八字、紫微斗数、星盘占星三大专业工具。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动API服务

```bash
# 方式1：使用启动脚本
python api/run.py

# 方式2：直接使用uvicorn
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 访问API文档

启动服务后，访问以下地址查看API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API 端点

### 1. 根路径

**GET** `/`

返回API基本信息。

**响应示例：**
```json
{
  "name": "MOA 命理分析 API",
  "version": "1.0.0",
  "description": "基于三层MOA架构的命理分析服务",
  "endpoints": {
    "/docs": "API文档（Swagger UI）",
    "/redoc": "API文档（ReDoc）",
    "/api/v1/analyze": "命理分析接口（POST）",
    "/health": "健康检查接口"
  }
}
```

### 2. 健康检查

**GET** `/health`

检查API服务状态。

**响应示例：**
```json
{
  "status": "healthy",
  "service": "MOA 命理分析 API"
}
```

### 3. 命理分析（主要接口）

**POST** `/api/v1/analyze`

基于用户提供的生辰信息进行命理分析。

#### 请求参数

```json
{
  "year": "2002",
  "month": "5",
  "day": "15",
  "hour": "14",
  "minute": "00",
  "gender": "男",
  "location": {
    "lat": "39n54",
    "lon": "116e23"
  },
  "model": "deepseek-chat"
}
```

**参数说明：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| year | string | 是 | 出生年份，4位数字，如：2002 |
| month | string | 是 | 出生月份，1-12，如：5 或 05 |
| day | string | 是 | 出生日期，1-31，如：15 或 05 |
| hour | string | 是 | 出生小时，0-23，如：14 或 06 |
| minute | string | 否 | 出生分钟，0-59，默认为00 |
| gender | string | 是 | 性别，男 或 女 |
| location | object | 否 | 出生地点（占星需要），格式：{"lat": "39n54", "lon": "116e23"} |
| model | string | 否 | 使用的模型名称，默认：deepseek-chat |

#### 响应示例

```json
{
  "success": true,
  "message": "分析完成",
  "reports": {
    "bazi": {
      "content": "八字命理分析报告内容...",
      "total_tokens": 1500,
      "elapsed_time": 3.5
    },
    "ziwei": {
      "content": "紫微斗数分析报告内容...",
      "total_tokens": 1800,
      "elapsed_time": 4.2
    },
    "xingpan": {
      "content": "星盘占星分析报告内容...",
      "total_tokens": 1600,
      "elapsed_time": 3.8
    }
  },
  "statistics": {
    "total_tokens": 15000,
    "total_time": 35.5,
    "layers": {
      "layer1": {
        "tokens": 5000,
        "time": 12.0
      },
      "layer2": {
        "tokens": 5000,
        "time": 11.5
      },
      "layer3": {
        "tokens": 5000,
        "time": 12.0
      }
    }
  },
  "error": null
}
```

## 使用示例

### Python 示例

```python
import requests
import json

# API地址
url = "http://localhost:8000/api/v1/analyze"

# 请求数据
data = {
    "year": "2002",
    "month": "5",
    "day": "15",
    "hour": "14",
    "minute": "00",
    "gender": "男",
    "location": {
        "lat": "39n54",
        "lon": "116e23"
    }
}

# 发送请求
response = requests.post(url, json=data)

# 处理响应
if response.status_code == 200:
    result = response.json()
    if result["success"]:
        print("分析成功！")
        print("\n八字报告：")
        print(result["reports"]["bazi"]["content"])
        print("\n紫微斗数报告：")
        print(result["reports"]["ziwei"]["content"])
        print("\n星盘报告：")
        print(result["reports"]["xingpan"]["content"])
        print(f"\n总耗时：{result['statistics']['total_time']}秒")
    else:
        print(f"分析失败：{result['error']}")
else:
    print(f"请求失败：{response.status_code}")
    print(response.text)
```

### cURL 示例

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "year": "2002",
    "month": "5",
    "day": "15",
    "hour": "14",
    "minute": "00",
    "gender": "男",
    "location": {
      "lat": "39n54",
      "lon": "116e23"
    }
  }'
```

### JavaScript (fetch) 示例

```javascript
const url = 'http://localhost:8000/api/v1/analyze';

const data = {
  year: '2002',
  month: '5',
  day: '15',
  hour: '14',
  minute: '00',
  gender: '男',
  location: {
    lat: '39n54',
    lon: '116e23'
  }
};

fetch(url, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(data)
})
.then(response => response.json())
.then(result => {
  if (result.success) {
    console.log('分析成功！');
    console.log('八字报告：', result.reports.bazi.content);
    console.log('紫微斗数报告：', result.reports.ziwei.content);
    console.log('星盘报告：', result.reports.xingpan.content);
    console.log('总耗时：', result.statistics.total_time, '秒');
  } else {
    console.error('分析失败：', result.error);
  }
})
.catch(error => {
  console.error('请求失败：', error);
});
```

## 环境变量配置

可以通过环境变量配置API服务：

- `API_HOST`: 服务监听地址（默认：0.0.0.0）
- `API_PORT`: 服务端口（默认：8000）

示例：

```bash
export API_HOST=127.0.0.1
export API_PORT=8080
python api/run.py
```

## 错误处理

API会返回标准的HTTP状态码：

- `200`: 请求成功
- `400`: 请求参数错误
- `500`: 服务器内部错误

错误响应格式：

```json
{
  "detail": "错误信息描述"
}
```

## 注意事项

1. **API密钥配置**：确保已正确配置 `config/.env` 文件中的 `DEEPSEEK_API_KEY`
2. **处理时间**：命理分析需要调用LLM，处理时间可能较长（通常30-60秒）
3. **Token消耗**：每次分析会消耗大量Token，请注意API配额
4. **并发限制**：建议根据服务器性能设置合理的并发限制
5. **生产环境**：生产环境部署时，建议：
   - 使用反向代理（如Nginx）
   - 配置HTTPS
   - 设置CORS白名单
   - 添加认证机制
   - 使用进程管理器（如supervisor或systemd）

## 架构说明

本API基于三层MOA架构：

1. **第一层**：三个独立的agent（八字、紫微、星盘）分别调用对应工具进行排盘，然后生成初步分析报告
2. **第二层**：三个agent参考第一层的三份报告，生成综合分析报告
3. **第三层**：三个agent参考第二层的报告和用户输入，生成最终报告

API返回的是第三层的最终报告。

