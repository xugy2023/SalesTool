from utils.intent_scorer import RuleBasedIntentScorer
from utils.intent_scorer_llm import DeepseekIntentScorer

# utils/hybrid_scorer.py


class HybridIntentScorer:
    def __init__(self, rule_weight=0.4, llm_weight=0.6):
        self.rule_scorer = RuleBasedIntentScorer()
        self.llm_scorer = DeepseekIntentScorer()
        self.rule_weight = rule_weight
        self.llm_weight = llm_weight

    def score(self, transcript, customer_name="客户"):
        # 规则评分
        rule_result = self.rule_scorer.score(transcript)
        rule_score = rule_result.get("score", 0)
        rule_summary = rule_result.get("summary", "")

        # LLM评分
        llm_result = self.llm_scorer.score_intent(transcript, customer_name=customer_name)
        llm_score = llm_result.get("score", 0)
        llm_reason = llm_result.get("reason", "")

        # 综合评分
        final_score = int(rule_score * self.rule_weight + llm_score * self.llm_weight)

        # 合并摘要说明
        full_reason = llm_reason or rule_summary or "暂无理由说明"

        return {
            "final_score": final_score,
            "rule_score": rule_score,
            "llm_score": llm_score,
            "reason": full_reason,
            "rule_details": rule_result.get("details", {}),
            "llm_raw": llm_result
        }