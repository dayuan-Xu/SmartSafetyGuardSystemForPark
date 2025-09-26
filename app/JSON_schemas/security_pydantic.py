from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    
    class Config:
        # API 文档示例数据
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VybmFtZSIsImV4cCI6MTUxNjIzOTAyMn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
                "token_type": "bearer"
            }
        }


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    user_name: str
    password: str


class UserInDB(User):
    # 继承User,新增哈希化的密码
    hashed_password: str