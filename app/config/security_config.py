import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 安全配置
SECRET_KEY = os.getenv("SECRET_KEY", "da3178e5264bff377e57d669c7143baf0b37264ceb3b8a0e976a7636039e7bc6")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))