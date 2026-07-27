from pydantic import BaseModel
from typing import List

class ClienteSchema(BaseModel):
    codigo_cli: str
    nombre_cli: str
    num_cel_cli: str

class ProductoItem(BaseModel):
    codigo_pro: str
    cantidad_ven: int
    total_ven: float

class CompraSchema(BaseModel):
    codigo_cli: str
    lugar_ven: str
    total_his: float
    productos: List[ProductoItem]
