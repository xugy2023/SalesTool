# utils/cache.py

analysis_results = {}

def save_analysis(filename, transcript, feedback):
    analysis_results[filename] = {
        "transcript": transcript,
        "score": feedback.get("score", 0),
        "reason": feedback.get("reason", "无评分解释"),
        "status": feedback.get("status", "未知"),
        "feedback": feedback  # 原始反馈信息也可以保留
    }


def get_analysis(filename):
    return analysis_results.get(filename)
