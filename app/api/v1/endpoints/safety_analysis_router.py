from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.JSON_schemas.Result_pydantic import Result
from app.services.safety_analysis_service import SafetyAnalysisService
from app.services.websocket_manager import manager
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Path
from typing import Annotated

# 创建路由实例（tags 用于 API 文档分类）
router = APIRouter()

# 1. GET /api/v1/safety_analysis/start/{camera_id}：启动某个摄像头的安防分析
@router.get("/start/{camera_id}", response_model=Result, summary="启动某监控摄像头的安防分析", status_code=200)
def start_monitoring(
    camera_id: Annotated[str, Path(title="摄像头ID", description="摄像头唯一标识")],
    db: Session = Depends(get_db)
):
    """
    启动某个摄像头的安防分析功能

    Args:
        camera_id (str): 摄像头唯一标识
        db (Session): 数据库会话

    Returns:
        Result: 启动操作结果的统一响应，包含操作状态码、消息和数据
        - code: 业务状态码（1表示成功，0表示失败）
        - msg: 操作结果消息
        - data: 操作相关数据，可能包含摄像头ID、分析模式和线程信息
    """
    # 调用Service层处理所有业务逻辑
    return SafetyAnalysisService.start_safety_analysis(camera_id, db)

# 2. GET /api/v1/safety_analysis/stop/{camera_id}：关闭某个摄像头的安防分析
@router.get("/stop/{camera_id}", response_model=Result, summary="关闭某监控摄像头的安防分析", status_code=200)
def stop_monitoring(
    camera_id: Annotated[str, Path(title="摄像头ID", description="摄像头唯一标识")],
    db: Session = Depends(get_db)
):
    """
    关闭某个摄像头的安防分析功能

    Args:
        camera_id (str): 摄像头唯一标识
        db (Session): 数据库会话

    Returns:
        Result: 关闭操作结果的统一响应，包含操作状态码、消息和数据
        - code: 业务状态码（1表示成功，0表示失败）
        - msg: 操作结果消息
        - data: 操作相关数据，可能包含摄像头ID、分析模式和线程信息
    """
    return SafetyAnalysisService.stop_safety_analysis(camera_id, db)

# 3. ws://后端服务器IP:运行端口/api/v1/safety_analysis/ws :WebSocket端点, 用于建立连接，后端实时推送告警
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket端点，用于建立连接，后端实时推送告警

    Args:
        websocket (WebSocket): WebSocket连接对象
    """
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