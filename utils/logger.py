import os
from datetime import datetime

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "failed_analysis.log")

# 确保 logs 目录存在
os.makedirs(LOG_DIR, exist_ok=True)

def log_failed_analysis(filename, reason):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] 文件: {filename}\n原因: {reason}\n\n")
