from pathlib import Path

BASE = Path(__file__).resolve().parent

DATOS = BASE / "datos"
EXPEDIENTES = DATOS / "expedientes.json"
USUARIOS = DATOS / "usuarios.json"
ESTUDIANTES = DATOS / "estudiantes.json"
APODERADOS = DATOS / "apoderados.json"

ADJUNTOS = BASE / "documentos_adjuntos"
