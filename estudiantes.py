from datetime import datetime

from persistencia import (
    cargar_estudiantes,
    guardar_estudiantes,
    cargar_apoderados,
    guardar_apoderados
)


AULAS = {
    "3": "Aula azul",
    "4": "Aula amarilla",
    "5": "Aula verde"
}


def normalizar(texto):
    return str(texto or "").strip()


def buscar_estudiante(codigo):
    codigo = normalizar(codigo).casefold()

    for estudiante in cargar_estudiantes():
        if normalizar(estudiante.get("codigo")).casefold() == codigo:
            return estudiante

    return None


def buscar_apoderado(dni):
    dni = normalizar(dni)

    for persona in cargar_apoderados():
        if normalizar(persona.get("dni")) == dni:
            return persona

    return None


def validar_nombre(texto, campo):
    texto = normalizar(texto)

    if not texto or not texto.replace(" ", "").isalpha():
        raise ValueError(f"El campo {campo} contiene datos no válidos.")

    return texto.title()


def validar_estudiante(datos):
    codigo = normalizar(datos.get("codigo"))
    nombres = validar_nombre(datos.get("nombres"), "nombres")
    apellidos = validar_nombre(datos.get("apellidos"), "apellidos")
    edad = normalizar(datos.get("edad"))
    seccion = normalizar(datos.get("seccion"))

    if not codigo:
        raise ValueError("Ingrese el código del estudiante.")

    if edad not in AULAS:
        raise ValueError("La edad debe ser 3, 4 o 5 años.")

    if not seccion:
        raise ValueError("Ingrese la sección del estudiante.")

    aula = AULAS[edad]

    return {
        "codigo": codigo,
        "nombres": nombres,
        "apellidos": apellidos,
        "edad": edad,
        "aula": aula,
        "seccion": seccion.upper()
    }


def validar_responsable(datos, tipo):
    dni = normalizar(datos.get("dni"))
    nombres = validar_nombre(datos.get("nombres"), "nombres")
    apellidos = validar_nombre(datos.get("apellidos"), "apellidos")
    telefono = normalizar(datos.get("telefono"))
    correo = normalizar(datos.get("correo"))
    parentesco = normalizar(datos.get("parentesco"))

    if not dni.isdigit() or len(dni) != 8:
        raise ValueError(f"El DNI del {tipo} debe contener 8 dígitos.")

    if not telefono.isdigit() or not 7 <= len(telefono) <= 15:
        raise ValueError(f"Ingrese un teléfono válido para el {tipo}.")

    if not parentesco:
        raise ValueError(f"Seleccione el parentesco del {tipo}.")

    if correo and ("@" not in correo or "." not in correo.split("@")[-1]):
        raise ValueError(f"El correo del {tipo} no es válido.")

    return {
        "dni": dni,
        "nombres": nombres,
        "apellidos": apellidos,
        "telefono": telefono,
        "correo": correo
    }, parentesco.title()


def validar_tutor_opcional(datos):
    valores = [
        normalizar(datos.get(campo))
        for campo in (
            "dni", "nombres", "apellidos",
            "telefono", "correo", "parentesco"
        )
    ]

    if not any(valores):
        return None

    return validar_responsable(datos, "tutor")


def comprobar_persona_existente(personas, persona):
    existente = next(
        (p for p in personas if p.get("dni") == persona["dni"]),
        None
    )

    if existente:
        campos = ("nombres", "apellidos", "telefono", "correo")

        if any(
            normalizar(existente.get(campo)) != persona[campo]
            for campo in campos
        ):
            raise ValueError(
                f"El DNI {persona['dni']} ya existe con otros datos. "
                "Verifique la información antes de continuar."
            )

        return existente

    return None


def registrar_estudiante_completo(datos_estudiante, datos_apoderado, datos_tutor=None):
    estudiante = validar_estudiante(datos_estudiante)
    apoderado, parentesco_apoderado = validar_responsable(
        datos_apoderado,
        "apoderado"
    )

    tutor_validado = validar_tutor_opcional(datos_tutor or {})

    estudiantes = cargar_estudiantes()
    personas = cargar_apoderados()

    if any(
        normalizar(e.get("codigo")).casefold()
        == estudiante["codigo"].casefold()
        for e in estudiantes
    ):
        raise ValueError("Ya existe un estudiante con ese código.")

    persona_apoderado = comprobar_persona_existente(
        personas,
        apoderado
    )

    persona_tutor = None
    parentesco_tutor = ""

    if tutor_validado:
        tutor, parentesco_tutor = tutor_validado

        if tutor["dni"] == apoderado["dni"]:
            persona_tutor = persona_apoderado
        else:
            persona_tutor = comprobar_persona_existente(
                personas,
                tutor
            )

    nuevos_responsables = []

    if not persona_apoderado:
        nuevos_responsables.append(apoderado)

    if tutor_validado and not persona_tutor and (
        tutor["dni"] != apoderado["dni"]
    ):
        nuevos_responsables.append(tutor)

    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

    for persona in nuevos_responsables:
        persona["estudiantes"] = [estudiante["codigo"]]
        persona["fecha_registro"] = fecha
        personas.append(persona)

    for persona in (persona_apoderado, persona_tutor):
        if persona:
            persona.setdefault("estudiantes", [])

            if estudiante["codigo"] not in persona["estudiantes"]:
                persona["estudiantes"].append(estudiante["codigo"])

    estudiante.update({
        "apoderado_dni": apoderado["dni"],
        "apoderado_parentesco": parentesco_apoderado,
        "tutor_dni": (
            tutor_validado[0]["dni"] if tutor_validado else ""
        ),
        "tutor_parentesco": parentesco_tutor,
        "fecha_registro": fecha
    })

    guardar_apoderados(personas)
    estudiantes.append(estudiante)
    guardar_estudiantes(estudiantes)

    return estudiante


# Se conserva para compatibilidad con registros anteriores.
def registrar_estudiante(datos):
    estudiante = validar_estudiante(datos)
    registros = cargar_estudiantes()

    if any(
        normalizar(e.get("codigo")).casefold()
        == estudiante["codigo"].casefold()
        for e in registros
    ):
        raise ValueError("Ya existe un estudiante con ese código.")

    estudiante["apoderados"] = []
    estudiante["fecha_registro"] = datetime.now().strftime(
        "%d/%m/%Y %H:%M"
    )

    registros.append(estudiante)
    guardar_estudiantes(registros)

    return estudiante


def registrar_apoderado(datos, codigo_estudiante):
    persona, parentesco = validar_responsable(datos, "apoderado")

    estudiantes = cargar_estudiantes()
    personas = cargar_apoderados()

    estudiante = next(
        (
            e for e in estudiantes
            if normalizar(e.get("codigo")).casefold()
            == normalizar(codigo_estudiante).casefold()
        ),
        None
    )

    if not estudiante:
        raise ValueError("No se encontró el estudiante.")

    existente = comprobar_persona_existente(personas, persona)

    if existente:
        responsable = existente
    else:
        responsable = persona
        responsable["estudiantes"] = []
        responsable["fecha_registro"] = datetime.now().strftime(
            "%d/%m/%Y %H:%M"
        )
        personas.append(responsable)

    responsable.setdefault("estudiantes", [])

    if estudiante["codigo"] not in responsable["estudiantes"]:
        responsable["estudiantes"].append(estudiante["codigo"])

    estudiante["apoderado_dni"] = persona["dni"]
    estudiante["apoderado_parentesco"] = parentesco

    guardar_apoderados(personas)
    guardar_estudiantes(estudiantes)

    return responsable, not bool(existente)


def obtener_datos_padron():
    estudiantes = cargar_estudiantes()
    responsables = cargar_apoderados()

    resultado = []

    for estudiante in estudiantes:
        apoderado = next(
            (
                p for p in responsables
                if p.get("dni") == estudiante.get("apoderado_dni")
            ),
            None
        )

        tutor = next(
            (
                p for p in responsables
                if p.get("dni") == estudiante.get("tutor_dni")
            ),
            None
        )

        fila = dict(estudiante)

        fila["apoderado"] = apoderado or {}
        fila["tutor"] = tutor or {}

        resultado.append(fila)

    return sorted(
        resultado,
        key=lambda e: (
            e.get("aula", ""),
            e.get("seccion", ""),
            e.get("apellidos", "").casefold(),
            e.get("nombres", "").casefold()
        )
    )

def editar_estudiante_completo(codigo_original, datos_estudiante, datos_apoderado, datos_tutor=None):
    estudiante_validado = validar_estudiante(datos_estudiante)

    apoderado, parentesco_apoderado = validar_responsable(
        datos_apoderado, "apoderado"
    )

    tutor_validado = validar_tutor_opcional(datos_tutor or {})

    estudiantes = cargar_estudiantes()
    personas = cargar_apoderados()

    estudiante = next(
        (
            e for e in estudiantes
            if normalizar(e.get("codigo")).casefold()
            == normalizar(codigo_original).casefold()
        ),
        None
    )

    if not estudiante:
        raise ValueError("No se encontr? el estudiante que desea editar.")

    nuevo_codigo = estudiante_validado["codigo"]

    if any(
        normalizar(e.get("codigo")).casefold() == nuevo_codigo.casefold()
        and e is not estudiante
        for e in estudiantes
    ):
        raise ValueError("Ya existe otro estudiante con ese c?digo.")

    dni_antiguos = {
        normalizar(estudiante.get("apoderado_dni")),
        normalizar(estudiante.get("tutor_dni"))
    }

    dni_antiguos.discard("")

    def obtener_persona(datos):
        existente = next(
            (p for p in personas if normalizar(p.get("dni")) == datos["dni"]),
            None
        )

        if existente:
            campos = ("nombres", "apellidos", "telefono", "correo")

            if datos["dni"] in dni_antiguos:
                existente.update(datos)
            elif any(
                normalizar(existente.get(campo)) != datos[campo]
                for campo in campos
            ):
                raise ValueError(
                    f"El DNI {datos['dni']} ya est? registrado con otros datos."
                )

            return existente

        nueva = dict(datos)
        nueva["estudiantes"] = []
        nueva["fecha_registro"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        personas.append(nueva)

        return nueva

    persona_apoderado = obtener_persona(apoderado)

    persona_tutor = None
    parentesco_tutor = ""

    if tutor_validado:
        tutor, parentesco_tutor = tutor_validado
        persona_tutor = obtener_persona(tutor)

    for persona in personas:
        relacionados = persona.setdefault("estudiantes", [])
        persona["estudiantes"] = [
            codigo for codigo in relacionados
            if normalizar(codigo).casefold()
            != normalizar(codigo_original).casefold()
        ]

    for persona in (persona_apoderado, persona_tutor):
        if persona and nuevo_codigo not in persona["estudiantes"]:
            persona["estudiantes"].append(nuevo_codigo)

    estudiante.update(estudiante_validado)

    estudiante.update({
        "apoderado_dni": apoderado["dni"],
        "apoderado_parentesco": parentesco_apoderado,
        "tutor_dni": tutor_validado[0]["dni"] if tutor_validado else "",
        "tutor_parentesco": parentesco_tutor,
        "fecha_actualizacion": datetime.now().strftime("%d/%m/%Y %H:%M")
    })

    guardar_apoderados(personas)
    guardar_estudiantes(estudiantes)

    return estudiante
