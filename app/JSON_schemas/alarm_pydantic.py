from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List


class AlarmBase(BaseModel):
    camera_id: int
    alarm_type: int
    alarm_status: int
    alarm_time: datetime
    alarm_end_time: Optional[datetime] = None
    snapshot_url: str


class AlarmResponse(AlarmBase):
    alarm_id: int
    create_time: datetime
    update_time: datetime

    class Config:
        from_attributes = True

class AlarmPageResponse(BaseModel):
    total: int
    alarms: List[AlarmResponse]


class AlarmQueryParams(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    alarm_type: Optional[int] = None
    alarm_status: Optional[int] = None
    skip: int = 0
    limit: int = 10
