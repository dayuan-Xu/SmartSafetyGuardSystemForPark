from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# 导入依赖、CRUD 函数、模型
from app.dependencies.db import get_db  # 获取数据库会话的依赖
from app.crud.product_crud import (
    get_product, get_all_products, create_product, update_product, delete_product
)
from app.JSON_schemas.product_pydantic import ProductResponse, ProductCreate, ProductUpdate

# 创建路由实例（tags 用于 API 文档分类）
# 这个 router 实例的作用是：
# 收集接口：把当前文件中定义的所有接口（如获取商品、创建商品等）收集到一起
# 统一管理：为这些接口添加统一的标签（tags=["Products"]），方便在 API 文档中分类显示
# 便于注册：作为一个整体，可以被 main.py 一次性注册到主应用中
router = APIRouter()

# 1. GET /api/v1/products/{product_id}：获取单个商品
@router.get("/{product_id}", response_model=ProductResponse)
def read_product(
    product_id: int,
    db: Session = Depends(get_db)  # 依赖注入：自动获取数据库会话
):
    db_product = get_product(db, product_id)
    if not db_product:
        # 抛出 404 错误（FastAPI 自动处理错误响应格式）
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    return db_product  # 自动转成 ProductResponse 格式返回

# 2. GET /api/v1/products：获取所有商品（支持分页）
@router.get("/", response_model=List[ProductResponse])
def read_all_products(
    skip: int = 0,  # 跳过前 N 条（默认 0）
    limit: int = 10,  # 最多返回 N 条（默认 10）
    db: Session = Depends(get_db)
):
    products = get_all_products(db, skip=skip, limit=limit)
    return products

# 3. POST /api/v1/products：创建新商品
@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_new_product(
    product: ProductCreate,  # 自动校验请求体（符合 ProductCreate 模型）
    db: Session = Depends(get_db)
):
    return create_product(db, product)  # 调用 CRUD 函数创建商品

# 4. PUT /api/v1/products/{product_id}：修改商品
@router.put("/{product_id}", response_model=ProductResponse)
def update_existing_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db)
):
    db_product = update_product(db, product_id, product_update)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    return db_product

# 5. DELETE /api/v1/products/{product_id}：删除商品
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    success = delete_product(db, product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    return  # 204 状态码不需要返回内容