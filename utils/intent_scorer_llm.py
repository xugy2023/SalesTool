# llm_scorer.py
import os
import json
import re
from typing import Dict, Any, Optional, Union, TypedDict
from openai import OpenAI
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScoreResult(TypedDict):
    score: int
    reason: str

class DeepseekIntentScorer:
    # 系统提示常量
    SYSTEM_PROMPT = "你是专业的销售分析专家，根据通话内容判断客户购买意向并返回JSON格式结果。"

    def __init__(self, api_key: Optional[str] = None,
                 base_url: str = "https://api.deepseek.com",
                 model: str = "deepseek-chat",
                 timeout: int = 30,
                 max_retries: int = 3):
        """
        初始化DeepSeek意向评分器

        Args:
            api_key: API密钥，如果为None则从环境变量获取
            base_url: API基础URL
            model: 使用的模型名称
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("未提供 DeepSeek API Key，请设置环境变量 DEEPSEEK_API_KEY 或传入参数")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=base_url,
            timeout=timeout
        )
        self.model = model
        self.max_retries = max_retries

    def _validate_input(self, transcript: str, customer_name: str) -> None:
        """验证输入参数"""
        if not transcript or not isinstance(transcript, str):
            raise ValueError("通话内容不能为空且必须是字符串")

        if not customer_name or not isinstance(customer_name, str):
            raise ValueError("客户姓名不能为空且必须是字符串")

        # 检查内容长度，避免超出API限制
        if len(transcript) > 100000:  # 假设限制为10万字符
            logger.warning(f"通话内容过长({len(transcript)}字符)，建议分段处理")

    def _extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """从LLM响应中提取JSON内容"""
        # 尝试直接解析
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass

        # 尝试提取JSON代码块
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(json_pattern, response_text, re.DOTALL | re.IGNORECASE)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # 尝试提取花括号内容
        brace_pattern = r'\{[^{}]*"score"[^{}]*\}'
        match = re.search(brace_pattern, response_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        # 如果都失败，尝试从文本中提取数字
        score_pattern = r'(?:score|分数|评分).*?(\d+)'
        match = re.search(score_pattern, response_text, re.IGNORECASE)
        if match:
            score = int(match.group(1))
            if 0 <= score <= 100:
                return {
                    "score": score,
                    "reason": f"从响应文本中提取到分数: {response_text[:200]}..."
                }

        raise ValueError("无法从响应中提取有效的JSON或分数")

    def _validate_result(self, result: Dict[str, Any]) -> ScoreResult:
        """验证并标准化结果"""
        if not isinstance(result, dict):
            raise ValueError("结果必须是字典格式")

        score = result.get("score")
        if score is None:
            raise ValueError("结果中缺少score字段")

        # 尝试转换为整数
        try:
            score = int(float(score))  # 支持浮点数转整数
        except (ValueError, TypeError):
            raise ValueError(f"score必须是数字，当前值: {score}")

        if not (0 <= score <= 100):
            raise ValueError(f"score必须在0-100范围内，当前值: {score}")

        reason = result.get("reason", "")
        if not isinstance(reason, str):
            reason = str(reason)

        return ScoreResult(score=score, reason=reason.strip() if reason else "未提供分析理由")

    def score_intent(self, transcript: str, customer_name: str = "客户") -> ScoreResult:
        """
        评估客户购买意向

        Args:
            transcript: 通话内容
            customer_name: 客户姓名

        Returns:
            包含score和reason的字典
        """
        try:
            # 输入验证
            self._validate_input(transcript, customer_name)

            # 构建提示词
            prompt = self._build_prompt(transcript, customer_name)

            # 调用API并重试
            for attempt in range(self.max_retries):
                try:
                    response = self._call_api(prompt)
                    reply = response.choices[0].message.content.strip()

                    if not reply:
                        raise ValueError("API返回空响应")

                    # 解析响应
                    result = self._extract_json_from_response(reply)

                    # 验证结果
                    validated_result = self._validate_result(result)

                    logger.info(f"成功评分客户'{customer_name}'，分数: {validated_result['score']}")
                    return validated_result

                except Exception as e:
                    logger.warning(f"第{attempt + 1}次尝试失败: {e}")
                    if attempt == self.max_retries - 1:
                        raise
                    continue

        except Exception as e:
            logger.error(f"评分失败: {e}")
            return ScoreResult(score=0, reason=f"❌ 评分失败: {str(e)}")

    def _build_prompt(self, transcript: str, customer_name: str) -> str:
        """构建提示词"""
        return f"""你是一个专业的销售分析专家。请根据下面与客户"{customer_name}"的销售通话内容，判断该客户的购买意向。

            请从以下几个维度进行分析：
            1. 客户对产品的兴趣程度
            2. 客户提出的问题类型（价格、功能、售后等）
            3. 客户的语气和态度
            4. 客户是否有明确的购买时间计划
            5. 客户是否有预算或决策权
            
            根据分析结果，给出0-100的购买意向分数：
            - 0-20分：完全无购买意向
            - 21-40分：购买意向较低
            - 41-60分：购买意向一般
            - 61-80分：购买意向较强
            - 81-100分：购买意向非常强烈
            
            【通话内容】：
            {transcript}
            
            请严格按照以下JSON格式返回结果，不要包含任何其他内容：
            {{"score": <0-100的整数>, "reason": "详细的分析理由"}}"""

    def _call_api(self, prompt: str):
        """调用DeepSeek API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                stream=False
            )

            # 检查响应是否有效
            if not response.choices or not response.choices[0].message:
                raise ValueError("API返回了无效的响应结构")

            return response

        except Exception as e:
            logger.error(f"API调用失败: {e}")
            # 重新抛出异常，让上层处理重试逻辑
            raise

    def batch_score(self, transcripts: Dict[str, str]) -> Dict[str, ScoreResult]:
        """
        批量评分

        Args:
            transcripts: 客户名称到通话内容的映射

        Returns:
            客户名称到评分结果的映射
        """
        results = {}
        for customer_name, transcript in transcripts.items():
            try:
                result = self.score_intent(transcript, customer_name)
                results[customer_name] = result
            except Exception as e:
                logger.error(f"批量评分中客户'{customer_name}'失败: {e}")
                results[customer_name] = ScoreResult(score=0, reason=f"评分失败: {str(e)}")
        return results

