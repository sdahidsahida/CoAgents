"""
主程序入口

展示如何使用 LLM Client。
"""
from llm.client import LLMClient


def main():
    """主函数"""
    # 创建聊天客户端
    chat_client = LLMClient(model="chat")
    
    # 基本聊天
    print("=" * 50)
    print("LLM Client 示例")
    print("=" * 50)
    
    response = chat_client.chat("Hello, how are you?")
    print(f"\n响应: {response}")
    
    # 使用推理模型
    print("\n" + "-" * 50)
    reasoner_client = LLMClient(model="reasoner")
    reason_response = reasoner_client.chat("What is 2+2? Please think step by step.")
    print(f"\n推理结果: {reason_response}")


if __name__ == "__main__":
    main()

