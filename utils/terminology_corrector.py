# utils/terminology_corrector.py
import re
import json
import os


class TerminologyCorrector:
    def __init__(self, dictionary_path=None):
        """
        初始化术语纠错器

        Args:
            dictionary_path: 字典文件路径，如果为None则使用默认字典
        """
        self.corrections = {}
        self.load_dictionary(dictionary_path)

    def load_dictionary(self, dictionary_path=None):
        """加载纠错字典"""
        if dictionary_path and os.path.exists(dictionary_path):
            # 从文件加载字典
            try:
                with open(dictionary_path, 'r', encoding='utf-8') as f:
                    self.corrections = json.load(f)
                print(f"✅ 成功加载术语字典: {len(self.corrections)} 条规则")
            except Exception as e:
                print(f"❌ 加载字典失败: {e}")
                self.load_default_dictionary()
        else:
            # 使用默认字典
            self.load_default_dictionary()

    def load_default_dictionary(self):
        """加载默认的行业术语纠错字典"""
        self.corrections = {
            # 水费相关
            "水费机": "水肥机",
            "水费计划": "水肥计划",
            "水费设备": "水肥设备",
            "水费系统": "水肥系统",
            "水费一体化": "水肥一体化",

            # 农业相关
            "玉苗": "玉米",
            "墓地": "亩地",
            "嵌苏膜": "滴灌膜",
            "前苏膜": "滴灌膜",
            "前速膜": "滴灌膜",

            # 设备相关
            "机器设备": "设备",
            "自动华": "自动化",
            "自动话": "自动化",
            "只能": "智能",
            "只能化": "智能化",

            # 常见错误
            "那个": "",  # 删除填充词
            "就是": "",  # 删除填充词
            "嗯": "",  # 删除填充词
            "呃": "",  # 删除填充词
            "额": "",  # 删除填充词

            # 客户相关
            "老闆": "老板",
            "老总": "老总",
            "贵信": "贵姓",

            # 公司相关
            "厂家": "厂家",
            "公司": "公司",
            "专业": "专业",

            # 动作相关
            "寻过": "询过",
            "问过": "询过",
            "联系": "联系",
            "协调": "协调",

            # 其他常见错误
            "怎么": "怎么",
            "什么": "什么",
            "多少": "多少",
            "好了": "好的",
            "行行行": "行",
            "对对对": "对",
        }
        print(f"✅ 加载默认术语字典: {len(self.corrections)} 条规则")

    def correct_text(self, text):
        if not text or not isinstance(text, str):
            return text

        corrected_text = text
        corrections_made = 0

        for wrong_term, correct_term in self.corrections.items():
            pattern = re.escape(wrong_term)
            if re.search(pattern, corrected_text):
                corrected_text = re.sub(pattern, correct_term, corrected_text)
                corrections_made += 1

        corrected_text = re.sub(r'\s+', ' ', corrected_text).strip()

        if corrections_made > 0:
            print(f"✅ 术语纠错完成: 修正了 {corrections_made} 处")

        return corrected_text

    def add_correction(self, wrong_term, correct_term):
        """动态添加纠错规则"""
        self.corrections[wrong_term] = correct_term
        print(f"✅ 添加纠错规则: '{wrong_term}' -> '{correct_term}'")

    def save_dictionary(self, file_path):
        """保存字典到文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.corrections, f, ensure_ascii=False, indent=2)
            print(f"✅ 字典已保存到: {file_path}")
        except Exception as e:
            print(f"❌ 保存字典失败: {e}")

    def get_correction_stats(self):
        """获取纠错统计信息"""
        return {
            "total_rules": len(self.corrections),
            "deletion_rules": sum(1 for v in self.corrections.values() if v == ""),
            "replacement_rules": sum(1 for v in self.corrections.values() if v != "")
        }


# 便捷函数
def correct_terminology(text, dictionary_path=None):
    """
    便捷的术语纠错函数

    Args:
        text: 待纠错的文本
        dictionary_path: 字典文件路径（可选）

    Returns:
        纠错后的文本
    """
    corrector = TerminologyCorrector(dictionary_path)
    return corrector.correct_text(text)