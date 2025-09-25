from passlib.context import CryptContext

# 密码处理上下文
# bcrypt：一种专门设计用于密码哈希的安全算法
# 使用 salt（盐值）来防止彩虹表攻击
# 具有适应性，可以调整计算复杂度来应对计算能力的提升
# 是目前推荐的密码哈希算法之一
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """
    验证明文密码与哈希密码是否匹配
    passlib库会从hashed_password字符串中自动提取出之前存储的salt
    使用提取出的salt对plain_password进行相同的哈希计算
    将计算结果与存储的哈希值进行比较
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码
        
    Returns:
        bool: 密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    获取密码的哈希值
    
    Args:
        password: 明文密码
        
    Returns:
        str: 哈希密码（明文密码加盐后的哈希值，注意这里并不是把密码加密，而是不可逆的密码哈希）
    """
    return pwd_context.hash(password)