# 1. 项目入口：main.py
# 核心职责：
#
# 启动 FastAPI 服务；
# 注册所有业务模块的路由；
# 加载全局配置（如跨域、中间件）。
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from app.JSON_schemas.Result_pydantic import Result
from app.JSON_schemas.security_pydantic import Token, User
from app.api.v1.endpoints import alarm_handle_record_router  # 导入报警记录接口路由
from app.api.v1.endpoints import camera_router  # 导入商品接口路由
from app.api.v1.endpoints import product  # 导入商品接口路由
from app.api.v1.endpoints import safety_detection_router  # 导入安全监测路由
from app.api.v1.endpoints import user_router  # 导入用户接口路由
from app.dependencies.db import get_db
from app.dependencies.security import get_current_active_user
from app.services.login_and_self_service import LoginAndSelfService
from app.services.thread_pool_manager import shutdown_executor
from app.utils.logger import get_logger

logger=get_logger()

@asynccontextmanager
async def lifespan(app66: FastAPI):
    # 启动前要执行的
    yield
    # 结束后要执行的
    shutdown_executor()


# 创建 FastAPI 实例
app = FastAPI(
    lifespan=lifespan,
    title="园区智能安防系统API",
    description="基于FASTAPI框架的后端服务",
    version="1.0.0"
)
# 配置允许跨域的源（前端地址）
origins = [
    "http://localhost:5173",  # 你的前端地址
    # 若需要，可添加其他允许的源，如 "http://localhost:3000" 等
]

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许指定的源
    allow_credentials=True,
    allow_methods=["*"],    # 允许所有 HTTP 方法（GET/POST 等）
    allow_headers=["*"],    # 允许所有请求头
)


# # 添加日志记录中间件（类似于Java Web中的过滤器）
# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     # 前置处理 - 请求到达时记录
#     start_time = time.time()
#     logger.info(f"收到请求: {request.method} {request.url}")
#
#     # 继续处理请求
#     response = await call_next(request)
#
#     # 后置处理 - 响应返回前记录
#     process_time = time.time() - start_time
#     logger.info(f"响应状态: {response.status_code} - 处理时间: {process_time:.4f}秒")
#
#     return response


# 注册登录、个人信息查看的路由
@app.post("/token", response_model=Result[Token])
async def login_for_access_token_endpoint(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):
    result = await LoginAndSelfService.login_for_access_token(form_data, db)
    return result

@app.get("/users/me", response_model=Result[User])
async def read_users_me_endpoint(current_user: User = Depends(get_current_active_user)):
    # 由于 current_user 已经通过依赖验证，直接传给服务层处理
    result = LoginAndSelfService.get_current_user_info(current_user)
    return result

@app.get("/users/me/items", response_model=Result)
async def read_own_items_endpoint(current_user: User = Depends(get_current_active_user)):
    # 由于 current_user 已经通过依赖验证，直接传给服务层处理
    result = LoginAndSelfService.get_current_user_items(current_user)
    return result


# 注册路由（给接口加统一前缀 /api/v1，方便版本管理）
# 这行代码的作用是：
# 整合接口：将 product.router 中收集的所有接口注册到主应用 app 中
# 设置访问路径前缀：为所有产品相关接口添加统一前缀 /api/v1/products
# 版本管理：通过 v1 这样的版本号，方便后续升级 API 版本
app.include_router(safety_detection_router.router, prefix="/api/v1/safety_analysis", tags=["安全监测"])
app.include_router(alarm_handle_record_router.router,prefix="/api/v1/alarm_handle_records",tags=["告警处理记录"])
app.include_router(user_router.router, prefix="/api/v1/users", tags=["用户信息"])
app.include_router(camera_router.router, prefix="/api/v1/cameraInfos", tags=["摄像头信息"])
app.include_router(product.router, prefix="/api/v1/products", tags=["产品信息"])

# 根路径
@app.get("/")
def read_root():
    return {"status": "运行中", "service": "YOLO安全监测系统-MVP"}

# 启动服务（开发环境用，生产环境用 uvicorn 命令启动）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="localhost", port=8089)