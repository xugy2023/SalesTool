# utils/highlighter.py
import re


def highlight_keywords(text):
    if not text or not isinstance(text, str):
        return ""

    # 保存原始文本，用于大小写不敏感的匹配
    original_text = text

    positive = [
        "我们是厂家", "可以支持定制", "包安装", "全国都可以做", "用下来效果不错",
        "性价比高", "用水省", "自动化程度高", "回头客户挺多", "项目能配合",
        "这边能协调", "领导认可", "客户满意", "对接方便", "售后有保障", "系统很稳定",
        # 添加一些可能匹配的关键词
        "厂家", "专业", "设备", "联系", "需要", "可以"
    ]

    negative = [
        "太贵了", "没预算", "领导不批", "我们不搞这个", "别人做过了", "设备太复杂",
        "不想搞", "听不懂", "系统太难用", "效果一般", "以前吃过亏", "被骗过",
        "你们跟某某一样吧", "不要", "不行"
    ]

    warning = ["考虑一下", "回头", "问问", "暂时", "看看", "再说", "等等"]

    # 使用大小写不敏感的匹配，但保持原文的大小写
    result_text = original_text

    for word in positive:
        pattern = f"(?<!\\w)({re.escape(word)})(?!\\w)"
        result_text = re.sub(pattern, r'<span class="highlight-positive">\1</span>',
                             result_text, flags=re.IGNORECASE)

    for word in negative:
        pattern = f"(?<!\\w)({re.escape(word)})(?!\\w)"
        result_text = re.sub(pattern, r'<span class="highlight-negative">\1</span>',
                             result_text, flags=re.IGNORECASE)

    for word in warning:
        pattern = f"(?<!\\w)({re.escape(word)})(?!\\w)"
        result_text = re.sub(pattern, r'<span class="highlight-warning">\1</span>',
                             result_text, flags=re.IGNORECASE)

    # ✅ 关键：返回处理后的文本
    return result_text