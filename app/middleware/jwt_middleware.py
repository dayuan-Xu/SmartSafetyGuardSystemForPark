from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.config.app_settings import settings
from app.config.database import SessionLocal
from app.crud.user_crud import get_user_by_username
from app.JSON_schemas.Result_pydantic import Result

# 直接从settings获取安全配置
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


class JWTMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # 排除不需要认证的路径
            if request.url.path in ["/", "/docs", "/openapi.json", "/api/v1/token", "/api/v1/register"]:
                await self.app(scope, receive, send)
                return
            
            token = request.headers.get("Authorization")

            if not token or not token.startswith("Bearer "):
                # 返回统一的错误响应格式
                result = Result.ERROR(msg="Authorization请求头缺失 or 该请求头内容格式不正确(正确格式：Bearer jwt)")
                response = JSONResponse(
                    status_code=401,
                    content=result.model_dump()
                )
                await response(scope, receive, send)
                return

            token = token[7:]  # 移除 "Bearer " 前缀
            try:
                # 验证JWT令牌
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                username: str = payload.get("sub")
                if username is None:
                    result = Result.ERROR(msg="无法验证凭据")
                    response = JSONResponse(
                        status_code=401,
                        content=result.model_dump()
                    )
                    await response(scope, receive, send)
                    return

                # 获取用户信息
                db: Session = SessionLocal()
                try:
                    user = get_user_by_username(db, username)
                    if user is None:
                        result = Result.ERROR(msg="用户不存在")
                        response = JSONResponse(
                            status_code=401,
                            content=result.model_dump()
                        )
                        await response(scope, receive, send)
                        return
                    # 可以将用户信息添加到scope中供后续使用
                    scope["user"] = user
                finally:
                    db.close()
            except JWTError:
                result = Result.ERROR(msg="令牌无效或已过期")
                response = JSONResponse(
                    status_code=401,
                    content=result.model_dump()
                )
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)