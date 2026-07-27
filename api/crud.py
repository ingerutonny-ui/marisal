from api.database import get_db_connection

def registrar_cliente_db(data: dict):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        codigo_cli = data.get("codigo_cli")
        nombre_cli = data.get("nombre_cli")
        num_cel_cli = data.get("num_cel_cli")

        cur.execute(
            """
            INSERT INTO CLIENTE_MS (codigo_cli, nombre_cli, num_cel_cli) 
            VALUES (%s, %s, %s) 
            ON CONFLICT (codigo_cli) DO UPDATE 
            SET nombre_cli = EXCLUDED.nombre_cli, num_cel_cli = EXCLUDED.num_cel_cli
            """,
            (codigo_cli, nombre_cli, num_cel_cli)
        )
        conn.commit()
        return {"estado": "éxito", "mensaje": "cliente registrado correctamente"}
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
        productos = data.get("productos", [])

        cur.execute(
            """
            INSERT INTO HISTORIAL_MS (codigo_cli, lugar_ven, total_his) 
            VALUES (%s, %s, %s) RETURNING codigo_his
            """,
            (codigo_cli, lugar_ven, total_his)
        )
        codigo_his = cur.fetchone()[0]

        for prod in productos:
            codigo_pro = prod.get("codigo_pro")
            cantidad_ven = prod.get("cantidad_ven")
            total_ven = prod.get("total_ven")

            cur.execute(
                """
                INSERT INTO VENTA_MS (codigo_his, codigo_pro, cantidad_ven, total_ven) 
                VALUES (%s, %s, %s, %s)
                """,
                (codigo_his, codigo_pro, cantidad_ven, total_ven)
            )

        conn.commit()
        return {"estado": "éxito", "mensaje": "compra realizada correctamente", "codigo_his": codigo_his}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def verificar_cliente_db(codigo_cli: str):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT * FROM cliente_ms WHERE codigo_cli = %s",
            (codigo_cli,)
        )
        cliente = cur.fetchone()
        if cliente:
            return {"estado": "éxito", "mensaje": "cliente encontrado"}
        else:
            raise Exception("El código de cliente no existe en el sistema.")
    except Exception as e:
        raise e
    finally:
        cur.close()
        conn.close()
