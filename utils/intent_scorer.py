# intent_scorer.py

import re

class RuleBasedIntentScorer:
    """
    客户意向评分类（基于规则）
    """
    def __init__(self):
        # 强意向关键词
        self.strong_intent_keywords = [
            r"(我\s*想\s*买)",
            r"(打算\s*装)",
            r"(你\s*微信\s*发我)",
            r"(加\s*你\s*微信)",
            r"(我们\s*地\s*太\s*多)",
            r"(后续\s*联系)"
        ]

        # 明确拒绝关键词
        self.no_intent_keywords = [
            r"(不用了)",
            r"(没\s*兴趣)",
            r"(今年\s*不\s*装)",
            r"(后面\s*再说)",
            r"(我\s*再\s*看看)"
        ]

        # 模糊表达关键词
        self.weak_intent_keywords = [
            r"(再说吧)",
            r"(我\s*考虑\s*一下)",
            r"(你\s*发资料我看看)"
        ]

    def score(self, transcript: str) -> dict:
        score = 50  # 基础分
        level = "中性"
        matched = []

        for pattern in self.strong_intent_keywords:
            if re.search(pattern, transcript):
                score += 20
                matched.append(f"强意向: {pattern}")

        for pattern in self.no_intent_keywords:
            if re.search(pattern, transcript):
                score -= 30
                matched.append(f"无意向: {pattern}")

        for pattern in self.weak_intent_keywords:
            if re.search(pattern, transcript):
                score -= 10
                matched.append(f"模糊意向: {pattern}")

        # 界定意向等级
        if score >= 80:
            level = "强意向"
        elif score >= 60:
            level = "中等意向"
        elif score >= 40:
            level = "弱意向"
        else:
            level = "无意向"

        return {
            "score": max(0, min(score, 100)),
            "intention_level": level,
            "matched_rules": matched
        }
