# utils/status_detector.py

def detect_customer_status(text):
    """
    根据文本内容判断客户状态：有意向、保持联系、无意向。
    """
    text = text.lower()

    positive_keywords = ["加微信", "发我资料", "发报价", "稍后联系", "方便加微信", "有需要再联系", "加个微信", "我再看一下", "你发我"]
    neutral_keywords = ["再联系", "改天聊", "不确定", "考虑下", "没决定", "等通知"]
    negative_keywords = ["不需要", "没预算", "不考虑", "做完了", "没时间", "不感兴趣", "不用了", "不做了", "已经合作", "已找别家"]

    if any(k in text for k in positive_keywords):
        return "有意向"
    elif any(k in text for k in negative_keywords):
        return "无意向"
    elif any(k in text for k in neutral_keywords):
        return "保持联系"
    else:
        return "保持联系"  # 默认状态
