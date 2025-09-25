from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    user_name: str
    password: str


class UserInDB(User):
    # 继承User,新增哈希化的密码
    hashed_password: str


