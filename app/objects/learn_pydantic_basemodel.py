# 本模块解释pydantic 中BaseModel的妙用
# Pydantic 的 BaseModel 相比普通 Python 类有以下优势：
# 自动数据验证：类型检查、数据转换、自定义验证
# 序列化/反序列化：轻松在 dict、JSON 和对象间转换
# 与框架集成：FastAPI 等框架深度集成，提供自动文档生成
# 开发效率：减少样板代码，提高开发速度
# 类型安全：提供完整的类型提示支持
# 这就是为什么现代 Python 项目（特别是 API 项目）广泛使用 Pydantic 而不是普通类的原因。


from pydantic import BaseModel, field_validator
from typing import Optional
from pathlib import Path

class User(BaseModel):
    username: str
    email: Optional[str] = None
    age: int

# 自动验证数据类型
user = User(username="johndoe", email="john@example.com", age=25)
print(user.username)  # 正常工作

# 自动类型转换
user2 = User(username="janedoe", email=None, age="30")  # age 会自动转换为 int
print(user2.age)  # 输出: 30

# 验证失败会抛出异常
try:
    user3 = User(username="bob", email="not-an-email", age="not-a-number")
except ValueError as e:
    print(f"验证错误: {e}")

# -------------------------- 自定义验证详解 --------------------------
print("\n--- 自定义验证详解 ---")
print("自定义验证不仅仅是类型注释和默认值，还包括：")


# 演示自定义验证的完整示例
class UserWithValidation(BaseModel):
    username: str
    email: str
    age: int
    password: str

    # 验证用户名长度
    @field_validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('用户名长度至少为3个字符')
        if len(v) > 20:
            raise ValueError('用户名长度不能超过20个字符')
        return v

    # 验证邮箱格式
    @field_validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('邮箱格式不正确')
        return v

    # 验证年龄范围
    @field_validator('age')
    def validate_age(cls, v):
        if v < 0:
            raise ValueError('年龄不能为负数')
        if v > 150:
            raise ValueError('年龄不能超过150岁')
        return v

    # 验证密码强度
    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('密码长度至少为8个字符')
        if not any(c.isupper() for c in v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not any(c.islower() for c in v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含至少一个数字')
        return v


# 测试自定义验证
try:
    user = UserWithValidation(
        username="jo",  # 太短
        email="invalid-email",  # 格式错误
        age=200,  # 超过范围
        password="123"  # 太简单
    )
except ValueError as e:
    print(f"验证错误: {e}")

# 正确的用户数据
try:
    valid_user = UserWithValidation(
        username="johndoe",
        email="john@example.com",
        age=25,
        password="MyPassword123"
    )
    print(f"验证通过的用户: {valid_user}")
except ValueError as e:
    print(f"验证错误: {e}")

# ---------------------------------------------------------------------------------------

# 从字典创建模型
user_data = {
    "username": "alice",
    "email": "alice@example.com",
    "age": 28
}
user = User(**user_data)

# 从 JSON 创建模型
json_data = '{"username": "charlie", "email": "charlie@example.com", "age": 35}'
user = User.model_validate_json(json_data)
print(f"从JSON创建的用户: {user}")

# ---------------------------------------------------------------------------------------

user = User(username="dave", email="dave@example.com", age=40)

# 转换为字典
user_dict = user.model_dump()
print(user_dict)  # {'username': 'dave', 'email': 'dave@example.com', 'age': 40}

# 转换为 JSON
user_json = user.model_dump_json()
print(user_json)  # {"username":"dave","email":"dave@example.com","age":40}


# ----------------实际项目中的使用:Pydantic Config 配置示例------------------------------------------------------------
print("\n--- Pydantic Config 配置示例 ---")

# 使用 Path 库配置 .env 文件路径
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"

print(f"项目根目录: {project_root}")
print(f".env 文件路径: {env_path}")

# Pydantic v2 的配置方式（使用 Path）
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

# -------------------------- BaseSettings vs 直接使用 dotenv + os.getenv --------------------------
print("\n--- BaseSettings vs 直接使用 dotenv + os.getenv ---")

# 传统方式：使用 dotenv + os.getenv
"""
import os
from dotenv import load_dotenv

load_dotenv()

# 需要手动获取每个环境变量，没有类型转换和验证
database_url = os.getenv("DATABASE_URL", "sqlite:///default.db")
api_key = os.getenv("API_KEY", "default-key")
debug = os.getenv("DEBUG", "False").lower() == "true"  # 需要手动转换类型

# 没有验证机制，容易出错
"""

# Pydantic BaseSettings 方式
class ModernSettings(BaseSettings):
    # Pydantic v2 使用 model_config
    model_config = ConfigDict(
        env_file=str(env_path),  # 使用 Path 对象并转换为字符串
        env_file_encoding="utf-8",
        validate_assignment=True,
        extra="ignore"  # 忽略 .env 中没有在模型中定义的字段
    )

    # 自动类型转换和验证
    database_url: str = "sqlite:///default.db"
    api_key: str = "default-key"
    debug: bool = False

    # 可以添加自定义验证
    mysql_port: int = 3306

    # 自定义验证器示例
    @field_validator('mysql_port')
    def validate_mysql_port(cls, v):
        """验证 MySQL 端口号是否有效"""
        if not 1 <= v <= 65535:
            raise ValueError('MySQL 端口号必须在 1-65535 之间')
        if v == 3306:
            print("警告：使用默认 MySQL 端口 3306")
        return v

    # 验证器示例 - 验证数据库URL格式
    @field_validator('database_url')
    def validate_database_url(cls, v):
        """验证数据库URL格式"""
        if not v.startswith(('sqlite://', 'postgresql://', 'mysql://')):
            raise ValueError('数据库URL必须以 sqlite://, postgresql:// 或 mysql:// 开头')
        return v

    # 验证器示例 - 复杂验证
    @field_validator('api_key')
    def validate_api_key(cls, v):
        """验证API密钥长度"""
        if len(v) < 10:
            raise ValueError('API密钥长度至少为10个字符')
        return v

# 只在 .env 文件存在时才尝试创建设置实例
if env_path.exists():
    app_settings = ModernSettings()
    print(f"Pydantic v2 配置方式可用, app_settings={app_settings}")
    print(f"MySQL端口: {app_settings.mysql_port}")
else:
    print(".env 文件不存在，跳过设置加载")
    # 创建使用默认值的实例
    app_settings = ModernSettings()
    print(f"使用默认配置, app_settings={app_settings}")

# BaseSettings 的优势：
# 1. 自动类型转换：环境变量字符串自动转换为指定类型
# 2. 数据验证：确保数据符合预期格式
# 3. 默认值支持：可以设置默认值
# 4. 结构化配置：配置项有明确的结构和类型
# 5. 集成性好：与 FastAPI 等框架无缝集成
# 6. 文档友好：自动生成配置文档

# -------------------------- BaseSettings 的主要优势总结（本身就具备BaseModel的特性） --------------------------
print("\n--- BaseSettings 的主要优势 ---")
print("1. 自动类型转换：环境变量自动转换为指定类型（str→int, str→bool等）")
print("2. 数据验证：确保配置值符合预期格式和范围")
print("3. 默认值支持：可以为配置项设置默认值")
print("4. 结构化配置：配置项有明确的结构和类型")
print("5. 集成性好：与 FastAPI 等框架无缝集成")
print("6. 文档友好：自动生成配置文档")
print("7. 层次化配置：支持多种配置源（环境变量、.env文件、命令行参数等）")
print("8. 错误处理：配置错误时提供清晰的错误信息")

