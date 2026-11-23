from datetime import datetime
from persistencia import cargar, guardar_todos


def archivar(codigo, responsable=""):
    registros = cargar()

    for registro in registros:
        if registro.get("codigo") == codigo:

            if registro.get("estado") == "Archivado":
                raise ValueError("El expediente ya se encuentra archivado.")

            if registro.get("estado") != "Finalizado":
                raise ValueError(
                    "Solo se pueden archivar expedientes finalizados."
                )

            registro["estado_anterior_archivo"] = registro.get("estado")
            registro["estado"] = "Archivado"
            registro["fecha_archivo"] = datetime.now().strftime(
                "%d/%m/%Y %H:%M"
            )
            registro["archivado_por"] = responsable

            guardar_todos(registros)
            return codigo

    raise ValueError("Expediente no encontrado.")


def listar_archivados():
    return [
        registro for registro in cargar()
        if registro.get("estado") == "Archivado"
    ]


def buscar_archivados(termino=""):
    termino = str(termino).casefold().strip()

    campos = [
        "codigo", "solicitante", "dni", "asunto",
        "tipo_tramite", "area_destino", "responsable",
        "fecha", "fecha_archivo", "archivado_por"
    ]

    return [
        registro
        for registro in listar_archivados()
        if not termino or any(
            termino in str(registro.get(campo, "")).casefold()
            for campo in campos
        )
    ]
