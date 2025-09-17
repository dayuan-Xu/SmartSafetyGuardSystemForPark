from sqlalchemy.orm import Session
from app.dependencies.db import get_db  # 获取数据库会话的依赖
from app.JSON_schemas.Result_pydantic import Result
from app.services.monitor_service import SafetyMonitorService, manager
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect


# 创建路由实例（tags 用于 API 文档分类）
router = APIRouter()

# 1. GET /api/v1/monitor/start/{camera_id}：启动某个摄像头的监控分析
@router.get("/start/{camera_id}", response_model=Result, summary="启动监控分析")
def start_monitoring(camera_id: str = "6", db: Session = Depends(get_db)):
    # 调用Service层处理所有业务逻辑
    return SafetyMonitorService.start_safety_monitor(camera_id, db)


# 2. GET /api/v1/monitor/stop/{camera_id}：关闭某个摄像头的监控分析
@router.get("/stop/{camera_id}", response_model=Result, summary="关闭监控分析")
def stop_monitoring(camera_id: str = "6", db: Session = Depends(get_db)):
    return SafetyMonitorService.stop_safety_monitor(camera_id, db)


# 3.GET /api/v1/monitor/test/{camera_id} :测试摄像头能否连接
@router.get("/test/{camera_id}", response_model=Result, summary="测试摄像头能否连接")
def test_camera_connection(camera_id: str = "6", db: Session = Depends(get_db)):
    return SafetyMonitorService.test_camera_connection(camera_id, db)

# 4. WebSocket端点：用于实时推送视频帧和告警信息
# ws://后端服务器IP:运行端口/api/v1/monitor/ws
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # 接受WebSocket连接
    await manager.connect(websocket)
    try:
        while True:
            # 保持连接活跃
            data = await websocket.receive_text()
            # 可以处理来自客户端的消息（如果需要）
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)