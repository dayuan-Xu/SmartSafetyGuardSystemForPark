from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.JSON_schemas.Result_pydantic import Result
from app.services.safety_analysis_service import SafetyAnalysisService
from app.services.websocket_manager import manager
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

# 创建路由实例（tags 用于 API 文档分类）
router = APIRouter()

# 1. GET /api/v1/safety_analysis/start/{camera_id}：启动某个摄像头的安防分析
@router.get("/start/{camera_id}", response_model=Result, summary="启动某监控摄像头的安防分析")
def start_monitoring(camera_id: str = "6", db: Session = Depends(get_db)):
    # 调用Service层处理所有业务逻辑
    return SafetyAnalysisService.start_safety_analysis(camera_id, db)

# 2. GET /api/v1/safety_analysis/stop/{camera_id}：关闭某个摄像头的安防分析
@router.get("/stop/{camera_id}", response_model=Result, summary="关闭某监控摄像头的安防分析")
def stop_monitoring(camera_id: str = "6", db: Session = Depends(get_db)):
    return SafetyAnalysisService.stop_safety_analysis(camera_id, db)

# 3. ws://后端服务器IP:运行端口/api/v1/safety_analysis/ws :WebSocket端点, 用于建立连接，后端实时推送告警
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
