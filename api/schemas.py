from pydantic import BaseModel
from typing import Optional, List

class ClienteCreate(BaseModel):
    codigo_cli: str
    nombre_cli: str
    num_cel_cli: str

class VentaItem(BaseModel):
    codigo_pro: str
    cantidad_ven: int
    total_ven: float

class CompraCreate(BaseModel):
    codigo_cli: str
    lugar_ven: Optional[str] = "WEB"
    total_his: float
    items: List[VentaItem]
