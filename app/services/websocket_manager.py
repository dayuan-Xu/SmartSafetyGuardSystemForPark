from typing import List
from fastapi import WebSocket
from app.utils.logger import get_logger

logger = get_logger()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket连接已建立，当前连接数: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket连接已断开，当前连接数: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: dict):
        """优化：批量处理连接，失败后及时移除无效连接"""
        valid_connections = []
        for conn in self.active_connections:
            try:
                await conn.send_json(message)
                valid_connections.append(conn)
            except Exception as e:
                logger.error(f"发送消息到WebSocket连接时出错: {e}")
                continue
        self.active_connections = valid_connections
        logger.info(f"广播消息完成，有效连接数: {len(self.active_connections)}")


# 创建全局WebSocket管理器
manager = ConnectionManager()
