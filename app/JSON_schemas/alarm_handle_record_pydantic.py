#file:app\JSON_schemas\alarm_handle_record_pydantic.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ------------------- 响应模型（给前端返回数据的格式）-------------------
class AlarmHandleRecordResponse(BaseModel):
    handle_id: int
    alarm_id: int
    handle_time: datetime
    handler_user_id: int
    handle_action: int
    handle_content: Optional[str] = None
    handle_attachment_url: Optional[str] = None
    create_time: datetime
    update_time: datetime

    class Config:
        from_attributes = True


