"""
MOA 三层架构 HTTP API 接口

提供HTTP接口供外部调用MOA三层架构进行命理分析。
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
import logging
from framework.moa.moa_layers import MOALayers

# 创建logger
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="MOA 命理分析 API",
    description="基于三层MOA架构的命理分析服务，集成八字、紫微斗数、星盘占星三大工具",
    version="1.0.0"
)

# 配置CORS中间件，允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应设置为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局MOA实例（可选：可以改为每次请求创建新实例）
moa_instance: Optional[MOALayers] = None


def get_moa_instance(model: Optional[str] = None) -> MOALayers:
    """获取MOA实例（单例模式）"""
    global moa_instance
    if moa_instance is None:
        moa_instance = MOALayers(model=model or "deepseek-chat")
    return moa_instance


# ==================== 请求和响应模型 ====================

class LocationModel(BaseModel):
    """出生地点模型"""
    lat: str = Field(..., description="纬度，格式如：39n54（北纬39度54分）")
    lon: str = Field(..., description="经度，格式如：116e23（东经116度23分）")


class AnalysisRequest(BaseModel):
    """命理分析请求模型"""
    year: str = Field(..., description="出生年份，4位数字，如：2002")
    month: str = Field(..., description="出生月份，1-12，如：5 或 05")
    day: str = Field(..., description="出生日期，1-31，如：15 或 05")
    hour: str = Field(..., description="出生小时，0-23，如：14 或 06")
    minute: str = Field("00", description="出生分钟，0-59，默认为00")
    gender: str = Field(..., description="性别，man 或 woman")
    location: Optional[LocationModel] = Field(None, description="出生地点（可选），占星需要")
    model: Optional[str] = Field(None, description="使用的模型名称，如：deepseek-chat（可选）")

    @validator('year')
    def validate_year(cls, v):
        if not v.isdigit() or len(v) != 4:
            raise ValueError('年份必须是4位数字')
        return v

    @validator('month')
    def validate_month(cls, v):
        if not v.isdigit():
            raise ValueError('月份必须是数字')
        month_num = int(v)
        if not (1 <= month_num <= 12):
            raise ValueError('月份必须在1-12之间')
        return v

    @validator('day')
    def validate_day(cls, v):
        if not v.isdigit():
            raise ValueError('日期必须是数字')
        day_num = int(v)
        if not (1 <= day_num <= 31):
            raise ValueError('日期必须在1-31之间')
        return v

    @validator('hour')
    def validate_hour(cls, v):
        if not v.isdigit():
            raise ValueError('小时必须是数字')
        hour_num = int(v)
        if not (0 <= hour_num <= 23):
            raise ValueError('小时必须在0-23之间')
        return v

    @validator('minute')
    def validate_minute(cls, v):
        if not v.isdigit():
            raise ValueError('分钟必须是数字')
        minute_num = int(v)
        if not (0 <= minute_num <= 59):
            raise ValueError('分钟必须在0-59之间')
        return v

    @validator('gender')
    def validate_gender(cls, v):
        if v not in ["man", "woman"]:
            raise ValueError('性别必须是：man 或 woman')
        return v


class ReportInfo(BaseModel):
    """报告信息模型"""
    content: str = Field(..., description="报告内容")
    total_tokens: int = Field(..., description="使用的Token总数")
    elapsed_time: float = Field(..., description="处理耗时（秒）")


class AnalysisResponse(BaseModel):
    """命理分析响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    reports: Dict[str, ReportInfo] = Field(..., description="最终报告（第三层）")
    statistics: Dict[str, Any] = Field(..., description="处理统计信息")
    error: Optional[str] = Field(None, description="错误信息（如果失败）")


# ==================== API 端点 ====================

@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
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


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "MOA 命理分析 API"
    }


@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest):
    """
    命理分析接口
    
    基于用户提供的生辰信息，使用三层MOA架构进行命理分析。
    每个agent会先调用对应的专业工具（八字、紫微斗数、星盘占星）进行排盘，
    然后基于排盘结果生成分析报告。
    
    **请求参数说明：**
    - year: 出生年份（4位数字，如：2002）
    - month: 出生月份（1-12，如：5 或 05）
    - day: 出生日期（1-31，如：15 或 05）
    - hour: 出生小时（0-23，如：14 或 06）
    - minute: 出生分钟（0-59，默认为00）
    - gender: 性别（man 或 woman）
    - location: 出生地点（可选，占星需要，格式：{"lat": "39n54", "lon": "116e23"}）
    - model: 使用的模型名称（可选，默认：deepseek-chat）
    
    **返回说明：**
    - success: 是否成功
    - reports: 包含三个报告（bazi、ziwei、xingpan）
    - statistics: 处理统计信息（Token使用、耗时等）
    """
    try:
        logger.info(f"收到分析请求：{request.year}年{request.month}月{request.day}日{request.hour}时{request.minute}分，性别：{request.gender}")
        
        # 获取MOA实例
        moa = get_moa_instance(model=request.model)
        
        # 准备location参数
        location_dict = None
        if request.location:
            location_dict = {
                "lat": request.location.lat,
                "lon": request.location.lon
            }
        
        # 转换性别格式：API使用man/woman，底层框架使用中文
        gender_map = {"man": "男", "woman": "女"}
        gender_chinese = gender_map.get(request.gender, request.gender)
        
        # 执行三层处理流程
        results = moa.process(
            year=request.year,
            month=request.month,
            day=request.day,
            hour=request.hour,
            minute=request.minute,
            gender=gender_chinese,
            location=location_dict
        )
        
        # 获取最终报告
        final_reports = moa.get_final_reports(results)
        
        # 构建响应数据
        reports_dict = {}
        for report_type, content in final_reports.items():
            layer3_response = results['layer3'][report_type]
            reports_dict[report_type] = ReportInfo(
                content=content,
                total_tokens=layer3_response.total_tokens,
                elapsed_time=layer3_response.elapsed_time
            )
        
        # 计算统计信息
        total_tokens = 0
        total_time = 0.0
        layer_stats = {}
        
        for layer_name in ['layer1', 'layer2', 'layer3']:
            layer_tokens = sum(r.total_tokens for r in results[layer_name].values())
            layer_time = sum(r.elapsed_time for r in results[layer_name].values())
            total_tokens += layer_tokens
            total_time += layer_time
            
            layer_stats[layer_name] = {
                "tokens": layer_tokens,
                "time": round(layer_time, 2)
            }
        
        statistics = {
            "total_tokens": total_tokens,
            "total_time": round(total_time, 2),
            "layers": layer_stats
        }
        
        return AnalysisResponse(
            success=True,
            message="分析完成",
            reports=reports_dict,
            statistics=statistics
        )
        
    except ValueError as e:
        logger.error(f"请求参数验证失败：{str(e)}")
        raise HTTPException(status_code=400, detail=f"请求参数错误：{str(e)}")
    except Exception as e:
        logger.error(f"分析过程中发生错误：{str(e)}", exc_info=True)
        return AnalysisResponse(
            success=False,
            message="分析失败",
            reports={},
            statistics={},
            error=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

