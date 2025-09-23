from datetime import datetime, timedelta, timezone
import jwt
from app.config.security_config import SECRET_KEY, ALGORITHM
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    创建访问令牌
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量
        
    Returns:
        str: 编码后的JWT令牌
    """
    to_encode = data.copy()  # 保存原始的用户关键信息(明文)
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})  # 添加过期时间（合并两个dict）
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    # 生成jwt：输入payload和密钥，利用指定的签名算法生成签名，
    # JWT最终结构：签名算法信息的base64编码（也叫Header）、用户数据的base64编码（也叫Payload）、生成的签名的base64编码（也叫Signature）
    return encoded_jwt