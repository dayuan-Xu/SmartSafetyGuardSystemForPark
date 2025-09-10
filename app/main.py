# 1. 项目入口：main.py
# 核心职责：
#
# 启动 FastAPI 服务；
# 注册所有业务模块的路由；
# 加载全局配置（如跨域、中间件）。
from fastapi import FastAPI
from app.api.v1.endpoints import product  # 导入商品接口路由

# 创建 FastAPI 实例
app = FastAPI(
    title="园区智能安防系统API",
    description="基于FASTAPI框架的后端服务",
    version="1.0.0"
)

# 注册路由（给接口加统一前缀 /api/v1，方便版本管理）
# 这行代码的作用是：
# 整合接口：将 product.router 中收集的所有接口注册到主应用 app 中
# 设置访问路径前缀：为所有产品相关接口添加统一前缀 /api/v1/products
# 版本管理：通过 v1 这样的版本号，方便后续升级 API 版本
app.include_router(product.router, prefix="/api/v1/products", tags=["Products"])

# 启动服务（开发环境用，生产环境用 uvicorn 命令启动）
if __name__ == "__main__":
    from app.config.database import Base, engine

    # 首次运行：创建所有数据库表（后续可注释）
    Base.metadata.create_all(bind=engine)

    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)