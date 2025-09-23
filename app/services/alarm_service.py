import asyncio
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from app.JSON_schemas.Result_pydantic import Result
from app.JSON_schemas.alarm_pydantic import AlarmPageResponse
from app.crud.alarm_crud import (
    get_alarms_with_condition as crud_get_alarms_with_condition,
    delete_alarms_and_related_records as crud_delete_alarms_and_related_records
)
from app.services.thread_pool_manager import executor as db_executor


class AlarmService:
    @staticmethod
    async def get_alarms_with_condition(
        db: Session,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        alarm_type: Optional[int] = None,
        alarm_status: Optional[int] = None,
        skip: int = 0,
        limit: int = 10
    ) -> Result[AlarmPageResponse]:
        """
        根据条件获取告警记录列表（支持分页）

        Args:
            db: 数据库会话
            start_time: 告警开始时间
            end_time: 告警结束时间
            alarm_type: 告警类型
            alarm_status: 告警状态
            skip: 跳过的记录数
            limit: 限制返回的记录数

        Returns:
            Result[dict]: 包含告警记录列表的响应对象
        """
        try:
            # 使用线程池执行数据库操作
            alarms = await asyncio.get_event_loop().run_in_executor(
                db_executor, 
                crud_get_alarms_with_condition,
                db, start_time, end_time, alarm_type, alarm_status, skip, limit
            )
            total = len(alarms)

            return Result.SUCCESS(AlarmPageResponse(total=total, alarms=alarms))
        except Exception as e:
            return Result.ERROR(f"查询告警记录失败: {str(e)}")

    @staticmethod
    async def delete_alarms(db: Session, alarm_ids_str: str) -> Result:
        """
        批量删除告警记录及其关联的处理记录

        Args:
            db: 数据库会话
            alarm_ids_str: 告警ID字符串（逗号分隔）

        Returns:
            Result: 包含删除结果的响应对象
        """
        # 解析ID列表，支持单个ID或多个ID（用逗号分隔）
        try:
            ids = [int(alarm_id.strip()) for alarm_id in alarm_ids_str.split(',') if alarm_id.strip()]
            if not ids:
                return Result.ERROR("无效的ID参数")
        except ValueError:
            return Result.ERROR("ID参数格式错误，请提供有效的数字ID")

        try:
            # 使用线程池执行数据库操作
            deleted_count = await asyncio.get_event_loop().run_in_executor(
                db_executor,
                crud_delete_alarms_and_related_records,
                db, ids
            )

            # 构造并返回响应结果
            if deleted_count == 0:
                return Result.ERROR("删除失败: 没有找到指定的任意一个告警记录")
            elif deleted_count < len(ids):
                return Result.SUCCESS(
                    {"deleted_count": deleted_count},
                    f"部分删除成功: 成功删除{deleted_count}条记录"
                )
            else:
                return Result.SUCCESS(
                    {"deleted_count": deleted_count},
                    f"批量删除成功: 共删除{deleted_count}条记录"
                )
        except Exception as e:
            return Result.ERROR(f"删除告警记录时发生错误: {str(e)}")