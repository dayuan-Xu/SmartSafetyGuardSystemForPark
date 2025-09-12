from datetime import datetime

import pytz
from sqlalchemy import Column, BigInteger, String, DateTime, Integer, Text

from app.config.database import Base


class AlarmHandleRecordDB(Base):
    __tablename__ = "alarm_handle_record"

    handle_id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)  # 处理记录唯一标识，自增
    alarm_id = Column(BigInteger, nullable=False, index=True)  # 关联的告警 ID，逻辑外键
    handle_time = Column(DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Shanghai')))  # 处理时间
    handler_user_id = Column(Integer, nullable=False)  # 处理人 ID（系统用户），逻辑外键
    handle_action = Column(Integer, nullable=False)  # 处理动作：0-标记误报， 1-派单处理， 2-标记已解决
    handle_content = Column(Text, nullable=True)  # 处理详情（如派单对象、解决措施），可为空，派单时前端自动生成处理详情
    handle_attachment_url = Column(String(255), nullable=True)  # 标记已解决时上传的附件的路径（如现场反馈照片）

    # 可选：添加默认时间字段
    create_time = Column(DateTime, default=datetime.now(pytz.timezone('Asia/Shanghai')))# 创建时间
    update_time = Column(DateTime, default=datetime.now(pytz.timezone('Asia/Shanghai')), onupdate=datetime.now(pytz.timezone('Asia/Shanghai')))# 更新时间
