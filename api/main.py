from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

# Configuración de CORS para permitir la conexión desde los archivos HTML
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cadena de conexión a Neon (reemplaza con tu URL real de Neon)
DATABASE_URL = "tu_cadena_de_conexion_de_neon_aqui"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

# 1. Endpoint para registrar o verificar al cliente
@app.post("/api/registrar_cliente")
def registrar_cliente(data: dict):
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
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

# 2. Endpoint para guardar la compra (Historial y Carrito/Venta)
@app.post("/api/comprar")
def realizar_compra(data: dict):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        codigo_cli = data.get("codigo_cli")
        lugar_ven = data.get("lugar_ven")
        total_his = data.get("total_his")
        productos = data.get("productos") # Lista de productos en el carrito

        # Insertar en HISTORIAL_MS
        cur.execute(
            "INSERT INTO HISTORIAL_MS (codigo_cli, lugar_ven, total_his) VALUES (%s, %s, %s) RETURNING codigo_his",
            (codigo_cli, lugar_ven, total_his)
        )
        codigo_his = cur.fetchone()["codigo_his"]

        # Insertar cada producto del carrito en VENTA_MS
        for item in productos:
            cur.execute(
                "INSERT INTO VENTA_MS (codigo_his, codigo_pro, cantidad_ven, total_ven) VALUES (%s, %s, %s, %s)",
                (codigo_his, item["codigo_pro"], item["cantidad_ven"], item["total_ven"])
            )

        conn.commit()
        return {"status": "success", "codigo_his": codigo_his, "mensaje": "Pedido registrado con éxito"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
