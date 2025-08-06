# routes/dashboard.py

from flask import Blueprint, render_template
from utils.cache import analysis_results
from collections import Counter

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
    emotion_trend = []
    status_counter = Counter()
    emotion_counter = Counter()
    keyword_counter = Counter()
    score_data = {"labels": [], "values": [],"reasons": []}

    keywords = ["价格", "优惠", "质量", "售后", "服务", "厂家"]
    print("当前 analysis_results 内容：", analysis_results)

    for filename, data in analysis_results.items():
        # 客户状态
        status = data.get("status", "未知")
        status_counter[status] += 1

        # 语音内容
        transcript = data.get("transcript", "")

        # 情绪计数
        if "😊" in transcript:
            emotion_counter["正面"] += 1
        elif "😠" in transcript:
            emotion_counter["负面"] += 1
        else:
            emotion_counter["中性"] += 1

        # 情绪趋势
        emotion_trend.append({
            "filename": filename,
            "positive": transcript.count("😊"),
            "negative": transcript.count("😠"),
            "neutral": transcript.count("😐"),
        })

        # 销售关键词统计
        for kw in keywords:
            keyword_counter[kw] += transcript.count(kw)

        # 打分
        feedback = data.get("feedback", {})
        score = feedback.get("score", 0)
        reason = feedback.get("reason", "无评分解释")

        score_data["labels"].append(filename)
        score_data["values"].append(score)
        score_data["reasons"].append(reason)
        print("dashboard 路由已加载")

    return render_template("dashboard.html",
        emotion_data={
            "labels": list(emotion_counter.keys()),
            "values": list(emotion_counter.values())
        },
        status_data=status_counter,
        emotion_trend_data={
            "labels": [e["filename"] for e in emotion_trend],
            "positive": [e["positive"] for e in emotion_trend],
            "neutral": [e["neutral"] for e in emotion_trend],
            "negative": [e["negative"] for e in emotion_trend],
        },
        keyword_data={
            "labels": list(keyword_counter.keys()),
            "values": list(keyword_counter.values())
        },
        score_data=score_data,
        analysis_results=analysis_results  # 用于客户列表部分
    )

