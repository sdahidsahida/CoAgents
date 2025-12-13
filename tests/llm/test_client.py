"""
LLM Client 测试模块

测试 LLM 客户端的功能。
"""
import pytest
from llm.client import LLMClient, get_client
from llm.response import LLMResponse
'''
class TestLLMClient:
    """LLM Client 测试类"""

    def test_client_initialization(self, config):
        """测试客户端初始化"""
        print(f"\n[测试模型] {config.chat_model}")
        client = LLMClient(model=config.chat_model)
        assert client is not None
        assert client.model == config.chat_model
        assert client.model_type == "custom"
        
        print(f"\n[测试模型] {config.reasoner_model}")
        reasoner_client = LLMClient(model=config.reasoner_model)
        assert reasoner_client.model == config.reasoner_model
        assert reasoner_client.model_type == "custom"

    def test_client_chat_basic(self, config):
        """测试基本聊天功能"""
        print(f"\n[测试模型] {config.chat_model}")
        client = LLMClient(model=config.chat_model)
        response = client.chat("Hello, please respond with 'Hello!'")
        
        assert response is not None
        assert isinstance(response, LLMResponse)
        assert len(response.content) > 0
        assert response.elapsed_time > 0
        assert response.retry_count >= 0
        print(f"\n聊天响应: {response.content}")
        print(f"耗时: {response.elapsed_time:.2f}秒")
        print(f"Token 使用: {response.total_tokens}")

    def test_client_chat_with_system_message(self, config):
        """测试带系统消息的聊天"""
        print(f"\n[测试模型] {config.chat_model}")
        client = LLMClient(model=config.chat_model)
        response = client.chat(
            message="What is your name?",
            system_message="You are a helpful assistant named Alice."
        )
        
        assert response is not None
        assert isinstance(response, LLMResponse)
        print(f"\n带系统消息的响应: {response.content}")

    def test_client_chat_with_custom_model(self, config):
        """测试使用自定义模型"""
        print(f"\n[测试模型] {config.chat_model}")
        client = LLMClient(model=config.chat_model)
        response = client.chat(
            message="Hello!",
            model=config.chat_model
        )
        
        assert response is not None
        assert isinstance(response, LLMResponse)
        assert response.model == config.chat_model
        print(f"\n自定义模型响应: {response.content}")

    def test_client_chat_stream(self, config):
        """测试流式聊天"""
        print(f"\n[测试模型] {config.chat_model}")
        client = LLMClient(model=config.chat_model)
        chunks = []
        
        for chunk in client.chat_stream("Count from 1 to 5."):
            chunks.append(chunk)
        
        full_content = ''.join(chunks)
        assert len(chunks) > 0
        assert len(full_content) > 0
        print(f"\n流式响应: {full_content}")

    def test_client_reason(self, config):
        """测试推理功能"""
        print(f"\n[测试模型] {config.reasoner_model}")
        client = LLMClient(model=config.reasoner_model)
        response = client.reason("What is 2+2? Please think step by step.")
        
        assert response is not None
        assert isinstance(response, LLMResponse)
        assert len(response.content) > 0
        print(f"\n推理响应内容: {response.content}")
        if response.has_reasoning:
            print(f"\n思考过程: {response.reasoning_content[:200]}...")
        print(f"耗时: {response.elapsed_time:.2f}秒")

    def test_client_reason_stream(self, config):
        """测试流式推理"""
        print(f"\n[测试模型] {config.reasoner_model}")
        client = LLMClient(model=config.reasoner_model)
        chunks = []
        
        for chunk in client.reason_stream("What is 3+3? Think step by step."):
            chunks.append(chunk)
        
        full_content = ''.join(chunks)
        assert len(chunks) > 0
        assert len(full_content) > 0
        print(f"\n流式推理响应: {full_content}")

    def test_client_chat_with_response(self, config):
        """测试获取完整响应"""
        print(f"\n[测试模型] {config.chat_model}")
        client = LLMClient(model=config.chat_model)
        response = client.chat_with_response("Hello!")
        
        assert response is not None
        assert isinstance(response, LLMResponse)
        assert response.content is not None
        assert response.usage is not None
        assert response.model is not None
        assert response.id is not None
        assert response.total_tokens > 0
        assert response.elapsed_time > 0
        print(f"\n完整响应:")
        print(f"  内容: {response.content[:100]}...")
        print(f"  模型: {response.model}")
        print(f"  Token: {response.total_tokens}")
        print(f"  耗时: {response.elapsed_time:.2f}秒")
        print(f"  重试次数: {response.retry_count}")

    def test_client_with_message_list(self, config):
        """测试使用消息列表"""
        print(f"\n[测试模型] {config.chat_model}")
        client = LLMClient(model=config.chat_model)
        messages = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "My name is Bob."},
            {"role": "assistant", "content": "Nice to meet you, Bob!"},
            {"role": "user", "content": "What is my name?"},
        ]
        
        response = client.chat(messages)
        assert response is not None
        assert isinstance(response, LLMResponse)
        assert "Bob" in response.content or "bob" in response.content.lower()
        print(f"\n多轮对话响应: {response.content}")

    def test_client_with_parameters(self, config):
        """测试使用自定义参数"""
        print(f"\n[测试模型] {config.chat_model}")
        client = LLMClient(model=config.chat_model)
        response = client.chat(
            message="Say hello in one word.",
            temperature=0.1,
            max_tokens=10
        )
        
        assert response is not None
        assert isinstance(response, LLMResponse)
        print(f"\n自定义参数响应: {response.content}")

    def test_get_client_function(self, config):
        """测试 get_client 便捷函数"""
        print(f"\n[测试模型] {config.chat_model}")
        client1 = get_client(model=config.chat_model)
        client2 = get_client(model=config.chat_model)
        
        # get_client 返回单例
        assert client1 is client2

    def test_client_properties(self, config):
        """测试客户端属性"""
        print(f"\n[测试模型] {config.chat_model}")
        chat_client = LLMClient(model=config.chat_model)
        assert chat_client.model == config.chat_model
        assert chat_client.model_type == "custom"
        
        print(f"\n[测试模型] {config.reasoner_model}")
        reasoner_client = LLMClient(model=config.reasoner_model)
        assert reasoner_client.model == config.reasoner_model
        assert reasoner_client.model_type == "custom"

    def test_client_repr(self, config):
        """测试客户端字符串表示"""
        print(f"\n[测试模型] {config.chat_model}")
        client = LLMClient(model=config.chat_model)
        repr_str = repr(client)
        
        assert 'LLMClient' in repr_str
        assert client.model in repr_str
        print(f"\n客户端表示: {repr_str}")
    
    def test_response_object_properties(self, config):
        """测试响应对象的属性和方法"""
        print(f"\n[测试模型] {config.reasoner_model}")
        client = LLMClient(model=config.reasoner_model)
        response = client.chat("What is 2+2? Think step by step.")
        
        # 测试基本属性
        assert hasattr(response, 'content')
        assert hasattr(response, 'reasoning_content')
        assert hasattr(response, 'elapsed_time')
        assert hasattr(response, 'retry_count')
        assert hasattr(response, 'model')
        assert hasattr(response, 'usage')
        
        # 测试属性方法
        assert hasattr(response, 'has_reasoning')
        assert hasattr(response, 'full_content')
        assert hasattr(response, 'prompt_tokens')
        assert hasattr(response, 'completion_tokens')
        assert hasattr(response, 'total_tokens')
        
        # 测试方法
        assert hasattr(response, 'to_dict')
        assert hasattr(response, 'to_json')
        
        # 测试 to_dict
        response_dict = response.to_dict()
        assert isinstance(response_dict, dict)
        assert 'content' in response_dict
        assert 'elapsed_time' in response_dict
        assert 'retry_count' in response_dict
        
        # 测试字符串表示
        assert str(response) == response.content
        print(f"\n响应对象测试通过")
        print(f"  有思考过程: {response.has_reasoning}")
        print(f"  完整内容长度: {len(response.full_content)}")
        print(f"  字典格式: {list(response.to_dict().keys())}")
    
    def test_chat_vs_reasoner_comparison(self, config):
        """测试 chat 和 reasoner 模式对同一问题的回答对比"""
        question = "What is 2+2? Please explain step by step."
        
        print("\n" + "=" * 80)
        print("对比测试：Chat 模式 vs Reasoner 模式")
        print("=" * 80)
        print(f"\n问题: {question}\n")
        
        # Chat 模式
        print("-" * 80)
        print(f"Chat 模式响应: [模型: {config.chat_model}]")
        print("-" * 80)
        chat_client = LLMClient(model=config.chat_model)
        chat_response = chat_client.chat(question)
        
        print(f"\n响应对象类型: {type(chat_response)}")
        print(f"响应对象: {chat_response}")
        print(f"\n详细内容:")
        print(f"  content: {chat_response.content}")
        print(f"  reasoning_content: {chat_response.reasoning_content}")
        print(f"  has_reasoning: {chat_response.has_reasoning}")
        print(f"  model: {chat_response.model}")
        print(f"  elapsed_time: {chat_response.elapsed_time:.2f}秒")
        print(f"  retry_count: {chat_response.retry_count}")
        print(f"  prompt_tokens: {chat_response.prompt_tokens}")
        print(f"  completion_tokens: {chat_response.completion_tokens}")
        print(f"  total_tokens: {chat_response.total_tokens}")
        print(f"  finish_reason: {chat_response.finish_reason}")
        print(f"  id: {chat_response.id}")
        print(f"  created: {chat_response.created}")
        
        # 验证 chat 模式没有 thinking
        assert chat_response.reasoning_content is None or chat_response.reasoning_content == ""
        assert chat_response.has_reasoning == False
        
        # Reasoner 模式
        print("\n" + "-" * 80)
        print(f"Reasoner 模式响应: [模型: {config.reasoner_model}]")
        print("-" * 80)
        reasoner_client = LLMClient(model=config.reasoner_model)
        reasoner_response = reasoner_client.chat(question)
        
        print(f"\n响应对象类型: {type(reasoner_response)}")
        print(f"响应对象: {reasoner_response}")
        print(f"\n详细内容:")
        print(f"  content: {reasoner_response.content}")
        print(f"  reasoning_content: {reasoner_response.reasoning_content}")
        print(f"  has_reasoning: {reasoner_response.has_reasoning}")
        print(f"  model: {reasoner_response.model}")
        print(f"  elapsed_time: {reasoner_response.elapsed_time:.2f}秒")
        print(f"  retry_count: {reasoner_response.retry_count}")
        print(f"  prompt_tokens: {reasoner_response.prompt_tokens}")
        print(f"  completion_tokens: {reasoner_response.completion_tokens}")
        print(f"  total_tokens: {reasoner_response.total_tokens}")
        print(f"  finish_reason: {reasoner_response.finish_reason}")
        print(f"  id: {reasoner_response.id}")
        print(f"  created: {reasoner_response.created}")
        
        # 验证 reasoner 模式有 thinking
        if reasoner_response.has_reasoning:
            print(f"\n思考过程（前500字符）:")
            print(f"  {reasoner_response.reasoning_content[:500]}...")
        
        # 打印完整字典格式
        print("\n" + "-" * 80)
        print("Chat 模式完整字典:")
        print("-" * 80)
        import json
        print(json.dumps(chat_response.to_dict(), ensure_ascii=False, indent=2))
        
        print("\n" + "-" * 80)
        print("Reasoner 模式完整字典:")
        print("-" * 80)
        print(json.dumps(reasoner_response.to_dict(), ensure_ascii=False, indent=2))
        
        print("\n" + "=" * 80)
        print("对比总结:")
        print("=" * 80)
        print(f"Chat 模式:")
        print(f"  - 有思考过程: {chat_response.has_reasoning}")
        print(f"  - 内容长度: {len(chat_response.content)}")
        print(f"  - 耗时: {chat_response.elapsed_time:.2f}秒")
        print(f"  - Token 使用: {chat_response.total_tokens}")
        
        print(f"\nReasoner 模式:")
        print(f"  - 有思考过程: {reasoner_response.has_reasoning}")
        print(f"  - 内容长度: {len(reasoner_response.content)}")
        if reasoner_response.has_reasoning:
            print(f"  - 思考过程长度: {len(reasoner_response.reasoning_content)}")
        print(f"  - 耗时: {reasoner_response.elapsed_time:.2f}秒")
        print(f"  - Token 使用: {reasoner_response.total_tokens}")
        
        # 断言验证
        assert isinstance(chat_response, LLMResponse)
        assert isinstance(reasoner_response, LLMResponse)
        # Chat 模式不应该有思考过程
        assert chat_response.reasoning_content is None or chat_response.reasoning_content == ""
        assert chat_response.has_reasoning == False
        # Reasoner 模式可能有思考过程（取决于 API 响应）
        # 至少 reasoning_content 字段应该存在（即使为 None）
        assert hasattr(reasoner_response, 'reasoning_content')

    def test_client_error_handling_invalid_message(self, config):
        """测试错误处理 - 无效的消息类型"""
        print(f"\n[测试模型] {config.chat_model}")
        client = LLMClient(model=config.chat_model)
        
        with pytest.raises(ValueError):
            client.chat(123)  # type: ignore

    def test_client_error_handling_invalid_model(self):
        """测试错误处理 - 无效的模型类型"""
        # 注意：现在无效模型不会立即抛出 ValueError，而是在 API 调用时失败
        # 但我们可以测试一个明显无效的模型名称
        print("\n[测试模型] invalid-model-name")
        # 这个测试现在会尝试初始化，但可能在 API 调用时失败
        # 如果模型名称无法识别提供商，会抛出 ValueError
        try:
            client = LLMClient(model="invalid-model-name")
            # 如果初始化成功，尝试调用 API（应该会失败）
            with pytest.raises(Exception):  # 可能是 ValueError 或其他异常
                client.chat("test")
        except ValueError:
            # 如果初始化时就失败，这也是预期的
            pass
'''

class TestGeminiClient:
    """Gemini 模型测试类"""
    
    def test_gemini_client_initialization(self, gemini_api_key):
        """测试 Gemini 客户端初始化"""
        print("\n[测试模型] gemini-2.5-flash")
        client = LLMClient(model="gemini-2.5-flash")
        assert client is not None
        assert client.model == "gemini-2.5-flash"
        assert client.model_name == "gemini-2.5-flash"
    
    def test_gemini_client_chat_basic(self, gemini_api_key):
        """测试 Gemini 基本聊天功能"""
        print("\n[测试模型] gemini-2.5-flash")
        client = LLMClient(model="gemini-2.5-flash")
        response = client.chat("Hello, please respond with 'Hello!'")
        
        assert response is not None
        assert isinstance(response, LLMResponse)
        assert len(response.content) > 0
        assert response.elapsed_time > 0
        assert response.retry_count >= 0
        assert response.model == "gemini-2.5-flash"
        print(f"\nGemini 聊天响应: {response.content}")
        print(f"耗时: {response.elapsed_time:.2f}秒")
        print(f"Token 使用: {response.total_tokens}")
    
    def test_gemini_client_chat_with_system_message(self, gemini_api_key):
        """测试 Gemini 带系统消息的聊天"""
        print("\n[测试模型] gemini-2.5-flash")
        client = LLMClient(model="gemini-2.5-flash")
        response = client.chat(
            message="What is your name?",
            system_message="You are a helpful assistant named Alice."
        )
        
        assert response is not None
        assert isinstance(response, LLMResponse)
        assert len(response.content) > 0
        print(f"\nGemini 带系统消息的响应: {response.content}")
    
    def test_gemini_client_chat_with_message_list(self, gemini_api_key):
        """测试 Gemini 使用消息列表"""
        print("\n[测试模型] gemini-2.5-flash")
        client = LLMClient(model="gemini-2.5-flash")
        messages = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "My name is Bob."},
            {"role": "assistant", "content": "Nice to meet you, Bob!"},
            {"role": "user", "content": "What is my name?"},
        ]
        
        response = client.chat(messages)
        assert response is not None
        assert isinstance(response, LLMResponse)
        assert len(response.content) > 0
        print(f"\nGemini 多轮对话响应: {response.content}")
    
    def test_gemini_client_chat_with_parameters(self, gemini_api_key):
        """测试 Gemini 使用自定义参数"""
        print("\n[测试模型] gemini-2.5-flash")
        client = LLMClient(model="gemini-2.5-flash")
        response = client.chat(
            message="Say hello in one word.",
            temperature=0.1,
            max_tokens=20  # 增加 max_tokens 以确保有响应
        )
        
        assert response is not None
        assert isinstance(response, LLMResponse)
        assert len(response.content) > 0
        print(f"\nGemini 自定义参数响应: {response.content}")
    
    def test_gemini_client_chat_stream(self, gemini_api_key):
        """测试 Gemini 流式聊天"""
        print("\n[测试模型] gemini-2.5-flash")
        client = LLMClient(model="gemini-2.5-flash")
        chunks = []
        
        for chunk in client.chat_stream("Count from 1 to 5."):
            chunks.append(chunk)
        
        full_content = ''.join(chunks)
        assert len(chunks) > 0
        assert len(full_content) > 0
        print(f"\nGemini 流式响应: {full_content}")
    
    def test_gemini_client_chat_with_response(self, gemini_api_key):
        """测试 Gemini 获取完整响应"""
        print("\n[测试模型] gemini-2.5-flash")
        client = LLMClient(model="gemini-2.5-flash")
        response = client.chat_with_response("Hello!")
        
        assert response is not None
        assert isinstance(response, LLMResponse)
        assert response.content is not None
        assert response.usage is not None
        assert response.model == "gemini-2.5-flash"
        assert response.id is not None
        assert response.elapsed_time > 0
        print(f"\nGemini 完整响应:")
        print(f"  内容: {response.content[:100]}...")
        print(f"  模型: {response.model}")
        print(f"  Token: {response.total_tokens}")
        print(f"  耗时: {response.elapsed_time:.2f}秒")
        print(f"  重试次数: {response.retry_count}")
    
    def test_gemini_client_repr(self, gemini_api_key):
        """测试 Gemini 客户端字符串表示"""
        print("\n[测试模型] gemini-2.5-flash")
        client = LLMClient(model="gemini-2.5-flash")
        repr_str = repr(client)
        
        assert 'LLMClient' in repr_str
        assert 'gemini-2.5-flash' in repr_str
        print(f"\nGemini 客户端表示: {repr_str}")
    
    def test_gemini_response_object_properties(self, gemini_api_key):
        """测试 Gemini 响应对象的属性和方法"""
        print("\n[测试模型] gemini-2.5-flash")
        client = LLMClient(model="gemini-2.5-flash")
        response = client.chat("What is 2+2?")
        
        # 测试基本属性
        assert hasattr(response, 'content')
        assert hasattr(response, 'elapsed_time')
        assert hasattr(response, 'retry_count')
        assert hasattr(response, 'model')
        assert hasattr(response, 'usage')
        
        # 测试属性方法
        assert hasattr(response, 'has_reasoning')
        assert hasattr(response, 'full_content')
        assert hasattr(response, 'prompt_tokens')
        assert hasattr(response, 'completion_tokens')
        assert hasattr(response, 'total_tokens')
        
        # 测试方法
        assert hasattr(response, 'to_dict')
        assert hasattr(response, 'to_json')
        
        # 测试 to_dict
        response_dict = response.to_dict()
        assert isinstance(response_dict, dict)
        assert 'content' in response_dict
        assert 'elapsed_time' in response_dict
        assert 'retry_count' in response_dict
        
        # 测试字符串表示
        assert str(response) == response.content
        print(f"\nGemini 响应对象测试通过")
        print(f"  有思考过程: {response.has_reasoning}")
        print(f"  完整内容长度: {len(response.full_content)}")
        print(f"  字典格式: {list(response.to_dict().keys())}")
    
    def test_gemini_vs_deepseek_comparison(self, gemini_api_key, config):
        """测试 Gemini 和 DeepSeek 模型对同一问题的回答对比"""
        question = "What is 2+2? Please explain step by step."
        
        print("\n" + "=" * 80)
        print("对比测试：Gemini 模式 vs DeepSeek 模式")
        print("=" * 80)
        print(f"\n问题: {question}\n")
        
        # Gemini 模式
        print("-" * 80)
        print("Gemini 模式响应: [模型: gemini-2.5-flash]")
        print("-" * 80)
        gemini_client = LLMClient(model="gemini-2.5-flash")
        gemini_response = gemini_client.chat(question)
        
        print(f"\n响应对象类型: {type(gemini_response)}")
        print(f"响应对象: {gemini_response}")
        print(f"\n详细内容:")
        print(f"  content: {gemini_response.content}")
        print(f"  model: {gemini_response.model}")
        print(f"  elapsed_time: {gemini_response.elapsed_time:.2f}秒")
        print(f"  retry_count: {gemini_response.retry_count}")
        print(f"  prompt_tokens: {gemini_response.prompt_tokens}")
        print(f"  completion_tokens: {gemini_response.completion_tokens}")
        print(f"  total_tokens: {gemini_response.total_tokens}")
        print(f"  id: {gemini_response.id}")
        print(f"  created: {gemini_response.created}")
        
        # DeepSeek 模式
        print("\n" + "-" * 80)
        print(f"DeepSeek 模式响应: [模型: {config.chat_model}]")
        print("-" * 80)
        deepseek_client = LLMClient(model=config.chat_model)
        deepseek_response = deepseek_client.chat(question)
        
        print(f"\n响应对象类型: {type(deepseek_response)}")
        print(f"响应对象: {deepseek_response}")
        print(f"\n详细内容:")
        print(f"  content: {deepseek_response.content}")
        print(f"  model: {deepseek_response.model}")
        print(f"  elapsed_time: {deepseek_response.elapsed_time:.2f}秒")
        print(f"  retry_count: {deepseek_response.retry_count}")
        print(f"  prompt_tokens: {deepseek_response.prompt_tokens}")
        print(f"  completion_tokens: {deepseek_response.completion_tokens}")
        print(f"  total_tokens: {deepseek_response.total_tokens}")
        print(f"  id: {deepseek_response.id}")
        print(f"  created: {deepseek_response.created}")
        
        # 打印完整字典格式
        print("\n" + "-" * 80)
        print("Gemini 模式完整字典:")
        print("-" * 80)
        import json
        print(json.dumps(gemini_response.to_dict(), ensure_ascii=False, indent=2))
        
        print("\n" + "-" * 80)
        print("DeepSeek 模式完整字典:")
        print("-" * 80)
        print(json.dumps(deepseek_response.to_dict(), ensure_ascii=False, indent=2))
        
        print("\n" + "=" * 80)
        print("对比总结:")
        print("=" * 80)
        print(f"Gemini 模式:")
        print(f"  - 内容长度: {len(gemini_response.content)}")
        print(f"  - 耗时: {gemini_response.elapsed_time:.2f}秒")
        print(f"  - Token 使用: {gemini_response.total_tokens}")
        
        print(f"\nDeepSeek 模式:")
        print(f"  - 内容长度: {len(deepseek_response.content)}")
        print(f"  - 耗时: {deepseek_response.elapsed_time:.2f}秒")
        print(f"  - Token 使用: {deepseek_response.total_tokens}")
        
        # 断言验证
        assert isinstance(gemini_response, LLMResponse)
        assert isinstance(deepseek_response, LLMResponse)
        assert gemini_response.model == "gemini-2.5-flash"
        assert deepseek_response.model == config.chat_model


if __name__ == "__main__":
    # 直接运行此文件时执行测试
    pytest.main([__file__, "-v", "-s"])

