# 接口路由：api/
# 核心职责：
#
# 定义 API 接口的路径、请求方法（GET/POST/PUT/DELETE）；
# 调用依赖项（如获取数据库会话 db）；
# 接收前端请求，调用 crud 函数处理数据；
# 返回符合 JSON_schemas 模型的响应（自动序列化）。
#
# 关键文件：api/v1/endpoints/product.py（商品接口）：