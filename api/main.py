import os
import psycopg2
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL no configurada")
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require", connect_timeout=10)
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de conexión: {str(e)}")

@app.get("/api/verificar_cliente/{codigo}")
def verificar_cliente(codigo: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT codigo_cli, nombre_cli, num_cel_cli FROM cliente_ms WHERE codigo_cli = %s",
            (codigo.upper(),)
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="El código de cliente no existe en el sistema.")
        return {
            "codigo": row[0],
            "nombre": row[1],
            "celular": row[2]
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/api/registrar_cliente")
def registrar_cliente(data: dict):
    codigo = data.get("codigo_cli")
    nombre = data.get("nombre_cli")
    celular = data.get("num_cel_cli")

    if not codigo or not nombre or not celular:
        raise HTTPException(status_code=400, detail="Faltan datos obligatorios para el registro.")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT codigo_cli FROM cliente_ms WHERE codigo_cli = %s", (codigo.upper(),))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="El código de cliente ya se encuentra registrado.")

        cursor.execute(
            "INSERT INTO cliente_ms (codigo_cli, nombre_cli, num_cel_cli) VALUES (%s, %s, %s)",
            (codigo.upper(), nombre.upper(), celular.upper())
        )
        conn.commit()
        return {
            "mensaje": "Cliente registrado exitosamente",
            "codigo": codigo.upper()
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/api/registrar_producto")
def registrar_producto(data: dict):
    codigo = data.get("codigo_pro")
    nombre = data.get("nombre_pro")
    precio = data.get("precio_pro")
    imagen = data.get("imagen_pro")
    color = data.get("color_pro")
    cantidad = data.get("cantidad_pro")

    if not codigo or not nombre or precio is None or not imagen or not color or cantidad is None:
        raise HTTPException(status_code=400, detail="Faltan datos obligatorios.")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM producto_ms WHERE codigo_pro = %s", (str(codigo).upper(),))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="El código de producto ya se encuentra registrado.")

        cursor.execute(
            """
            INSERT INTO producto_ms (codigo_pro, nombre_pro, precio_pro, imagen_pro, color_pro, cantidad_pro) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (str(codigo).upper(), str(nombre).upper(), float(precio), str(imagen), str(color).upper(), int(cantidad))
        )
        conn.commit()
        return {
            "mensaje": "Producto registrado exitosamente",
            "codigo": str(codigo).upper()
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/api/listar_productos")
def listar_productos():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT codigo_pro, nombre_pro, precio_pro, imagen_pro, color_pro, cantidad_pro FROM producto_ms")
        rows = cursor.fetchall()
        productos = []
        for row in rows:
            productos.append({
                "codigo_pro": row[0],
                "nombre_pro": row[1],
                "precio_pro": float(row[2]) if row[2] is not None else 0.0,
                "imagen_pro": row[3],
                "color_pro": row[4],
                "cantidad_pro": row[5]
            })
        return productos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.delete("/api/eliminar_producto/{codigo}")
def eliminar_producto(codigo: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        codigo_upper = codigo.upper()
        # Primero eliminar los registros de ventas asociados para evitar conflicto de llave foránea
        cursor.execute("DELETE FROM venta_ms WHERE codigo_pro = %s", (codigo_upper,))
        
        # Luego eliminar el producto
        cursor.execute("DELETE FROM producto_ms WHERE codigo_pro = %s", (codigo_upper,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
            
        return {"mensaje": "Producto eliminado exitosamente"}
    except HTTPException as he:
        raise he
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/api/actualizar_stock")
def actualizar_stock(data: dict):
    codigo = data.get("codigo_pro")
    cantidad = data.get("cantidad_pro")

    if not codigo or cantidad is None:
        raise HTTPException(status_code=400, detail="Faltan datos obligatorios.")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Verificar si el producto existe
        cursor.execute("SELECT * FROM producto_ms WHERE codigo_pro = %s", (str(codigo).upper(),))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="El producto no existe.")

        # Actualizar el stock
        cursor.execute(
            """
            UPDATE producto_ms 
            SET cantidad_pro = %s 
            WHERE codigo_pro = %s
            """,
            (int(cantidad), str(codigo).upper())
        )
        conn.commit()
        return {
            "mensaje": "Stock actualizado exitosamente",
            "codigo": str(codigo).upper(),
            "nuevo_stock": int(cantidad)
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@app.post("/api/registrar_historial")
def registrar_historial(data: dict):
    codigo_cli = data.get("codigo_cli")
    lugar_ven = data.get("lugar_ven")
    total_his = data.get("total_his")
    detalles = data.get("detalles", [])

    if not codigo_cli or not lugar_ven or total_his is None:
        raise HTTPException(status_code=400, detail="Faltan datos obligatorios para el historial.")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO historial_ms (codigo_cli, lugar_ven, total_his)
            VALUES (%s, %s, %s)
            RETURNING codigo_his
            """,
            (str(codigo_cli).upper(), str(lugar_ven).upper(), float(total_his))
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=500, detail="No se pudo generar el código de historial.")
        
        codigo_his = row[0]

        for item in detalles:
            codigo_pro = item.get("codigo_pro")
            cantidad_ven = item.get("cantidad_ven")
            total_ven = item.get("total_ven")

            if not codigo_pro or cantidad_ven is None or total_ven is None:
                continue

            cursor.execute(
                """
                INSERT INTO venta_ms (codigo_his, codigo_pro, cantidad_ven, total_ven)
                VALUES (%s, %s, %s, %s)
                """,
                (int(codigo_his), str(codigo_pro).upper(), int(cantidad_ven), float(total_ven))
            )

        conn.commit()
        return {
            "mensaje": "Historial y ventas registrados exitosamente",
            "codigo_his": codigo_his
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/api/factura_reciente/{codigo_cli}")
def factura_reciente(codigo_cli: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Buscar el último historial del cliente
        cursor.execute(
            """
            SELECT h.codigo_his, h.fecha_his, h.lugar_ven, h.total_his, 
                   c.nombre_cli, c.num_cel_cli, c.codigo_cli
            FROM historial_ms h
            JOIN cliente_ms c ON h.codigo_cli = c.codigo_cli
            WHERE h.codigo_cli = %s
            ORDER BY h.codigo_his DESC
            LIMIT 1
            """,
            (codigo_cli.upper(),)
        )
        historial = cursor.fetchone()
        if not historial:
            raise HTTPException(status_code=404, detail="No hay historiales para este cliente.")

        codigo_his = historial[0]

        # Buscar los detalles de la venta
        cursor.execute(
            """
            SELECT p.nombre_pro, v.cantidad_ven, (v.total_ven / v.cantidad_ven) as precio_unitario, v.total_ven
            FROM venta_ms v
            JOIN producto_ms p ON v.codigo_pro = p.codigo_pro
            WHERE v.codigo_his = %s
            """,
            (codigo_his,)
        )
        items = cursor.fetchall()
        detalles = []
        for item in items:
            detalles.append({
                "detalle": item[0],
                "cantidad": item[1],
                "precio": float(item[2]),
                "total": float(item[3])
            })

        return {
            "codigo_his": codigo_his,
            "fecha": str(historial[1]),
            "lugar": historial[2],
            "total_his": float(historial[3]),
            "cliente": {
                "nombre": historial[4],
                "celular": historial[5],
                "codigo": historial[6]
            },
            "detalles": detalles
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/api/cancelar_compra/{codigo_his}")
def cancelar_compra(codigo_his: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Obtener los detalles de la venta asociada a este historial
        cursor.execute("SELECT codigo_pro, cantidad_ven FROM venta_ms WHERE codigo_his = %s", (codigo_his,))
        detalles = cursor.fetchall()

        # Devolver el stock a cada producto
        for detalle in detalles:
            codigo_pro, cantidad_ven = detalle[0], detalle[1]
            cursor.execute(
                "UPDATE producto_ms SET cantidad_pro = cantidad_pro + %s WHERE codigo_pro = %s",
                (cantidad_ven, codigo_pro)
            )

        # Eliminar los registros de venta y el historial temporal
        cursor.execute("DELETE FROM venta_ms WHERE codigo_his = %s", (codigo_his,))
        cursor.execute("DELETE FROM historial_ms WHERE codigo_his = %s", (codigo_his,))
        conn.commit()

        return {"message": "Compra cancelada y stock devuelto con éxito."}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@app.get("/api/listar_clientes_con_compras")
def listar_clientes_con_compras():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 1. Obtener todos los clientes usando el nombre de columna real (num_cel_cli)
        cursor.execute("SELECT codigo_cli, nombre_cli, num_cel_cli FROM cliente_ms")
        clientes_db = cursor.fetchall()
        
        resultado = []
        for cli in clientes_db:
            codigo_cli, nombre_cli, celular_cli = cli
            
            # 2. Obtener el historial de compras usando codigo_his
            cursor.execute("""
                SELECT codigo_his, fecha_his, lugar_ven, total_his 
                FROM historial_ms 
                WHERE codigo_cli = %s
            """, (codigo_cli,))
            historiales_db = cursor.fetchall()
            
            lista_historial = []
            for his in historiales_db:
                id_his, fecha_his, lugar_ven, total_his = his
                
                # 3. Obtener los detalles desde la tabla venta_ms
                cursor.execute("""
                    SELECT codigo_pro, cantidad_ven, total_ven 
                    FROM venta_ms 
                    WHERE codigo_his = %s
                """, (id_his,))
                detalles_db = cursor.fetchall()
                
                lista_detalles = [
                    {
                        "codigo_pro": d[0], 
                        "cantidad_ven": d[1], 
                        "total_ven": float(d[2]) if d[2] is not None else 0.0
                    } 
                    for d in detalles_db
                ]
                
                lista_historial.append({
                    "id_his": id_his,
                    "fecha_his": str(fecha_his),
                    "lugar_ven": lugar_ven,
                    "total_his": float(total_his) if total_his is not None else 0.0,
                    "detalles": lista_detalles
                })
                
            resultado.append({
                "codigo_cli": codigo_cli,
                "nombre_cli": nombre_cli,
                "celular_cli": celular_cli,
                "historial": lista_historial
            })
            
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
