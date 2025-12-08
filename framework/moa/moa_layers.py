"""
三层 MOA (Mixture of Agents) 架构

实现三层 agent 协同架构，用于命理分析。
"""
from typing import List, Dict, Any, Tuple, Optional
from llm.client import LLMClient, get_client
from llm.response import LLMResponse
import prompt.moa.bazi as bazi  # type: ignore
import prompt.moa.ziwei as ziwei  # type: ignore
import prompt.moa.xingpan as xingpan  # type: ignore
import os
import logging
from datetime import datetime

# 创建logger
logger = logging.getLogger(__name__)


class MOALayers:
    """
    三层 MOA 架构类
    
    第一层：三个独立的 agent（八字、紫微、星盘）分别分析用户输入
    第二层：三个 agent 参考第一层的三份报告，生成新的报告
    第三层：三个 agent 参考第二层的三份报告和用户输入，生成最终报告
    """
    
    def __init__(self, model: str = "chat"):
        """
        初始化 MOA 架构。
        
        Args:
            model: 使用的模型类型，"chat" 或 "reasoner"
        """
        self.client = LLMClient(model=model)
        # 第一层角色提示词
        self.roles_layer1 = {
            'bazi': bazi.ROLE_LAYER1,
            'ziwei': ziwei.ROLE_LAYER1,
            'xingpan': xingpan.ROLE_LAYER1,
        }
        # 第二层角色提示词
        self.roles_layer2 = {
            'bazi': bazi.ROLE_LAYER2,
            'ziwei': ziwei.ROLE_LAYER2,
            'xingpan': xingpan.ROLE_LAYER2,
        }
        # 第三层角色提示词
        self.roles_layer3 = {
            'bazi': bazi.ROLE_LAYER3,
            'ziwei': ziwei.ROLE_LAYER3,
            'xingpan': xingpan.ROLE_LAYER3,
        }
        # 保持向后兼容
        self.roles = self.roles_layer1
        # 日志目录（在process方法中设置）
        self.log_dir: Optional[str] = None
    
    def _format_birth_info(self, year: str, month: str, day: str, hour: str, minute: str = "00") -> str:
        """
        格式化生日信息。
        
        Args:
            year: 年份（字符串，如 "1990"）
            month: 月份（字符串，如 "5" 或 "05"）
            day: 日期（字符串，如 "15" 或 "05"）
            hour: 小时（字符串，如 "14" 或 "06"）
            minute: 分钟（字符串，默认为 "00"，如 "30" 或 "00"）
            
        Returns:
            格式化的生日字符串
        """
        return f"公历生日：{year}年{month}月{day}日{hour}时{minute}分"
    
    
    def _call_agent(
        self,
        role: str,
        user_input: str,
        max_tokens: int = 2000,
        max_retries: int = 2,
        layer_name: Optional[str] = None,
        agent_name: Optional[str] = None
    ) -> LLMResponse:
        """
        调用单个 agent。
        
        Args:
            role: 角色提示词
            user_input: 用户输入
            max_tokens: 最大 token 数（控制输出长度）
            max_retries: 最大重试次数
            layer_name: 层级名称（如 "layer1"）
            agent_name: Agent 名称（如 "bazi"）
            
        Returns:
            LLMResponse 对象
        """
        messages = [
            {"role": "system", "content": role},
            {"role": "user", "content": user_input}
        ]
        
        response = self.client.chat(
            message=messages,
            max_tokens=max_tokens,
            max_retries=max_retries
        )
        
        # 保存日志
        if self.log_dir and layer_name and agent_name:
            self._save_agent_log(layer_name, agent_name, role, user_input, response)
        
        return response
    
    def _get_agent_number(self, layer_name: str, agent_name: str) -> int:
        """
        获取 agent 编号。
        
        Args:
            layer_name: 层级名称（如 "layer1"）
            agent_name: Agent 名称（如 "bazi"）
            
        Returns:
            Agent 编号（1-9）
        """
        agent_order = ['bazi', 'ziwei', 'xingpan']
        layer_order = ['layer1', 'layer2', 'layer3']
        
        layer_idx = layer_order.index(layer_name) if layer_name in layer_order else 0
        agent_idx = agent_order.index(agent_name) if agent_name in agent_order else 0
        
        return layer_idx * 3 + agent_idx + 1
    
    def _save_agent_log(
        self,
        layer_name: str,
        agent_name: str,
        role: str,
        user_input: str,
        response: LLMResponse
    ):
        """
        保存 agent 的输入输出日志。
        
        Args:
            layer_name: 层级名称（如 "layer1"）
            agent_name: Agent 名称（如 "bazi"）
            role: 角色提示词
            user_input: 用户输入
            response: LLM 响应对象
        """
        if not self.log_dir:
            return
        
        # 确保日志目录存在
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 获取 agent 编号
        agent_number = self._get_agent_number(layer_name, agent_name)
        
        # 日志文件名：agent_1.log, agent_2.log, ...
        log_filename = f"agent_{agent_number}.log"
        log_path = os.path.join(self.log_dir, log_filename)
        
        # 格式化日志内容
        log_content = []
        log_content.append("=" * 80)
        log_content.append(f"Agent: {layer_name} - {agent_name}")
        log_content.append(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        log_content.append("=" * 80)
        log_content.append("\n【系统提示词】")
        log_content.append("-" * 80)
        log_content.append(role)
        log_content.append("\n【用户输入】")
        log_content.append("-" * 80)
        log_content.append(user_input)
        log_content.append("\n【Agent 输出】")
        log_content.append("-" * 80)
        log_content.append(response.content)
        log_content.append("\n【响应信息】")
        log_content.append("-" * 80)
        log_content.append(f"模型: {response.model}")
        log_content.append(f"Token 使用: {response.total_tokens} (Prompt: {response.prompt_tokens}, Completion: {response.completion_tokens})")
        log_content.append(f"耗时: {response.elapsed_time:.2f}秒")
        log_content.append(f"重试次数: {response.retry_count}")
        if response.reasoning_content:
            log_content.append("\n【思考过程】")
            log_content.append("-" * 80)
            log_content.append(response.reasoning_content)
        log_content.append("\n" + "=" * 80 + "\n")
        
        # 写入日志文件（追加模式）
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write('\n'.join(log_content))
    
    def _combine_reports(self, reports: Dict[str, LLMResponse]) -> str:
        """
        合并多份报告。
        
        Args:
            reports: 报告字典，键为报告类型，值为 LLMResponse 对象
            
        Returns:
            合并后的报告字符串
        """
        combined = []
        type_names = {
            'bazi': '八字命理报告',
            'ziwei': '紫微斗数报告',
            'xingpan': '星盘占星报告'
        }
        
        for report_type, response in reports.items():
            type_name = type_names.get(report_type, report_type)
            combined.append(f"=== {type_name} ===\n{response.content}\n")
        
        return "\n".join(combined)
    
    def layer1(self, year: str, month: str, day: str, hour: str, minute: str = "00") -> Dict[str, LLMResponse]:
        """
        第一层：三个独立的 agent 分别分析用户输入。
        
        Args:
            year: 年份（字符串，如 "1990"）
            month: 月份（字符串，如 "5" 或 "05"）
            day: 日期（字符串，如 "15" 或 "05"）
            hour: 小时（字符串，如 "14" 或 "06"）
            minute: 分钟（字符串，默认为 "00"，如 "30"）
            
        Returns:
            包含三份报告的字典
        """
        birth_info = self._format_birth_info(year, month, day, hour, minute)
        user_input = f"{birth_info}"
        
        reports = {}
        
        # 并行调用三个 agent
        for role_type in ['bazi', 'ziwei', 'xingpan']:
            role = self.roles_layer1[role_type]
            response = self._call_agent(
                role, 
                user_input, 
                max_tokens=2000,
                layer_name="layer1",
                agent_name=role_type
            )
            reports[role_type] = response
        
        return reports
    
    def layer2(self, layer1_reports: Dict[str, LLMResponse], birth_info: str) -> Dict[str, LLMResponse]:
        """
        第二层：三个 agent 参考第一层的三份报告，生成新的报告。
        
        Args:
            layer1_reports: 第一层的三份报告
            birth_info: 用户生日信息
            
        Returns:
            包含三份新报告的字典
        """
        # 合并第一层的报告
        combined_reports = self._combine_reports(layer1_reports)
        
        user_input = f"{birth_info}\n\n以下是来自其他命理师的三份报告：\n{combined_reports}"
        
        reports = {}
        
        # 并行调用三个 agent
        for role_type in ['bazi', 'ziwei', 'xingpan']:
            role = self.roles_layer2[role_type]
            response = self._call_agent(
                role, 
                user_input, 
                max_tokens=2000,
                layer_name="layer2",
                agent_name=role_type
            )
            reports[role_type] = response
        
        return reports
    
    def layer3(
        self,
        layer2_reports: Dict[str, LLMResponse],
        year: str,
        month: str,
        day: str,
        hour: str,
        minute: str = "00"
    ) -> Dict[str, LLMResponse]:
        """
        第三层：三个 agent 参考第二层的三份报告和用户输入，生成最终报告。
        
        Args:
            layer2_reports: 第二层的三份报告
            year: 年份（字符串，如 "1990"）
            month: 月份（字符串，如 "5" 或 "05"）
            day: 日期（字符串，如 "15" 或 "05"）
            hour: 小时（字符串，如 "14" 或 "06"）
            minute: 分钟（字符串，默认为 "00"，如 "30"）
            
        Returns:
            包含最终三份报告的字典
        """
        birth_info = self._format_birth_info(year, month, day, hour, minute)
        
        # 合并第二层的报告
        combined_reports = self._combine_reports(layer2_reports)
        
        user_input = f"{birth_info}\n\n以下是来自其他命理师的三份综合分析报告：\n{combined_reports}"
        
        reports = {}
        
        # 并行调用三个 agent
        for role_type in ['bazi', 'ziwei', 'xingpan']:
            role = self.roles_layer3[role_type]
            response = self._call_agent(
                role, 
                user_input, 
                max_tokens=2000,
                layer_name="layer3",
                agent_name=role_type
            )
            reports[role_type] = response
        
        return reports
    
    def process(
        self,
        year: str,
        month: str,
        day: str,
        hour: str,
        minute: str = "00"
    ) -> Dict[str, Dict[str, LLMResponse]]:
        """
        执行完整的三层处理流程。
        
        Args:
            year: 年份（字符串，如 "1990"）
            month: 月份（字符串，如 "5" 或 "05"）
            day: 日期（字符串，如 "15" 或 "05"）
            hour: 小时（字符串，如 "14" 或 "06"）
            minute: 分钟（字符串，默认为 "00"，如 "30"）
            
        Returns:
            包含三层报告的字典，结构为：
            {
                'layer1': {report_type: LLMResponse, ...},
                'layer2': {report_type: LLMResponse, ...},
                'layer3': {report_type: LLMResponse, ...}
            }
        """
        birth_info = self._format_birth_info(year, month, day, hour, minute)
        
        # 创建日志目录（基于framework名称和时间戳）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dir_name = f"moa_layers_{timestamp}"
        self.log_dir = os.path.join('log', dir_name)
        os.makedirs(self.log_dir, exist_ok=True)
        logger.info(f"\n日志保存目录: {self.log_dir}\n")
        
        # 第一层
        logger.info("=" * 80)
        logger.info("第一层：三个独立的命理师分别分析用户输入")
        logger.info("=" * 80)
        layer1_reports = self.layer1(year, month, day, hour, minute)
        logger.info(f"第一层完成，生成了 {len(layer1_reports)} 份报告\n")
        
        # 第二层
        logger.info("=" * 80)
        logger.info("第二层：三个命理师参考第一层的报告，生成综合分析")
        logger.info("=" * 80)
        layer2_reports = self.layer2(layer1_reports, birth_info)
        logger.info(f"第二层完成，生成了 {len(layer2_reports)} 份报告\n")
        
        # 第三层
        logger.info("=" * 80)
        logger.info("第三层：三个命理师参考第二层的报告和用户输入，生成最终报告")
        logger.info("=" * 80)
        layer3_reports = self.layer3(layer2_reports, year, month, day, hour, minute)
        logger.info(f"第三层完成，生成了 {len(layer3_reports)} 份最终报告\n")
        
        return {
            'layer1': layer1_reports,
            'layer2': layer2_reports,
            'layer3': layer3_reports
        }
    
    def get_final_reports(self, results: Dict[str, Dict[str, LLMResponse]]) -> Dict[str, str]:
        """
        从处理结果中提取最终报告（第三层）。
        
        Args:
            results: process() 方法的返回结果
            
        Returns:
            包含最终报告内容的字典
        """
        layer3 = results.get('layer3', {})
        return {
            'bazi': layer3.get('bazi', LLMResponse("", "", {}, "", 0)).content,
            'ziwei': layer3.get('ziwei', LLMResponse("", "", {}, "", 0)).content,
            'xingpan': layer3.get('xingpan', LLMResponse("", "", {}, "", 0)).content,
        }
