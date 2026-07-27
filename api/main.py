from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.models import crear_tablas
from api.crud import registrar_cliente_db, realizar_compra_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    crear_tablas()

@app.post("/api/registrar_cliente")
def registrar_cliente(data: dict):
    try:
        return registrar_cliente_db(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/comprar")
def realizar_compra(data: dict):
    try:
        return realizar_compra_db(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
