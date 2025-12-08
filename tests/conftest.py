"""
pytest 配置文件

此文件包含所有测试共享的 fixtures 和配置。
pytest 会自动发现并加载此文件。
"""
import os
import sys
import pytest
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 加载环境变量
load_dotenv()

from config.config import get_config


@pytest.fixture(scope="session")
def config():
    """
    获取全局配置实例的 fixture。
    
    作用域：session - 整个测试会话只创建一次
    """
    return get_config()


@pytest.fixture(scope="session")
def api_key():
    """
    获取 API Key 的 fixture。
    
    如果环境变量未设置，则跳过所有需要 API 的测试。
    """
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    if not api_key:
        pytest.skip("DEEPSEEK_API_KEY 环境变量未设置")
    return api_key


@pytest.fixture(scope="session")
def base_url():
    """
    获取 Base URL 的 fixture。
    
    如果环境变量未设置，则跳过所有需要 API 的测试。
    """
    base_url = os.environ.get('DEEPSEEK_BASE_URL')
    if not base_url:
        pytest.skip("DEEPSEEK_BASE_URL 环境变量未设置")
    return base_url


@pytest.fixture(scope="session")
def openai_client(api_key, base_url):
    """
    创建 OpenAI 客户端的 fixture。
    
    作用域：session - 整个测试会话只创建一次，提高测试效率
    """
    return OpenAI(
        api_key=api_key,
        base_url=base_url
    )


@pytest.fixture(scope="function")
def chat_messages():
    """
    提供标准的聊天消息列表 fixture。
    
    作用域：function - 每个测试函数都会获得一个新的消息列表
    """
    return [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ]

