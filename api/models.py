from api.database import get_db_connection

def crear_tablas():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS CLIENTE_MS (
                codigo_cli VARCHAR(50) PRIMARY KEY,
                nombre_cli VARCHAR(100),
                num_cel_cli VARCHAR(20)
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS HISTORIAL_MS (
                codigo_his SERIAL PRIMARY KEY,
                codigo_cli VARCHAR(50),
                lugar_ven VARCHAR(100),
                total_his NUMERIC(10, 2)
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS VENTA_MS (
                codigo_ven SERIAL PRIMARY KEY,
                codigo_his INT,
                codigo_pro VARCHAR(50),
                cantidad_ven INT,
                total_ven NUMERIC(10, 2)
            );
        """)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()
