from fastapi import HTTPException
from api.database import get_db_connection
from api.models import Cliente, Historial, Venta

def registrar_cliente_db(data: dict):
    db = get_db_connection()
    try:
        existente = db.query(Cliente).filter(Cliente.codigo_cli == data["codigo_cli"]).first()
        if existente:
            raise HTTPException(status_code=400, detail="El código de cliente ya existe")
        
        nuevo_cliente = Cliente(
            codigo_cli=data["codigo_cli"],
            nombre_cli=data["nombre_cli"],
            num_cel_cli=data["num_cel_cli"]
        )
        db.add(nuevo_cliente)
        db.commit()
        db.refresh(nuevo_cliente)
        return {"mensaje": "Cliente registrado con éxito"}
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def verificar_cliente_db(codigo_cli: str):
    db = get_db_connection()
    try:
        cliente = db.query(Cliente).filter(Cliente.codigo_cli == codigo_cli).first()
        if cliente:
            return {"estado": "éxito", "mensaje": "cliente encontrado"}
        else:
            raise HTTPException(status_code=404, detail="El código de cliente no existe en el sistema.")
    finally:
        db.close()

def realizar_compra_db(data: dict):
    db = get_db_connection()
    try:
        nueva_historial = Historial(
            codigo_cli=data["codigo_cli"],
            lugar_ven=data.get("lugar_ven", "WEB"),
            total_his=data["total_his"]
        )
        db.add(nueva_historial)
        db.commit()
        db.refresh(nueva_historial)

        for item in data.get("items", []):
            nueva_venta = Venta(
                codigo_his=nueva_historial.codigo_his,
                codigo_pro=item["codigo_pro"],
                cantidad_ven=item["cantidad_ven"],
                total_ven=item["total_ven"]
            )
            db.add(nueva_venta)
        
        db.commit()
        return {"mensaje": "Compra realizada con éxito"}
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
