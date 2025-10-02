import asyncio
from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Session
from app.JSON_schemas.Result_pydantic import Result
from app.JSON_schemas.alarm_pydantic import AlarmPageResponse, AlarmResponse, AlarmReport, AlarmPercent, TopAlarmAreasReport, TopAlarmArea, TodayAlarmHandleReport
from app.crud.alarm_crud import (
    get_alarms_with_condition as crud_get_alarms_with_condition,
    delete_alarms_and_related_records as crud_delete_alarms_and_related_records,
    get_recent_unresolved_alarms as crud_get_recent_unresolved_alarms,
    get_today_alarm_counts as crud_get_today_alarm_counts,
    get_today_alarm_handle_stats as crud_get_today_alarm_handle_stats,
    get_all_alarm_counts as crud_get_all_alarm_counts,
    get_top3_alarm_areas as crud_get_top3_alarm_areas
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
            total, alarms_with_details = await asyncio.get_event_loop().run_in_executor(
                db_executor, 
                crud_get_alarms_with_condition,
                db, start_time, end_time, alarm_type, alarm_status, skip, limit
            )
            
            # 转换查询结果为AlarmResponse对象
            alarms = []
            for alarm_row in alarms_with_details:
                # 处理 SQLAlchemy 查询结果对象
                alarm_response = AlarmResponse(
                    alarm_id=alarm_row.AlarmDB.alarm_id,
                    camera_id=alarm_row.AlarmDB.camera_id,
                    alarm_type=alarm_row.AlarmDB.alarm_type,
                    alarm_status=alarm_row.AlarmDB.alarm_status,
                    alarm_time=alarm_row.AlarmDB.alarm_time,
                    alarm_end_time=alarm_row.AlarmDB.alarm_end_time,
                    snapshot_url=alarm_row.AlarmDB.snapshot_url,
                    create_time=alarm_row.AlarmDB.create_time,
                    update_time=alarm_row.AlarmDB.update_time,
                    park_area=alarm_row.park_area,
                    camera_name=alarm_row.camera_name,
                    handle_user_name=alarm_row.handle_user_name
                )
                alarms.append(alarm_response)

            return Result.SUCCESS(AlarmPageResponse(total=total, rows=alarms))
        except Exception as e:
            return Result.ERROR(f"查询告警记录失败: {str(e)}")

    @staticmethod
    async def get_recent_unresolved_alarms(db: Session, limit: int = 5) -> Result[AlarmPageResponse]:
        """
        获取最近的未解决告警记录（alarm_status in [0,2]，默认最多5条

        Args:
            db: 数据库会话
            limit: 限制返回的记录数，默认为5

        Returns:
            Result[AlarmPageResponse]: 包含最近未解决告警记录的响应对象
        """
        try:
            # 使用线程池执行数据库操作
            total, alarms_with_details = await asyncio.get_event_loop().run_in_executor(
                db_executor,
                crud_get_recent_unresolved_alarms,
                db, limit
            )

            # 转换查询结果为AlarmResponse对象
            alarms = []
            for alarm_row in alarms_with_details:
                # 处理 SQLAlchemy 查询结果对象
                alarm_response = AlarmResponse(
                    alarm_id=alarm_row.AlarmDB.alarm_id,
                    camera_id=alarm_row.AlarmDB.camera_id,
                    alarm_type=alarm_row.AlarmDB.alarm_type,
                    alarm_status=alarm_row.AlarmDB.alarm_status,
                    alarm_time=alarm_row.AlarmDB.alarm_time,
                    alarm_end_time=alarm_row.AlarmDB.alarm_end_time,
                    snapshot_url=alarm_row.AlarmDB.snapshot_url,
                    create_time=alarm_row.AlarmDB.create_time,
                    update_time=alarm_row.AlarmDB.update_time,
                    park_area=alarm_row.park_area,
                    camera_name=alarm_row.camera_name,
                    handle_user_name=alarm_row.handle_user_name
                )
                alarms.append(alarm_response)

            # 返回结果，total设为实际获取的数量
            return Result.SUCCESS(AlarmPageResponse(total=total, rows=alarms))
        except Exception as e:
            return Result.ERROR(f"查询最近未解决告警记录失败: {str(e)}")

    @staticmethod
    async def get_today_alarm_report(db: Session) -> Result[AlarmReport]:
        """
        获取本日告警统计报告

        Args:
            db: 数据库会话

        Returns:
            Result[AlarmReport]: 包含本日告警统计数据的响应对象
        """
        try:
            # 使用线程池执行数据库操作
            alarm_counts = await asyncio.get_event_loop().run_in_executor(
                db_executor,
                crud_get_today_alarm_counts,
                db
            )

            # 计算告警总数
            total_alarms = sum(alarm_number for _, alarm_number in alarm_counts)
            
            # 转换查询结果为AlarmCount对象列表，percent字段存储占比
            alarm_count_list = []
            for alarm_type, alarm_number in alarm_counts:
                if total_alarms > 0:
                    alarm_count_list.append(AlarmPercent(
                        alarm_type=alarm_type,
                        percent=round(alarm_number / total_alarms, 4)  # 保留4位小数
                    ))
                else:
                    alarm_count_list.append(AlarmPercent(
                        alarm_type=alarm_type,
                        percent=0.0
                    ))

            return Result.SUCCESS(AlarmReport(alarms=alarm_count_list))
        except Exception as e:
            return Result.ERROR(f"查询本日告警统计失败: {str(e)}")

    @staticmethod
    async def get_today_alarm_handle_report(db: Session) -> Result[TodayAlarmHandleReport]:
        """
        获取本日告警处理统计报告

        Args:
            db: 数据库会话

        Returns:
            Result[TodayAlarmHandleReport]: 包含本日告警处理统计数据的响应对象
        """
        try:
            # 使用线程池执行数据库操作
            total_count, handled_count, unhandled_count = await asyncio.get_event_loop().run_in_executor(
                db_executor,
                crud_get_today_alarm_handle_stats,
                db
            )

            # 计算处理率
            handle_rate = 0.0
            if total_count > 0:
                handle_rate = round(handled_count / total_count, 4)

            return Result.SUCCESS(TodayAlarmHandleReport(
                handle_rate=handle_rate,
                unhandled_count=unhandled_count
            ))
        except Exception as e:
            return Result.ERROR(f"查询本日告警处理统计失败: {str(e)}")

    @staticmethod
    async def get_all_alarm_report(db: Session) -> Result[AlarmReport]:
        """
        获取所有告警统计报告

        Args:
            db: 数据库会话

        Returns:
            Result[AlarmReport]: 包含所有告警统计数据的响应对象
        """
        try:
            # 使用线程池执行数据库操作
            alarm_counts = await asyncio.get_event_loop().run_in_executor(
                db_executor,
                crud_get_all_alarm_counts,
                db
            )

            # 计算告警总数
            total_alarms = sum(alarm_number for _, alarm_number in alarm_counts)
            
            # 转换查询结果为AlarmCount对象列表，percent字段存储占比
            alarm_count_list = []
            for alarm_type, alarm_number in alarm_counts:
                if total_alarms > 0:
                    alarm_count_list.append(AlarmPercent(
                        alarm_type=alarm_type,
                        percent=round(alarm_number / total_alarms, 4)  # 保留4位小数
                    ))
                else:
                    alarm_count_list.append(AlarmPercent(
                        alarm_type=alarm_type,
                        percent=0.0
                    ))

            return Result.SUCCESS(AlarmReport(alarms=alarm_count_list))
        except Exception as e:
            return Result.ERROR(f"查询所有告警统计失败: {str(e)}")

    @staticmethod
    async def get_top3_alarm_areas_report(db: Session) -> Result[TopAlarmAreasReport]:
        """
        获取告警数位居前3的园区区域统计报告

        Args:
            db: 数据库会话

        Returns:
            Result[TopAlarmAreasReport]: 包含前3个告警区域统计数据的响应对象
        """
        try:
            # 使用线程池执行数据库操作
            top_areas_data = await asyncio.get_event_loop().run_in_executor(
                db_executor,
                crud_get_top3_alarm_areas,
                db
            )

            # 转换查询结果为TopAlarmArea对象列表
            top_areas_list = []
            for park_area, alarm_count in top_areas_data:
                top_areas_list.append(TopAlarmArea(
                    park_area=park_area,
                    alarm_count=alarm_count
                ))

            return Result.SUCCESS(TopAlarmAreasReport(top_areas=top_areas_list))
        except Exception as e:
            return Result.ERROR(f"查询前3个告警区域统计失败: {str(e)}")

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