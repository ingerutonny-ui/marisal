from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from .database import Base

class Cliente(Base):
    __tablename__ = "cliente_ms"
    
    codigo_cli = Column(String(50), primary_key=True, index=True)
    nombre_cli = Column(String(100))
    num_cel_cli = Column(String(20))

class Producto(Base):
    __tablename__ = "producto_ms"
    
    codigo_pro = Column(String(50), primary_key=True, index=True)
    nombre_pro = Column(String(100))
    precio_pro = Column(Numeric(10, 2))

class Historial(Base):
    __tablename__ = "historial_ms"
    
    codigo_his = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo_cli = Column(String(50), ForeignKey("cliente_ms.codigo_cli"))
    lugar_ven = Column(String(100))
    total_his = Column(Numeric(10, 2))

class Venta(Base):
    __tablename__ = "venta_ms"
    
    codigo_ven = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo_his = Column(Integer, ForeignKey("historial_ms.codigo_his"))
    codigo_pro = Column(String(50), ForeignKey("producto_ms.codigo_pro"))
    cantidad_ven = Column(Integer)
    total_ven = Column(Numeric(10, 2))
