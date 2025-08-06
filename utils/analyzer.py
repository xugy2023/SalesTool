# utils/analyzer.py
import re

from utils.intent_scorer import RuleBasedIntentScorer

def analyze_sales_text(text):
    scorer = RuleBasedIntentScorer()
    result = scorer.score(text)  # 是 dict，而不是 int
    score = result.get("score", 0)

    summary = ""
    if score >= 70:
        summary = "客户表达了强烈的购买意愿，建议重点跟进。"
    elif score >= 40:
        summary = "客户有一定兴趣，可以继续跟进并推动转化。"
    elif score >= 20:
        summary = "客户态度模糊或犹豫，需进一步引导。"
    else:
        summary = "客户购买意愿较低，建议降低优先级。"

    return {
        "score": score,
        "summary": summary,
        "status": result.get("status", "低意向")
    }


# 销售关键词（正向得分）
positive_keywords = [
    "优惠", "免费", "推荐", "高性价比", "新品", "专业", "保质", "保量", "合作", "支持", "售后", "服务", "方案", "预算", "补贴", "质保"
]

# 消极或低效关键词（扣分项）
negative_keywords = [
    "不清楚", "不知道", "等通知", "以后再说", "先不考虑", "没听说", "不负责", "不是我管", "我们没做", "不好说", "不方便", "没兴趣"
]

def score_transcript(transcript: str) -> int:
    if not transcript or not isinstance(transcript, str):
        return 0
    transcript = transcript.lower()
    """
    根据正向 / 负向关键词简单打分
    """
    score = 60  # 初始分

    for keyword in positive_keywords:
        if re.search(keyword, transcript, re.IGNORECASE):
            score += 3

    for keyword in negative_keywords:
        if re.search(keyword, transcript, re.IGNORECASE):
            score -= 5

    # 限制在 [0, 100] 范围
    return max(0, min(100, score))
