# 园区智能安防系统

基于YOLO模型的园区安全规范监测系统，使用计算机视觉技术实时检测园区内的安全隐患，包括未戴安全帽、未穿反光衣、区域入侵、火焰和烟雾等。

## 项目简介

本项目是一个智能安防监控系统，通过连接园区内的摄像头，利用YOLO目标检测模型实时分析视频流，自动识别并报警以下安全隐患：

- 安全规范违规：未戴安全帽、未穿反光衣
- 区域入侵：检测禁止进入区域的人体或车辆
- 火警隐患：检测火焰和烟雾

系统采用FastAPI构建后端服务，提供RESTful API接口，支持实时告警推送、告警处理记录、摄像头管理等功能。

### 主要功能模块

1. **视频流采集与模型推理模块**
   - 拉取指定摄像头RTSP流
   - 调用YOLOv11模型实时检测5类安全隐患场景
   - 检测到异常时触发告警并生成截图

2. **告警管理模块**
   - 告警数据存储与状态管理
   - 支持告警状态更新（未处理→处理中→已解决/误报）
   - 通过WebSocket推送实时告警到前端

3. **摄像头管理模块**
   - 摄像头基础信息CRUD操作
   - 摄像头在线/离线状态检测
   - RTSP连接测试功能

4. **用户与权限模块**
   - 用户注册、登录和JWT认证
   - 基于角色的权限控制（管理员、安保管理员、普通操作员）

5. **数据统计与分析模块**
   - 告警统计报表
   - 今日告警处理情况分析
   - 高风险区域排名

## 项目运行

### 环境要求

- Python 3.8+
- MySQL 5.7+
- pip包管理工具

### 安装步骤

1. 克隆项目代码：
   ```bash
   git clone <项目地址>
   cd PictureAnalysis
   ```

2. 创建并激活虚拟环境(windows下建议通过PyCharm自动完成该步骤)：
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

4. 配置环境变量：
   复制`.envexample`文件为`.env`，并根据实际情况修改配置：
   ```bash
   cp .envexample .env
   ```
   
   主要配置项包括：
   - 数据库连接信息（MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE）
   - 阿里云OSS配置（用于存储告警截图）
   - 安全配置（SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES）

5. 初始化数据库：
   确保MySQL服务运行正常，并使用管理工具（推荐DBeaver）完成数据库迁移，迁移脚本见app/config下的.sql文件。

6. 启动服务：
   ```bash
   python app/main.py
   ```

   或使用uvicorn命令启动：
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8089
   ```

### 项目结构

```
app/
├── api/              # API接口层
├── services/         # 业务逻辑层
├── crud/             # 数据访问层
├── DB_models/        # 数据库模型
├── JSON_schemas/     # 数据传输模型
├── config/           # 配置文件
├── dependencies/     # 依赖项
├── middleware/       # 中间件
├── utils/            # 工具类
└── main.py           # 项目入口
```

### API文档

项目启动后，可通过以下地址访问API文档：
- Swagger UI: http://localhost:8089/docs
- ReDoc: http://localhost:8089/redoc

### 登录账户

可以使用数据库管理软件（比如DBeaver），查看账户信息。