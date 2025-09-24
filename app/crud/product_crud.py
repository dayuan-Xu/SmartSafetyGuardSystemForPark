from sqlalchemy.orm import Session
from app.DB_models.product_db import ProductDB  # 数据库模型
from app.JSON_schemas.product_pydantic import ProductCreate, ProductUpdate  # 请求模型
from typing import Optional, List

# 1. 查：根据 ID 获取单个商品
def get_product(db: Session, product_id: int) -> Optional[ProductDB]:
    return db.query(ProductDB).filter(ProductDB.id == product_id).first()

# 2. 查：获取所有商品（支持分页，默认取 10 条）
def get_all_products(db: Session, skip: int = 0, limit: int = 10) -> List[ProductDB]:
    return db.query(ProductDB).offset(skip).limit(limit).all()

# 3. 增：创建新商品
def create_product(db: Session, product: ProductCreate) -> ProductDB:
    # 1. 将 Pydantic 模型（ProductCreate）转成 SQLAlchemy 模型（ProductDB）
    db_product = ProductDB(
        name=product.name,
        price=product.price,
        stock=product.stock
    )
    # 2. 提交到数据库
    db.add(db_product)
    db.commit()
    db.refresh(db_product)  # 刷新实例，获取数据库自动生成的 id 等字段
    return db_product

# 4. 改：根据 ID 修改商品
def update_product(
    db: Session,
    product_id: int,
    product_update: ProductUpdate
) -> Optional[ProductDB]:
    # 先查询商品是否存在
    db_product = get_product(db, product_id)
    if not db_product:
        return None  # 商品不存在，返回 None
    # 将更新的字段赋值给数据库实例（只更新非 None 的字段）
    update_data = product_update.model_dump(exclude_unset=True)  # 排除未传的字段
    for key, value in update_data.rows():
        setattr(db_product, key, value)
    # 提交修改
    db.commit()
    db.refresh(db_product)
    return db_product

# 5. 删：根据 ID 删除商品
def delete_product(db: Session, product_id: int) -> bool:
    db_product = get_product(db, product_id)
    if not db_product:
        return False  # 商品不存在，删除失败
    db.delete(db_product)
    db.commit()
    return True  # 删除成功