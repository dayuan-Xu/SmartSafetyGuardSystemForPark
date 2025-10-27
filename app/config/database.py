from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config.app_settings import settings

# 数据库连接URL
SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
    "?charset=utf8mb4"
)

# 创建引擎
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# 基类
Base = declarative_base()