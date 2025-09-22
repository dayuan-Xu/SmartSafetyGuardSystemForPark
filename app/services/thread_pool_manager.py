from concurrent.futures import ThreadPoolExecutor

# 创建统一的线程池
executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="Worker")

__all__ = ['executor', 'shutdown_executor']

def shutdown_executor():
    executor.shutdown(wait=True)
