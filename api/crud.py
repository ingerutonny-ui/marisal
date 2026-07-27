from api.database import get_db_connection

def registrar_cliente_db(data: dict):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        codigo_cli = data.get("codigo_cli")
        nombre_cli = data.get("nombre_cli")
        num_cel_cli = data.get("num_cel_cli")

        cur.execute(
            "INSERT INTO CLIENTE_MS (codigo_cli, nombre_cli, num_cel_cli) VALUES (%s, %s, %s) ON CONFLICT (codigo_cli) DO NOTHING",
            (codigo_cli, nombre_cli, num_cel_cli)
        )
        conn.commit()
        return {"status": "success", "mensaje": "Cliente registrado correctamente"}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def realizar_compra_db(data: dict):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        codigo_cli = data.get("codigo_cli")
        lugar_ven = data.get("lugar_ven")
        total_his = data.get("total_his")
        productos = data.get("productos")

        cur.execute(
            "INSERT INTO HISTORIAL_MS (codigo_cli, lugar_ven, total_his) VALUES (%s, %s, %s) RETURNING codigo_his",
            (codigo_cli, lugar_ven, total_his)
        )
        codigo_his = cur.fetchone()["codigo_his"]

        for item in productos:
            cur.execute(
                "INSERT INTO VENTA_MS (codigo_his, codigo_pro, cantidad_ven, total_ven) VALUES (%s, %s, %s, %s)",
                (codigo_his, item["codigo_pro"], item["cantidad_ven"], item["total_ven"])
            )

        conn.commit()
        return {"status": "success", "codigo_his": codigo_his, "mensaje": "Pedido registrado con éxito"}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()
