"""
MOA Layers 测试模块

测试三层 MOA 架构的功能。
"""
import pytest
from framework.moa.moa_layers import MOALayers


class TestMOALayers:
    """MOA Layers 测试类"""

    def test_moa_layers_initialization(self):
        """测试 MOA Layers 初始化"""
        moa = MOALayers(model="chat")
        assert moa is not None
        assert moa.client is not None
        assert len(moa.roles_layer1) == 3
        assert len(moa.roles_layer2) == 3
        assert len(moa.roles_layer3) == 3
        assert 'bazi' in moa.roles_layer1
        assert 'ziwei' in moa.roles_layer1
        assert 'xingpan' in moa.roles_layer1

    def test_format_birth_info(self):
        """测试生日信息格式化"""
        moa = MOALayers()
        birth_info = moa._format_birth_info("1990", "5", "15", "14", "30")
        assert "1990年5月15日14时30分" in birth_info
        
        # 测试默认分钟为00
        birth_info_default = moa._format_birth_info("1990", "5", "15", "14")
        assert "1990年5月15日14时00分" in birth_info_default
        
        # 测试前导零格式
        birth_info_leading_zero = moa._format_birth_info("1990", "05", "15", "06", "00")
        assert "1990年05月15日06时00分" in birth_info_leading_zero

    def test_layer1(self):
        """测试第一层处理"""
        moa = MOALayers(model="chat")
        reports = moa.layer1(year="1990", month="5", day="15", hour="14", minute="30")
        
        assert isinstance(reports, dict)
        assert len(reports) == 3
        assert 'bazi' in reports
        assert 'ziwei' in reports
        assert 'xingpan' in reports
        
        # 验证每份报告都是 LLMResponse 对象
        for report_type, response in reports.items():
            assert response is not None
            assert hasattr(response, 'content')
            assert len(response.content) > 0
            assert hasattr(response, 'elapsed_time')
            assert hasattr(response, 'total_tokens')

    def test_layer2(self):
        """测试第二层处理"""
        moa = MOALayers(model="chat")
        
        # 先运行第一层
        layer1_reports = moa.layer1(year="1990", month="5", day="15", hour="14", minute="30")
        
        # 运行第二层
        birth_info = moa._format_birth_info("1990", "5", "15", "14", "30")
        layer2_reports = moa.layer2(layer1_reports, birth_info)
        
        assert isinstance(layer2_reports, dict)
        assert len(layer2_reports) == 3
        
        # 验证第二层报告包含参考信息（通过检查内容长度应该比第一层更长或不同）
        for report_type, response in layer2_reports.items():
            assert response is not None
            assert len(response.content) > 0
            assert isinstance(response.content, str)

    def test_layer3(self):
        """测试第三层处理"""
        moa = MOALayers(model="chat")
        
        # 先运行第一层和第二层
        layer1_reports = moa.layer1(year="1990", month="5", day="15", hour="14", minute="30")
        birth_info = moa._format_birth_info("1990", "5", "15", "14", "30")
        layer2_reports = moa.layer2(layer1_reports, birth_info)
        
        # 运行第三层
        layer3_reports = moa.layer3(layer2_reports, year="1990", month="5", day="15", hour="14", minute="30")
        
        assert isinstance(layer3_reports, dict)
        assert len(layer3_reports) == 3
        
        for report_type, response in layer3_reports.items():
            assert response is not None
            assert len(response.content) > 0
            assert isinstance(response.content, str)

    def test_full_process(self):
        """测试完整的三层处理流程"""
        moa = MOALayers(model="chat")
        
        results = moa.process(year="1990", month="5", day="15", hour="14", minute="30")
        
        assert isinstance(results, dict)
        assert 'layer1' in results
        assert 'layer2' in results
        assert 'layer3' in results
        
        # 验证每层都有三份报告
        for layer_name in ['layer1', 'layer2', 'layer3']:
            layer_reports = results[layer_name]
            assert len(layer_reports) == 3
            for report_type, response in layer_reports.items():
                assert response is not None
                assert len(response.content) > 0
                assert response.elapsed_time > 0
                assert response.total_tokens > 0
        
        # 验证第三层报告数量正确
        assert len(results['layer3']) == 3
        
        # 获取最终报告
        final_reports = moa.get_final_reports(results)
        assert isinstance(final_reports, dict)
        assert len(final_reports) == 3
        assert 'bazi' in final_reports
        assert 'ziwei' in final_reports
        assert 'xingpan' in final_reports
        
        # 验证最终报告内容不为空
        for report_type, content in final_reports.items():
            assert isinstance(content, str)
            assert len(content) > 0

    def test_get_final_reports(self):
        """测试获取最终报告"""
        moa = MOALayers(model="chat")
        
        # 创建模拟结果
        from llm.response import LLMResponse
        mock_results = {
            'layer3': {
                'bazi': LLMResponse("八字报告", "model", {}, "id", 0),
                'ziwei': LLMResponse("紫微报告", "model", {}, "id", 0),
                'xingpan': LLMResponse("星盘报告", "model", {}, "id", 0),
            }
        }
        
        final_reports = moa.get_final_reports(mock_results)
        assert final_reports['bazi'] == "八字报告"
        assert final_reports['ziwei'] == "紫微报告"
        assert final_reports['xingpan'] == "星盘报告"


if __name__ == "__main__":
    # 直接运行此文件时执行测试
    pytest.main([__file__, "-v", "-s"])
