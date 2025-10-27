from pathlib import Path
from typing import Optional

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    # Pydantic配置
    model_config = ConfigDict(
        env_file=Path(__file__).parent.parent.parent / '.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )
    
    # 数据库配置
    MYSQL_HOST: str = 'localhost'
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = 'root'
    MYSQL_PASSWORD: str = 'your_password'
    MYSQL_DATABASE: str = 'your_db_name'
    
    # 安全配置
    SECRET_KEY: str = 'da3178e5264bff377e57d669c7143baf0b37264ceb3b8a0e976a7636039e7bc6'
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 阿里云OSS配置 (使用与代码中实际使用的环境变量名称一致)
    ALI_OSS_ACCESS_KEY_ID: Optional[str] = None
    ALI_OSS_ACCESS_KEY_SECRET: Optional[str] = None
    ALIYUN_OSS_ENDPOINT: Optional[str] = None
    ALIYUN_OSS_BUCKET_NAME: Optional[str] = None
    
    # 应用配置
    SNAPSHOT_PATH: str = './snapshots/'
    
    # 兼容性属性，用于支持代码中可能使用的新名称
    @property
    def OSS_ACCESS_KEY_ID(self) -> Optional[str]:
        return self.ALI_OSS_ACCESS_KEY_ID
    
    @property
    def OSS_ACCESS_KEY_SECRET(self) -> Optional[str]:
        return self.ALI_OSS_ACCESS_KEY_SECRET
    
    @property
    def OSS_ENDPOINT(self) -> Optional[str]:
        return self.ALIYUN_OSS_ENDPOINT
    
    @property
    def OSS_BUCKET_NAME(self) -> Optional[str]:
        return self.ALIYUN_OSS_BUCKET_NAME


# 创建全局配置实例
settings = AppSettings()