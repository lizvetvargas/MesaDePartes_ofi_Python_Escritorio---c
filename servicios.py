from datetime import datetime
from persistencia import cargar, guardar_todos

ESTADOS = [
    "Recibido", "En revisión", "Observado", "Derivado",
    "En atención", "Respondido", "Finalizado", "Archivado"
]

REVISIONES = [
    "Pendiente",
    "En revisión",
    "Revisado",
    "Observado"
]

TIPOS = [
    "Matrícula", "Constancia de estudios", "Traslado",
    "Solicitud", "Justificación", "Actualización de datos", "Otro"
]

AREAS = [
    "Dirección", "Secretaría", "Administración",
    "Área académica", "Archivo"
]

PRIORIDADES = ["Normal", "Urgente", "Muy urgente"]


def fecha():
    return datetime.now().strftime("%d/%m/%Y %H:%M")


def validar(datos, codigo_actual=""):
    obligatorios = [
        "solicitante", "documento", "dni",
        "asunto", "tipo_tramite", "area_destino"
    ]

    for campo in obligatorios:
        valor = str(datos.get(campo, "") or "").strip()

        if not valor:
            raise ValueError(
                "Complete el campo: " + campo.replace("_", " ")
            )

    dni = str(datos["dni"]).strip()

    if len(dni) != 8 or not dni.isdigit():
        raise ValueError("El DNI debe contener exactamente 8 dígitos.")

    asunto = str(datos["asunto"]).strip()

    if len(asunto) < 4:
        raise ValueError("El asunto debe tener al menos 4 caracteres.")

    opciones = {
        "tipo_tramite": TIPOS,
        "area_destino": AREAS,
        "prioridad": PRIORIDADES,
        "estado": ESTADOS,
        "revision": REVISIONES
    }

    for campo, valores in opciones.items():
        valor = str(datos.get(campo, "") or "").strip()

        if valor and valor not in valores:
            raise ValueError(
                "La opción seleccionada para "
                + campo.replace("_", " ")
                + " no es válida."
            )

    for registro in cargar():
        if (
            registro.get("codigo") == datos.get("codigo")
            and registro.get("codigo") != codigo_actual
        ):
            raise ValueError("El código ya existe.")


def registrar(datos):
    registros = cargar()
    datos = dict(datos)

    validar(datos)

    numero = 1

    for registro in registros:
        try:
            numero = max(
                numero,
                int(registro["codigo"].replace("MP-", "")) + 1
            )
        except (ValueError, KeyError):
            pass

    datos["codigo"] = f"MP-{numero:05d}"
    datos["fecha"] = fecha()
    datos.setdefault("estado", "Recibido")
    datos.setdefault("revision", "Pendiente")
    datos.setdefault("prioridad", "Normal")
    datos.setdefault("responsable", "")
    datos.setdefault("observaciones", "")
    datos.setdefault("archivo", "")

    registros.append(datos)
    guardar_todos(registros)

    return datos["codigo"]


def actualizar(codigo, datos):
    registros = cargar()

    for i, registro in enumerate(registros):
        if registro.get("codigo") == codigo:
            nuevos_datos = dict(registro)
            nuevos_datos.update(datos)

            nuevos_datos["codigo"] = codigo
            nuevos_datos["fecha"] = registro.get("fecha", fecha())
            nuevos_datos.setdefault("revision", "Pendiente")

            validar(nuevos_datos, codigo)

            registros[i] = nuevos_datos
            guardar_todos(registros)
            return

    raise ValueError("Expediente no encontrado.")


def eliminar(codigo):
    registros = cargar()

    nuevos = [
        registro for registro in registros
        if registro.get("codigo") != codigo
    ]

    if len(nuevos) == len(registros):
        raise ValueError("Expediente no encontrado.")

    guardar_todos(nuevos)


def buscar(termino=""):
    termino = termino.casefold().strip()

    campos = [
        "codigo", "solicitante", "dni", "asunto",
        "tipo_tramite", "area_destino", "estado",
        "responsable", "revision"
    ]

    return [
        registro for registro in cargar()
        if not termino or any(
            termino in str(registro.get(campo, "")).casefold()
            for campo in campos
        )
    ]


def ordenar(registros, campo):
    return sorted(
        registros,
        key=lambda registro: str(
            registro.get(campo, "")
        ).casefold()
    )


def seguimiento(codigo, estado, area, responsable, nota):
    if estado not in ESTADOS:
        raise ValueError("El estado seleccionado no es válido.")

    if area not in AREAS:
        raise ValueError("El área seleccionada no es válida.")

    registros = cargar()

    for registro in registros:
        if registro.get("codigo") == codigo:
            registro["estado"] = estado
            registro["area_destino"] = area
            registro["responsable"] = responsable

            if nota:
                anterior = registro.get("observaciones", "")
                registro["observaciones"] = (
                    anterior + "\n" + nota
                ).strip()

            registro["ultima_actualizacion"] = fecha()
            guardar_todos(registros)
            return

    raise ValueError("Expediente no encontrado.")


def resumen():
    registros = cargar()

    return len(registros), {
        estado: sum(
            registro.get("estado") == estado
            for registro in registros
        )
        for estado in ESTADOS
    }


def exportar(ruta):
    import csv

    registros = cargar()

    campos = [
        "codigo", "fecha", "solicitante", "documento",
        "dni", "asunto", "tipo_tramite", "area_destino",
        "responsable", "prioridad", "estado", "revision",
        "observaciones", "archivo"
    ]

    with open(ruta, "w", newline="", encoding="utf-8-sig") as archivo:
        escritor = csv.DictWriter(
            archivo,
            fieldnames=campos,
            extrasaction="ignore"
        )

        escritor.writeheader()
        escritor.writerows(registros)

    return len(registros)