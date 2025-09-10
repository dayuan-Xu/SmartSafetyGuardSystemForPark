from app.config.database import SessionLocal  # 导入数据库会话工厂

# 依赖函数：获取数据库会话（供接口调用）
def get_db():
    db = SessionLocal()  # 创建新会话
    try:
        yield db  # 把会话交给接口使用
    finally:
        db.close()  # 接口处理完后，自动关闭会话（避免连接泄漏）