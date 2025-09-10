import logging
from logging.handlers import RotatingFileHandler
import os

# 创建日志目录
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# 配置日志格式
log_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# 配置文件日志（按大小切割，最大 10MB，保留 5 个备份）
file_handler = RotatingFileHandler(
    f"{LOG_DIR}/app.log", maxBytes=10*1024*1024, backupCount=5
)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

# 配置控制台日志
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.DEBUG)

# 创建日志实例（供其他模块调用）
def get_logger(name: str = "fastapi_app") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    # 避免重复添加处理器
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    return logger