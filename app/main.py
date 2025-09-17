# 1. 项目入口：main.py
# 核心职责：
#
# 启动 FastAPI 服务；
# 注册所有业务模块的路由；
# 加载全局配置（如跨域、中间件）。
from fastapi import FastAPI
from app.api.v1.endpoints import product  # 导入商品接口路由
from app.api.v1.endpoints import camera_router  # 导入商品接口路由
from app.api.v1.endpoints import safety_detection_router  # 导入安全监测路由
from app.api.v1.endpoints import user_router  # 导入用户接口路由
from app.api.v1.endpoints import alarm_handle_record_router #导入报警记录接口路由

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
app.include_router(safety_detection_router.router, prefix="/api/v1/safety_analysis", tags=["安全监测"])
app.include_router(alarm_handle_record_router.router,prefix="/api/v1/alarm_handle_records",tags=["告警处理记录"])
app.include_router(user_router.router, prefix="/api/v1/users", tags=["用户信息"])
app.include_router(camera_router.router, prefix="/api/v1/cameraInfos", tags=["摄像头信息"])
app.include_router(product.router, prefix="/api/v1/products", tags=["产品信息"])

# 根接口
@app.get("/")
def read_root():
    return {"status": "运行中", "service": "YOLO安全监测系统-MVP"}

# 启动服务（开发环境用，生产环境用 uvicorn 命令启动）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="localhost", port=8089)

