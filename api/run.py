"""
API 服务启动脚本

用于启动MOA命理分析API服务。
"""
import uvicorn
import logging
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """启动API服务"""
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    logger.info(f"启动MOA命理分析API服务...")
    logger.info(f"服务地址: http://{host}:{port}")
    logger.info(f"API文档: http://{host}:{port}/docs")
    logger.info(f"ReDoc文档: http://{host}:{port}/redoc")
    
    uvicorn.run(
        "api.app:app",
        host=host,
        port=port,
        reload=True,  # 开发模式：代码变更自动重载
        log_level="info"
    )


if __name__ == "__main__":
    main()

