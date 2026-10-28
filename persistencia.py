import json
from configuracion import DATOS, EXPEDIENTES, USUARIOS

def leer(ruta, defecto):
    try:
        with open(ruta, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return defecto

def guardar(ruta, datos):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    temporal = ruta.with_suffix(".tmp")
    with open(temporal, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    temporal.replace(ruta)

def preparar():
    DATOS.mkdir(parents=True, exist_ok=True)
    if not EXPEDIENTES.exists():
        guardar(EXPEDIENTES, [])
    if not USUARIOS.exists():
        guardar(USUARIOS, [
            {"usuario":"admin","clave":"admin123","rol":"Administrador"},
            {"usuario":"secretaria","clave":"secre123","rol":"Secretaría"},
            {"usuario":"direccion","clave":"direc123","rol":"Dirección"}
        ])

def cargar():
    return leer(EXPEDIENTES, [])

def guardar_todos(datos):
    guardar(EXPEDIENTES, datos)

def autenticar(usuario, clave):
    for cuenta in leer(USUARIOS, []):
        if cuenta["usuario"] == usuario and cuenta["clave"] == clave:
            return cuenta
    return None
