#  告警广播服务模块
import asyncio
import threading

from app.objects.alarm_case import AlarmCase
from app.services.websocket_manager import manager
from app.utils.logger import get_logger

logger = get_logger(__name__)

# -------------------------- 全局异步广播任务处理（使用独立线程运行事件循环，避免与FastAPI主线程冲突） --------------------------
# 1. 创建独立的asyncio事件循环，专门处理WebSocket广播（避免与FastAPI主循环冲突）
broadcast_loop = asyncio.new_event_loop()
# 2. 启动事件循环的守护线程（后台运行，不阻塞主程序退出）
broadcast_thread = threading.Thread(
    target=broadcast_loop.run_forever,
    daemon=True,
    name="WebSocket-Broadcast-Loop"
)
broadcast_thread.start()

async def _async_broadcast_alarm(alarm):
    """内部异步广播告警函数（供事件循环调用）"""
    alarm_dict = {
        "alarm_id": alarm.alarm_id,
        "camera_id": alarm.camera_id,
        "alarm_type": alarm.alarm_type,
        "alarm_status": alarm.alarm_status,
        "alarm_time": alarm.alarm_time.isoformat() if alarm.alarm_time else None,
        "snapshot_url": alarm.snapshot_url,
    }
    await manager.broadcast(alarm_dict)

def sync_broadcast_alarm(alarm):
    """同步接口：将告警广播任务提交到全局事件循环（线程安全）"""
    logger.info(f"广播告警: Alarm ID={alarm.alarm_id}, 类型={AlarmCase.descs[alarm.alarm_type]}")
    asyncio.run_coroutine_threadsafe(
        _async_broadcast_alarm(alarm),
        loop=broadcast_loop
    )
