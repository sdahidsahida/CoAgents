"""
API 测试脚本

用于测试MOA命理分析API服务。
"""
import requests
import json
import time

# API地址
API_BASE_URL = "http://localhost:8000"


def test_health_check():
    """测试健康检查接口"""
    print("=" * 80)
    print("测试1: 健康检查")
    print("=" * 80)
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        assert response.status_code == 200
        print("✓ 健康检查通过\n")
        return True
    except Exception as e:
        print(f"✗ 健康检查失败: {e}\n")
        return False


def test_root():
    """测试根路径接口"""
    print("=" * 80)
    print("测试2: 根路径")
    print("=" * 80)
    
    try:
        response = requests.get(f"{API_BASE_URL}/")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        assert response.status_code == 200
        print("✓ 根路径测试通过\n")
        return True
    except Exception as e:
        print(f"✗ 根路径测试失败: {e}\n")
        return False


def test_analyze():
    """测试命理分析接口"""
    print("=" * 80)
    print("测试3: 命理分析接口")
    print("=" * 80)
    
    # 测试数据
    test_data = {
        "year": "2002",
        "month": "5",
        "day": "15",
        "hour": "14",
        "minute": "00",
        "gender": "man",  # 使用man/woman格式
        "location": {
            "lat": "39n54",
            "lon": "116e23"
        }
    }
    
    print(f"请求数据:")
    print(json.dumps(test_data, ensure_ascii=False, indent=2))
    print("\n正在发送请求...")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/api/v1/analyze",
            json=test_data,
            timeout=300  # 5分钟超时，因为分析可能需要较长时间
        )
        elapsed_time = time.time() - start_time
        
        print(f"\n状态码: {response.status_code}")
        print(f"请求耗时: {elapsed_time:.2f}秒")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n响应数据:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            if result.get("success"):
                print("\n✓ 分析成功！")
                print(f"\n报告统计:")
                for report_type, report_info in result["reports"].items():
                    print(f"  {report_type}:")
                    print(f"    Token使用: {report_info['total_tokens']}")
                    print(f"    耗时: {report_info['elapsed_time']:.2f}秒")
                    print(f"    内容长度: {len(report_info['content'])} 字符")
                
                print(f"\n总体统计:")
                stats = result["statistics"]
                print(f"  总Token: {stats['total_tokens']}")
                print(f"  总耗时: {stats['total_time']:.2f}秒")
                print(f"  各层统计:")
                for layer_name, layer_stats in stats["layers"].items():
                    print(f"    {layer_name}: {layer_stats['tokens']} tokens, {layer_stats['time']:.2f}秒")
                
                return True
            else:
                print(f"\n✗ 分析失败: {result.get('error', '未知错误')}")
                return False
        else:
            print(f"\n✗ 请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n✗ 请求超时（分析可能需要更长时间）")
        return False
    except Exception as e:
        print(f"\n✗ 请求失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_analyze_minimal():
    """测试最小化请求（不包含可选参数）"""
    print("=" * 80)
    print("测试4: 最小化请求测试")
    print("=" * 80)
    
    # 最小化测试数据（只包含必填字段）
    test_data = {
        "year": "1990",
        "month": "1",
        "day": "1",
        "hour": "12",
        "gender": "woman"
    }
    
    print(f"请求数据:")
    print(json.dumps(test_data, ensure_ascii=False, indent=2))
    print("\n正在发送请求...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/analyze",
            json=test_data,
            timeout=300
        )
        
        print(f"\n状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✓ 最小化请求测试通过\n")
                return True
            else:
                print(f"✗ 分析失败: {result.get('error', '未知错误')}\n")
                return False
        else:
            print(f"✗ 请求失败: {response.status_code}")
            print(f"响应内容: {response.text}\n")
            return False
            
    except Exception as e:
        print(f"✗ 请求失败: {e}\n")
        return False


def test_validation_error():
    """测试参数验证错误"""
    print("=" * 80)
    print("测试5: 参数验证错误测试")
    print("=" * 80)
    
    # 错误的性别值
    test_data = {
        "year": "2002",
        "month": "5",
        "day": "15",
        "hour": "14",
        "gender": "invalid"  # 无效的性别值
    }
    
    print(f"请求数据（故意使用无效性别）:")
    print(json.dumps(test_data, ensure_ascii=False, indent=2))
    print("\n正在发送请求...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/analyze",
            json=test_data,
            timeout=10
        )
        
        print(f"\n状态码: {response.status_code}")
        
        if response.status_code == 422:  # FastAPI验证错误返回422
            print("✓ 参数验证错误测试通过（正确返回422错误）\n")
            return True
        else:
            print(f"✗ 未返回预期的422错误，实际状态码: {response.status_code}")
            print(f"响应内容: {response.text}\n")
            return False
            
    except Exception as e:
        print(f"✗ 请求失败: {e}\n")
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("MOA 命理分析 API 测试")
    print("=" * 80)
    print("\n请确保API服务已启动: python api/run.py")
    print("等待3秒后开始测试...\n")
    time.sleep(3)
    
    results = []
    
    # 运行测试
    results.append(("健康检查", test_health_check()))
    results.append(("根路径", test_root()))
    results.append(("参数验证", test_validation_error()))
    results.append(("最小化请求", test_analyze_minimal()))
    results.append(("完整分析", test_analyze()))  # 这个测试最耗时，放在最后
    
    # 打印测试结果汇总
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n总计: {len(results)} 个测试")
    print(f"通过: {passed} 个")
    print(f"失败: {failed} 个")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

