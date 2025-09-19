from typing import List, Optional, Annotated
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from datetime import datetime

from app.JSON_schemas.Result_pydantic import Result
from app.JSON_schemas.alarm_pydantic import AlarmPageResponse
from app.dependencies.db import get_db
from app.services.alarm_service import AlarmService

# 创建路由实例（tags 用于 API 文档分类）
router = APIRouter()

# GET /api/v1/alarms：根据条件获取告警记录列表（支持分页）
@router.get("/", response_model=Result[AlarmPageResponse], summary="根据条件获取告警记录列表（支持分页）")
def get_alarms(
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
    return AlarmService.get_alarms_with_condition(
        db, start_time, end_time, alarm_type, alarm_status, skip, limit
    )


# DELETE /api/v1/alarms/{alarm_ids}：批量删除告警记录（同时删除关联的处理记录）
@router.delete("/{alarm_ids}", response_model=Result, summary="批量删除告警记录（同时删除关联的处理记录）")
def delete_alarms(
    alarm_ids: Annotated[str, Path(min_length=1, title="告警ID列表", description="告警ID列表，多个ID之间用英文逗号分隔")],
    db: Session = Depends(get_db)
):
    """
    批量删除告警记录（同时删除关联的处理记录）

    参数说明:
    - alarm_ids: 告警ID列表，多个ID之间用英文逗号分隔，例如: 1,2,3
    """
    return AlarmService.delete_alarms(db, alarm_ids)
