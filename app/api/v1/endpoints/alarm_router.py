from datetime import datetime
from typing import Optional, Annotated, List

from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session

from app.JSON_schemas.Result_pydantic import Result
from app.JSON_schemas.alarm_pydantic import AlarmPageResponse, AlarmReport, TopAlarmAreasReport, TodayAlarmHandleReport
from app.dependencies.db import get_db
from app.services.alarm_service import AlarmService

# 创建路由实例（tags 用于 API 文档分类）
router = APIRouter()


# GET /api/v1/alarms/recent_unresolved：获取最近5条未解决的告警记录+ 未解决的告警总数
@router.get("/recent_unresolved", response_model=Result[AlarmPageResponse],
            summary="获取最近5条未解决的告警记录+ 未解决的告警总数")
async def get_recent_unresolved_alarms(
        limit: Optional[int] = Query(5, description="限制返回的记录数", le=10),
        db: Session = Depends(get_db)
):
    """
    获取最近5条未解决的告警记录（alarm_status in [0,2]）

    参数说明:
    - limit: 限制返回的记录数，最大10条，默认5条
    """
    result = await AlarmService.get_recent_unresolved_alarms(db, limit)
    return result

# GET /api/v1/alarms/today_report：获取本日告警统计
@router.get("/today_report", response_model=Result[AlarmReport], summary="获取本日告警统计（饼状图）")
async def get_today_alarm_report(
    db: Session = Depends(get_db)
):
    """
    获取本日告警统计信息，按告警类型分组
    """
    result = await AlarmService.get_today_alarm_report(db)
    return result


# GET /api/v1/alarms/all_report：获取所有告警统计
@router.get("/all_report", response_model=Result[AlarmReport], summary="获取所有告警统计（饼状图）")
async def get_all_alarm_report(
    db: Session = Depends(get_db)
):
    """
    获取所有告警统计信息，按告警类型分组
    """
    result = await AlarmService.get_all_alarm_report(db)
    return result

# GET /api/v1/alarms/top3_areas：获取告警数位居前3的园区区域统计
@router.get("/top3_areas", response_model=Result[TopAlarmAreasReport], summary="获取告警数位居前3的园区区域统计（柱状图）")
async def get_top3_alarm_areas(
    db: Session = Depends(get_db)
):
    """
    获取告警数位居前3的园区区域统计信息，如 "工地 A 区 28 次、仓库 C 区 15 次、办公区 3 次"
    """
    result = await AlarmService.get_top3_alarm_areas_report(db)
    return result


# GET /api/v1/alarms/today_handle_report：获取本日告警处理统计
@router.get("/today_handle_report", response_model=Result[TodayAlarmHandleReport], summary="获取本日告警处理统计")
async def get_today_alarm_handle_report(
    db: Session = Depends(get_db)
):
    """
    获取本日告警处理率、未处理告警数统计信息，如 "今日处理率 96%，2 条未处理"
    """
    result = await AlarmService.get_today_alarm_handle_report(db)
    return result


# GET /api/v1/alarms：根据条件获取告警记录列表（支持分页）
@router.get("/", response_model=Result[AlarmPageResponse], summary="根据条件获取告警记录列表（支持分页）")
async def get_alarms(
    start_time: Optional[datetime] = Query(None, description="告警触发时间左边界"),
    end_time: Optional[datetime] = Query(None, description="告警触发时间右边界"),
    alarm_type: Optional[int] = Query(None, description="告警类型: 0-安全规范, 1-区域入侵, 2-火警"),
    alarm_status: Optional[int] = Query(None, description="告警状态: 0-未处理, 1-确认误报, 2-处理中, 3-处理完成"),
    skip: int = Query(0, description="跳过的记录数"),
    limit: int = Query(10, description="限制返回的记录数"),
    db: Session = Depends(get_db)
):
    """
    根据条件获取告警记录列表（支持分页）

    参数说明:
    - start_time: 告警触发时间起始时间
    - end_time: 告警触发时间结束时间
    - alarm_type: 告警类型筛选
    - alarm_status: 告警状态筛选
    - skip: 分页参数，跳过的记录数
    - limit: 分页参数，限制返回的记录数
    """
    result = await AlarmService.get_alarms_with_condition(
        db, start_time, end_time, alarm_type, alarm_status, skip, limit
    )
    return result


# DELETE /api/v1/alarms/{alarm_ids}：批量删除告警记录（同时删除关联的处理记录）
@router.delete("/{alarm_ids}", response_model=Result, summary="批量删除告警记录（同时删除关联的处理记录）")
async def delete_alarms(
    alarm_ids: Annotated[str, Path(min_length=1, title="告警ID列表", description="告警ID列表，多个ID之间用英文逗号分隔")],
    db: Session = Depends(get_db)
):
    """
    批量删除告警记录（同时删除关联的处理记录）

    参数说明:
    - alarm_ids: 告警ID列表，多个ID之间用英文逗号分隔，例如: 1,2,3
    """
    result = await AlarmService.delete_alarms(db, alarm_ids)
    return result