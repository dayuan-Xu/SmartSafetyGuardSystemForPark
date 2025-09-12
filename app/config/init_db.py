from app.config.database import engine
from app.DB_models import camera_info_db, alarm_db, user_db, alarm_handle_record_db

# 创建所有表
camera_info.Base.metadata.create_all(bind=engine)
alarm.Base.metadata.create_all(bind=engine)
user.Base.metadata.create_all(bind=engine)
alarm_handle_record.Base.metadata.create_all(bind=engine)

print("数据库表创建成功！")