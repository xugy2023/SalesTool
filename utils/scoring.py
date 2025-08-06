# utils/scoring.py
from .intent_scorer import RuleBasedIntentScorer
from .intent_scorer_llm import DeepseekIntentScorer


def get_combined_score(transcript):
    try:
        rule_score = RuleBasedIntentScorer().score(transcript)
        llm_score = DeepseekIntentScorer().score_intent(transcript)

        # ✅ 检查并提取分数值
        score1 = rule_score.get("score", 0)
        score2 = llm_score.get("score", 0)
        # 保证reason存在
        reason_rule = rule_score.get("reason", "无规则评分理由")
        reason_llm = llm_score.get("reason", "无LLM评分理由")

        combined_score = round((score1 * 0.4 + score2 * 0.6), 2)

        return {
            "score": combined_score,
            "summary": f"🔍 规则评分: {score1:.1f} / LLM评分: {score2:.1f} → 综合评分: {combined_score:.1f}",
            "reason": f"规则评分：{reason_rule} | LLM评分：{reason_llm}",
            "rule_score": rule_score,
            "llm_score": llm_score
        }
    except Exception as e:
        print("[混合评分异常]", e)
        return {
            "score": 0,
            "reason": f"⚠️ 混合评分失败：{e}"
        }