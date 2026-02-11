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
import prompt.moa.final as final_prompt  # type: ignore
from framework.tools import tool_manager, extract_birth_info
import os
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# 创建logger
logger = logging.getLogger(__name__)


class MOALayers:
    """
    三层 MOA 架构类
    
    第一层：三个独立的 agent（八字、紫微、星盘）分别分析用户输入
    第二层：三个 agent 参考第一层的三份报告，生成新的报告
    第三层：三个 agent 参考第二层的三份报告和用户输入，生成最终报告
    """
    
    def __init__(self, model: Optional[str] = None):
        """
        初始化 MOA 架构。
        
        Args:
            model: 使用的模型名称，如 "deepseek-chat", "deepseek-reasoner", "gemini-2.5-flash"
                如果为 None，则使用配置中的 chat_model
        """
        self.client = LLMClient(model=model)
        keys = os.getenv("DEEPSEEK_API_KEYS", "").strip()
        self._api_keys = [k.strip() for k in keys.split(",") if k.strip()]

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
        # 第四层（总编聚合）角色提示词：将三系输出按领域权重融合为一份最终报告
        self.role_layer4 = final_prompt.ROLE_LAYER4

        # 默认领域权重（可后续用数据集标注/评测再校准）
        # 分数越高代表该体系在该领域的相对置信度越高（用于融合时的“主/辅参考”权重）
        self.domain_weights = {
            "personality": {"bazi": 50, "ziwei": 70, "xingpan": 70},
            "wealth_career": {"bazi": 80, "ziwei": 82, "xingpan": 72},
            "fortune_cycles": {"bazi": 90, "ziwei": 85, "xingpan": 78},
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

    def _run_agents_parallel(
            self,
            roles: Dict[str, str],
            user_input: str,
            layer_name: str,
            max_tokens: int = 2000,
            max_retries: int = 2,
            max_workers: int = 3,
    ) -> Dict[str, LLMResponse]:
        """
        并行调用多个 agent（同一层的 bazi/ziwei/xingpan）
        - 每个线程创建独立 LLMClient（避免线程安全问题）
        - 支持多 Key：从环境变量 DEEPSEEK_API_KEYS=key1,key2,key3 读取
        - 计时日志：打印每个线程的 START/END 和 dt
        """

        def _pick_key(role_type: str) -> Optional[str]:
            keys = getattr(self, "_api_keys", None) or []
            if not keys:
                return None
            mapping = {"bazi": 0, "ziwei": 1, "xingpan": 2}
            idx = mapping.get(role_type, 0) % len(keys)
            return keys[idx]

        def _one(role_type: str, role_prompt: str) -> Tuple[str, LLMResponse]:
            api_key = _pick_key(role_type)
            logger.info(f"[multi-key] {layer_name}:{role_type} key=***{(api_key or '')[-4:]}")

            # 每线程一个 client
            tmp_client = LLMClient(
                model=getattr(self.client, "model_name", None) or getattr(self.client, "model", None),
                api_key=api_key,
                base_url=os.getenv("DEEPSEEK_BASE_URL", None),
            )

            messages = [
                {"role": "system", "content": role_prompt},
                {"role": "user", "content": user_input},
            ]

            import time
            t0 = time.time()
            logger.info(f"[parallel] START {layer_name}:{role_type} t={t0:.3f}")

            resp = tmp_client.chat(
                message=messages,
                max_tokens=max_tokens,
                max_retries=max_retries,
            )

            t1 = time.time()
            logger.info(f"[parallel] END   {layer_name}:{role_type} t={t1:.3f} dt={t1 - t0:.2f}s")

            # 保存日志（每个 agent 写不同文件，线程并发安全）
            if self.log_dir:
                self._save_agent_log(layer_name, role_type, role_prompt, user_input, resp)

            return role_type, resp

        reports: Dict[str, LLMResponse] = {}

        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            futures = {ex.submit(_one, rt, rp): rt for rt, rp in roles.items()}

            for fut in as_completed(futures):
                role_type = futures[fut]
                # 注意：这里不要手搓 LLMResponse（你项目里构造参数很复杂）
                k, v = fut.result()  # 如果失败，直接抛出，让你看见真实错误
                reports[k] = v

        return reports

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

    def layer1(
            self,
            year: str,
            month: str,
            day: str,
            hour: str,
            minute: str = "00",
            gender: str = "女",
            location: Optional[Dict[str, str]] = None
    ) -> Dict[str, LLMResponse]:
        """
        第一层：三个独立的 agent 分别分析用户输入（工具排盘顺序；LLM 并行）。
        """
        birth_info = self._format_birth_info(year, month, day, hour, minute)

        # 转换为整数用于工具调用
        year_int = int(year)
        month_int = int(month)
        day_int = int(day)
        hour_int = int(hour)
        minute_int = int(minute)

        # ===== 1) 先顺序跑工具，准备每个 agent 的 user_input =====
        reports: Dict[str, LLMResponse] = {}
        tool_results: Dict[str, Any] = {}
        inputs: Dict[str, str] = {}

        for role_type in ["bazi", "ziwei", "xingpan"]:
            tool_type = {
                "bazi": "bazi",
                "ziwei": "ziwei",
                "xingpan": "astrology",
            }[role_type]

            tool_result = tool_manager.calculate(
                tool_type=tool_type,
                year=year_int,
                month=month_int,
                day=day_int,
                hour=hour_int,
                minute=minute_int,
                gender=gender,
                location=location,
            )
            tool_results[role_type] = tool_result

            if tool_result.get("success"):
                tool_text = tool_manager.format_for_prompt(tool_type, tool_result)
                user_input = (
                    f"{birth_info}\n"
                    f"【硬约束】性别={gender}。你必须以{gender}命盘解读，禁止输出“女命/男命”与该性别相反的表述。\n"
                    f"{tool_text}"
                )
            else:
                logger.warning(f"{tool_type} tool failed: {tool_result.get('error')}")
                user_input = (
                    f"{birth_info}\n性别：{gender}\n\n"
                    f"注意：{tool_type}工具计算失败，请基于生辰信息进行分析。"
                )

            inputs[role_type] = user_input

        # ===== 2) 缓存“工具原文区”，供 layer2/layer3 使用（保持你现有逻辑）=====
        try:
            bazi_txt = tool_manager.format_for_prompt("bazi", tool_results.get("bazi", {}))
            ziwei_txt = tool_manager.format_for_prompt("ziwei", tool_results.get("ziwei", {}))
            xingpan_txt = tool_manager.format_for_prompt("astrology", tool_results.get("xingpan", {}))
            self._latest_tool_block = (
                    "【工具原文（事实源，字段必须原样照抄，不得改写）】\n"
                    + bazi_txt + "\n"
                    + ziwei_txt + "\n"
                    + xingpan_txt + "\n"
            )
        except Exception as e:
            logger.warning(f"build _latest_tool_block failed: {e}")
            self._latest_tool_block = ""

        # ===== 3) 并行调用 layer1 的三个 agent（每个线程独立 client + 多 key）=====
        def _pick_key(rt: str) -> Optional[str]:
            keys = getattr(self, "_api_keys", None) or []
            if not keys:
                return None
            mapping = {"bazi": 0, "ziwei": 1, "xingpan": 2}
            idx = mapping.get(rt, 0) % len(keys)
            return keys[idx]

        def _one(rt: str) -> Tuple[str, LLMResponse]:
            role_prompt = self.roles_layer1[rt]
            user_input_i = inputs[rt]

            api_key = _pick_key(rt)
            logger.info(f"[multi-key] layer1:{rt} key=***{(api_key or '')[-4:]}")

            tmp_client = LLMClient(
                model=getattr(self.client, "model_name", None) or getattr(self.client, "model", None),
                api_key=api_key,
                base_url=os.getenv("DEEPSEEK_BASE_URL", None),
            )

            messages = [
                {"role": "system", "content": role_prompt},
                {"role": "user", "content": user_input_i},
            ]

            import time
            t0 = time.time()
            logger.info(f"[parallel] START layer1:{rt} t={t0:.3f}")

            resp = tmp_client.chat(
                message=messages,
                max_tokens=2000,
                max_retries=2,
            )

            t1 = time.time()
            logger.info(f"[parallel] END   layer1:{rt} t={t1:.3f} dt={t1 - t0:.2f}s")

            if self.log_dir:
                self._save_agent_log("layer1", rt, role_prompt, user_input_i, resp)

            return rt, resp

        with ThreadPoolExecutor(max_workers=3) as ex:
            futs = [ex.submit(_one, rt) for rt in ["bazi", "ziwei", "xingpan"]]
            for f in as_completed(futs):
                rt, resp = f.result()
                reports[rt] = resp

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

        tool_block = getattr(self, "_latest_tool_block", "")
        user_input = (
            f"{birth_info}\n"
            f"{tool_block}\n"
            "【硬约束-字段一致性】\n"
            "1) 上方《工具原文》是唯一事实源（四柱/五行局/命宫主星/行星落座等字段必须原样照抄）。\n"
            "2) 若下方报告与工具原文冲突，以工具原文为准；不确定就直接引用工具原文，禁止脑补改写。\n\n"
            f"以下是来自其他命理师的三份报告：\n{combined_reports}"
        )

        return self._run_agents_parallel(
            roles=self.roles_layer2,
            user_input=user_input,
            layer_name="layer2",
            max_tokens=2000,
            max_retries=2,
            max_workers=3,
        )

    def layer3(
        self,
        layer2_reports: Dict[str, LLMResponse],
        year: str,
        month: str,
        day: str,
        hour: str,
        minute: str = "00",
        gender: str = "女"
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
        birth_info += (
            f"\n性别：{gender}\n"
            f"【硬约束】性别={gender}。你必须以{gender}命盘解读，禁止输出与该性别相反的“女命/男命”。\n"
        )

        # 合并第二层的报告
        combined_reports = self._combine_reports(layer2_reports)

        tool_block = getattr(self, "_latest_tool_block", "")
        user_input = (
            f"{birth_info}\n"
            f"{tool_block}\n"
            "【硬约束-字段一致性】\n"
            "1) 上方《工具原文》是唯一事实源（四柱/五行局/命宫主星/行星落座等字段必须原样照抄）。\n"
            "2) 若下方综合报告与工具原文冲突，以工具原文为准；不确定就直接引用工具原文，禁止脑补改写。\n\n"
            f"以下是来自其他命理师的三份综合分析报告：\n{combined_reports}"
        )

        return self._run_agents_parallel(
            roles=self.roles_layer3,
            user_input=user_input,
            layer_name="layer3",
            max_tokens=2000,
            max_retries=2,
            max_workers=3,
        )

    def layer4(
        self,
        layer3_reports: Dict[str, LLMResponse],
        birth_info: str,
        gender: str,
        location: Optional[Dict[str, str]] = None,
        weights: Optional[Dict[str, Dict[str, int]]] = None,
    ) -> LLMResponse:
        """
        第四层（总编聚合）：按“领域权重”融合三系最终报告，生成单一最终报告。
        """
        w = weights or getattr(self, "domain_weights", None) or {
            "personality": {"bazi": 50, "ziwei": 70, "xingpan": 70},
            "wealth_career": {"bazi": 80, "ziwei": 82, "xingpan": 72},
            "fortune_cycles": {"bazi": 90, "ziwei": 85, "xingpan": 78},
        }

        weight_table = (
            "【领域权重（默认，可后续校准）】\n"
            "维度/体系 | 八字 | 紫微 | 星盘\n"
            f"性格人格   | {w['personality']['bazi']} | {w['personality']['ziwei']} | {w['personality']['xingpan']}\n"
            f"财官福禄   | {w['wealth_career']['bazi']} | {w['wealth_career']['ziwei']} | {w['wealth_career']['xingpan']}\n"
            f"大运流年   | {w['fortune_cycles']['bazi']} | {w['fortune_cycles']['ziwei']} | {w['fortune_cycles']['xingpan']}\n"
        )

        tool_block = getattr(self, "_latest_tool_block", "")
        loc_txt = f"\n出生地点：{location}" if location else ""

        combined_reports = self._combine_reports(layer3_reports)

        user_input = (
            f"{birth_info}\n"
            f"性别：{gender}{loc_txt}\n"
            f"{tool_block}\n"
            f"{weight_table}\n"
            "【输入材料】以下是三系（八字/紫微/星盘）在第三层生成的最终报告（可能存在转述误差）：\n"
            f"{combined_reports}\n\n"
            "【你的任务】你是‘总编/裁决器’，需要基于《工具原文（事实源）》与三系报告，产出一份统一的最终命理报告。\n"
            "- 输出必须分为三大板块：①性格人格 ②财官福禄 ③大运流年。每个板块内：先给结论，再给依据推导。\n"
            "- 依据推导必须引用工具事实（如四柱、命宫主星、行星落座等）作为证据锚点；工具原文未提供的字段一律不得当作事实输出。\n"
            "- 融合规则：按‘领域权重’确定主参考体系（权重最高者为主，次高者为辅）。若出现冲突：说明冲突点，并按权重选择更可信的表述；无法判断则保留分歧并提示需进一步校验。\n"
            "- 表述风格：保持专业、结构化、不过度玄学；避免空话套话；给出可执行建议与风险提示。\n"
        )

        return self._call_agent(
            self.role_layer4,
            user_input,
            max_tokens=2500,
            layer_name="layer4",
            agent_name="final",
        )


    def process(
        self,
        year: str,
        month: str,
        day: str,
        hour: str,
        minute: str = "00",
        gender: str = "女",
        location: Optional[Dict[str, str]] = None
    ) -> Dict[str, Dict[str, LLMResponse]]:
        """
        执行完整的三层处理流程。
        
        Args:
            year: 年份（字符串，如 "1990"）
            month: 月份（字符串，如 "5" 或 "05"）
            day: 日期（字符串，如 "15" 或 "05"）
            hour: 小时（字符串，如 "14" 或 "06"）
            minute: 分钟（字符串，默认为 "00"，如 "30"）
            gender: 性别（字符串，"男" 或 "女"）
            location: 出生地点（字典，格式：{"lat": "39n54", "lon": "116e23"}）
            
        Returns:
            包含三层报告的字典，结构为：
            {
                'layer1': {report_type: LLMResponse, ...},
                'layer2': {report_type: LLMResponse, ...},
                'layer3': {report_type: LLMResponse, ...}
            }
        """
        birth_info = self._format_birth_info(year, month, day, hour, minute)
        guard = (
            f"性别：{gender}\n"
            f"【硬约束】性别={gender}。你必须以{gender}命盘解读，禁止输出与该性别相反的“女命/男命”。\n"
        )
        birth_info_guarded = f"{birth_info}\n{guard}"

        # 创建日志目录（基于framework名称和时间戳）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dir_name = f"moa_layers_{timestamp}"
        self.log_dir = os.path.join('log', dir_name)
        os.makedirs(self.log_dir, exist_ok=True)
        logger.info(f"\n日志保存目录: {self.log_dir}\n")
        logger.info(f"出生信息：{birth_info}，性别：{gender}")
        if location:
            logger.info(f"出生地点：{location}")
        
        # 第一层
        logger.info("=" * 80)
        logger.info("第一层：三个独立的命理师分别分析用户输入")
        logger.info("=" * 80)
        layer1_reports = self.layer1(year, month, day, hour, minute, gender, location)
        logger.info(f"第一层完成，生成了 {len(layer1_reports)} 份报告\n")
        
        # 第二层
        logger.info("=" * 80)
        logger.info("第二层：三个命理师参考第一层的报告，生成综合分析")
        logger.info("=" * 80)
        layer2_reports = self.layer2(layer1_reports, birth_info_guarded)

        logger.info(f"第二层完成，生成了 {len(layer2_reports)} 份报告\n")
        
        # 第三层
        logger.info("=" * 80)
        logger.info("第三层：三个命理师参考第二层的报告和用户输入，生成最终报告")
        logger.info("=" * 80)
        layer3_reports = self.layer3(layer2_reports, year, month, day, hour, minute, gender)
        logger.info(f"第三层完成，生成了 {len(layer3_reports)} 份最终报告\n")

        # 第四层（总编聚合）
        logger.info("=" * 80)
        logger.info("第四层：总编聚合三系最终报告，按领域权重生成统一最终报告")
        logger.info("=" * 80)
        layer4_report = self.layer4(layer3_reports, birth_info_guarded, gender, location=location)
        logger.info("第四层完成，生成了 1 份统一最终报告\n")

        
        return {
            'layer1': layer1_reports,
            'layer2': layer2_reports,
            'layer3': layer3_reports,
            'layer4': {'final': layer4_report}
        }
    
    def get_final_reports(self, results: Dict[str, Dict[str, LLMResponse]]) -> Dict[str, str]:
        """
        从处理结果中提取最终报告。

        - 返回三系第三层最终报告：bazi / ziwei / xingpan
        - 若存在第四层聚合结果，则额外返回 final

        Args:
            results: process() 方法的返回结果

        Returns:
            包含最终报告内容的字典
        """
        layer3 = results.get('layer3', {})
        layer4 = results.get('layer4', {})
        return {
            'bazi': layer3.get('bazi', LLMResponse("", "", {}, "", 0)).content,
            'ziwei': layer3.get('ziwei', LLMResponse("", "", {}, "", 0)).content,
            'xingpan': layer3.get('xingpan', LLMResponse("", "", {}, "", 0)).content,
            'final': layer4.get('final', LLMResponse("", "", {}, "", 0)).content,
        }
