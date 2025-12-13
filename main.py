"""
主程序入口

展示如何使用 LLM Client。
"""
import logging
from llm.client import LLMClient

# 创建logger
logger = logging.getLogger(__name__)


def main():
    """主函数"""
    # 创建聊天客户端
    chat_client = LLMClient(model="deepseek-chat")
    
    # 基本聊天
    logger.info("=" * 50)
    logger.info("LLM Client 示例")
    logger.info("=" * 50)
    
    response = chat_client.chat("Hello, how are you?")
    logger.info(f"\n响应: {response}")
    
    # 使用推理模型
    logger.info("\n" + "-" * 50)
    reasoner_client = LLMClient(model="deepseek-reasoner")
    reason_response = reasoner_client.chat("What is 2+2? Please think step by step.")
    logger.info(f"\n推理结果: {reason_response}")


if __name__ == "__main__":
    main()

