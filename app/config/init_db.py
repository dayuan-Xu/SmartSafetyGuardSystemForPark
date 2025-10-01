from app.config.database import engine
from app.DB_models import camera_info_db, alarm_db, user_db, alarm_handle_record_db, park_area_db

# 创建所有表
# park_area_db.Base.metadata.create_all(bind=engine)
# camera_info_db.Base.metadata.create_all(bind=engine)
# alarm_db.Base.metadata.create_all(bind=engine)
# user_db.Base.metadata.create_all(bind=engine)
# alarm_handle_record_db.Base.metadata.create_all(bind=engine)

print("数据库表创建成功！")