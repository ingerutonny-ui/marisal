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
        raise HTTPException(status_code=400, detail="Faltan datos obligatorios para el registro del producto.")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT codigo_pro FROM producto_ms WHERE codigo_pro = %s", (codigo.upper(),))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="El código de producto ya se encuentra registrado.")

        cursor.execute(
            "INSERT INTO producto_ms (codigo_pro, nombre_pro, precio_pro, imagen_pro, color_pro, cantidad_pro) VALUES (%s, %s, %s, %s, %s, %s)",
            (codigo.upper(), nombre.upper(), precio, imagen, color.upper(), cantidad)
        )
        conn.commit()
        return {
            "mensaje": "Producto registrado exitosamente",
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
