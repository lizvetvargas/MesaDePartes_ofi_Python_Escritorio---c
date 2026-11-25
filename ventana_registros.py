import tkinter as tk
from tkinter import ttk, messagebox

from estudiantes import (
    registrar_estudiante_completo,
    editar_estudiante_completo,
    obtener_datos_padron
)


VERDE_OSCURO = "#174D38"
VERDE = "#347A59"
VERDE_CLARO = "#DCEBDD"
CREMA = "#F5F3E9"
BLANCO = "#FFFFFF"
TEXTO = "#263B30"
GRIS = "#64756B"
DORADO = "#C6A45C"


def preparar_ventana(ventana, titulo, ancho, alto):
    ventana.title(titulo)
    ventana.configure(bg=CREMA)
    ventana.geometry(f"{ancho}x{alto}")
    ventana.minsize(850, 600)

    cabecera = tk.Frame(ventana, bg=VERDE_OSCURO, height=65)
    cabecera.pack(fill="x")
    cabecera.pack_propagate(False)

    tk.Label(
        cabecera,
        text=titulo.upper(),
        bg=VERDE_OSCURO,
        fg=BLANCO,
        font=("Segoe UI", 14, "bold")
    ).pack(expand=True)


def crear_campo(panel, fila, etiqueta, variable, opciones=None):
    tk.Label(
        panel,
        text=etiqueta,
        bg=BLANCO,
        fg=TEXTO,
        font=("Segoe UI", 9, "bold")
    ).grid(row=fila, column=0, sticky="w", padx=10, pady=7)

    if opciones:
        campo = ttk.Combobox(
            panel,
            textvariable=variable,
            values=opciones,
            state="readonly",
            width=30
        )
    else:
        campo = ttk.Entry(
            panel,
            textvariable=variable,
            width=33
        )

    campo.grid(row=fila, column=1, sticky="ew", padx=10, pady=7)
    return campo


def crear_seccion_formulario(contenedor, titulo):
    seccion = tk.LabelFrame(
        contenedor,
        text=titulo,
        bg=BLANCO,
        fg=VERDE_OSCURO,
        font=("Segoe UI", 10, "bold"),
        padx=12,
        pady=10
    )
    seccion.pack(fill="x", padx=15, pady=9)
    seccion.columnconfigure(1, weight=1)
    return seccion


def crear_responsable(contenedor, titulo, prefijo, opcional=False):
    seccion = crear_seccion_formulario(contenedor, titulo)

    variables = {
        "dni": tk.StringVar(),
        "nombres": tk.StringVar(),
        "apellidos": tk.StringVar(),
        "telefono": tk.StringVar(),
        "correo": tk.StringVar(),
        "parentesco": tk.StringVar()
    }

    campos = [
        ("DNI", "dni"),
        ("Nombres", "nombres"),
        ("Apellidos", "apellidos"),
        ("Teléfono", "telefono"),
        ("Correo electrónico", "correo"),
        ("Parentesco", "parentesco")
    ]

    for fila, (etiqueta, clave) in enumerate(campos):
        nombre = etiqueta

        if clave == "correo":
            nombre += " (opcional)"

        crear_campo(
            seccion,
            fila,
            nombre,
            variables[clave],
            (
                ["Madre", "Padre", "Abuelo/a", "Hermano/a", "Tío/a", "Otro"]
                if clave == "parentesco" else None
            )
        )

    return variables


def abrir_estudiante(raiz):
    ventana = tk.Toplevel(raiz)
    preparar_ventana(
        ventana,
        "Registro de estudiante y responsables",
        850,
        780
    )

    contenedor_principal = tk.Frame(ventana, bg=CREMA)
    contenedor_principal.pack(fill="both", expand=True)

    canvas = tk.Canvas(
        contenedor_principal,
        bg=CREMA,
        highlightthickness=0
    )

    barra = ttk.Scrollbar(
        contenedor_principal,
        orient="vertical",
        command=canvas.yview
    )

    canvas.configure(yscrollcommand=barra.set)

    barra.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    contenido = tk.Frame(canvas, bg=CREMA)
    ventana_canvas = canvas.create_window(
        (0, 0),
        window=contenido,
        anchor="nw"
    )

    def ajustar_contenido(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def ajustar_ancho(event):
        canvas.itemconfigure(ventana_canvas, width=event.width)

    contenido.bind("<Configure>", ajustar_contenido)
    canvas.bind("<Configure>", ajustar_ancho)

    tk.Label(
        contenido,
        text="Complete los datos del estudiante y su apoderado. "
             "El tutor puede quedar sin registrar.",
        bg=CREMA,
        fg=GRIS,
        font=("Segoe UI", 9)
    ).pack(pady=(12, 3))

    # DATOS DEL ESTUDIANTE
    seccion_estudiante = crear_seccion_formulario(
        contenido,
        "DATOS DEL ESTUDIANTE"
    )

    estudiante_vars = {
        "codigo": tk.StringVar(),
        "nombres": tk.StringVar(),
        "apellidos": tk.StringVar(),
        "edad": tk.StringVar(),
        "aula": tk.StringVar(),
        "seccion": tk.StringVar()
    }

    crear_campo(
        seccion_estudiante, 0, "Código del estudiante",
        estudiante_vars["codigo"]
    )
    crear_campo(
        seccion_estudiante, 1, "Nombres",
        estudiante_vars["nombres"]
    )
    crear_campo(
        seccion_estudiante, 2, "Apellidos",
        estudiante_vars["apellidos"]
    )

    campo_edad = crear_campo(
        seccion_estudiante,
        3,
        "Edad",
        estudiante_vars["edad"],
        ["3", "4", "5"]
    )

    campo_aula = crear_campo(
        seccion_estudiante,
        4,
        "Aula asignada automáticamente",
        estudiante_vars["aula"]
    )
    campo_aula.configure(state="disabled")

    crear_campo(
        seccion_estudiante, 5, "Sección",
        estudiante_vars["seccion"]
    )

    def actualizar_aula(event=None):
        aulas = {
            "3": "Aula azul",
            "4": "Aula amarilla",
            "5": "Aula verde"
        }
        estudiante_vars["aula"].set(
            aulas.get(estudiante_vars["edad"].get(), "")
        )

    campo_edad.bind("<<ComboboxSelected>>", actualizar_aula)

    # DATOS DEL APODERADO
    apoderado_vars = crear_responsable(
        contenido,
        "APODERADO (OBLIGATORIO)",
        "apoderado"
    )

    # DATOS DEL TUTOR
    tutor_vars = crear_responsable(
        contenido,
        "TUTOR (OPCIONAL)",
        "tutor",
        opcional=True
    )

    tk.Label(
        contenido,
        text="Si el estudiante no tiene tutor registrado, deje "
             "todos los campos de esta sección vacíos.",
        bg=CREMA,
        fg=GRIS,
        font=("Segoe UI", 9, "italic")
    ).pack(pady=5)

    def guardar():
        datos_estudiante = {
            clave: variable.get().strip()
            for clave, variable in estudiante_vars.items()
        }

        datos_apoderado = {
            clave: variable.get().strip()
            for clave, variable in apoderado_vars.items()
        }

        datos_tutor = {
            clave: variable.get().strip()
            for clave, variable in tutor_vars.items()
        }

        try:
            estudiante = registrar_estudiante_completo(
                datos_estudiante,
                datos_apoderado,
                datos_tutor
            )

            messagebox.showinfo(
                "Registro exitoso",
                "El registro se guardó correctamente.\n\n"
                f"Estudiante: {estudiante['nombres']} "
                f"{estudiante['apellidos']}\n"
                f"Aula: {estudiante['aula']}\n"
                f"Sección: {estudiante['seccion']}",
                parent=ventana
            )

            ventana.destroy()

        except ValueError as error:
            messagebox.showerror(
                "No se pudo registrar",
                str(error),
                parent=ventana
            )

    tk.Button(
        contenido,
        text="GUARDAR REGISTRO COMPLETO",
        command=guardar,
        bg=VERDE,
        fg=BLANCO,
        activebackground=VERDE_OSCURO,
        activeforeground=BLANCO,
        relief="flat",
        cursor="hand2",
        font=("Segoe UI", 10, "bold"),
        pady=12
    ).pack(fill="x", padx=25, pady=18)

    ventana.transient(raiz)
    ventana.grab_set()



def abrir_edicion_estudiante(raiz, codigo, al_guardar, padre=None):
    registros = obtener_datos_padron()

    estudiante = next(
        (
            e for e in registros
            if str(e.get("codigo", "")).casefold()
            == str(codigo).casefold()
        ),
        None
    )

    if not estudiante:
        messagebox.showerror(
            "Estudiante no encontrado",
            "No se encontr? el registro seleccionado."
        )
        return

    ventana = tk.Toplevel(padre or raiz)
    preparar_ventana(
        ventana,
        "Editar estudiante y responsables",
        850,
        780
    )

    principal = tk.Frame(ventana, bg=CREMA)
    principal.pack(fill="both", expand=True)

    canvas = tk.Canvas(principal, bg=CREMA, highlightthickness=0)
    barra = ttk.Scrollbar(
        principal, orient="vertical", command=canvas.yview
    )
    canvas.configure(yscrollcommand=barra.set)

    barra.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    contenido = tk.Frame(canvas, bg=CREMA)
    ventana_canvas = canvas.create_window(
        (0, 0), window=contenido, anchor="nw"
    )

    contenido.bind(
        "<Configure>",
        lambda event: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.bind(
        "<Configure>",
        lambda event: canvas.itemconfigure(
            ventana_canvas, width=event.width
        )
    )

    tk.Label(
        contenido,
        text="Modifique los datos necesarios y guarde los cambios.",
        bg=CREMA,
        fg=GRIS,
        font=("Segoe UI", 9)
    ).pack(pady=(12, 3))

    seccion = crear_seccion_formulario(
        contenido, "DATOS DEL ESTUDIANTE"
    )

    estudiante_vars = {
        "codigo": tk.StringVar(value=estudiante.get("codigo", "")),
        "nombres": tk.StringVar(value=estudiante.get("nombres", "")),
        "apellidos": tk.StringVar(value=estudiante.get("apellidos", "")),
        "edad": tk.StringVar(value=str(estudiante.get("edad", ""))),
        "aula": tk.StringVar(value=estudiante.get("aula", "")),
        "seccion": tk.StringVar(value=estudiante.get("seccion", ""))
    }

    crear_campo(
        seccion, 0, "C?digo del estudiante", estudiante_vars["codigo"]
    )
    crear_campo(
        seccion, 1, "Nombres", estudiante_vars["nombres"]
    )
    crear_campo(
        seccion, 2, "Apellidos", estudiante_vars["apellidos"]
    )

    campo_edad = crear_campo(
        seccion, 3, "Edad", estudiante_vars["edad"], ["3", "4", "5"]
    )

    campo_aula = crear_campo(
        seccion, 4, "Aula asignada autom?ticamente",
        estudiante_vars["aula"]
    )
    campo_aula.configure(state="disabled")

    crear_campo(
        seccion, 5, "Secci?n", estudiante_vars["seccion"]
    )

    def actualizar_aula(event=None):
        aulas = {
            "3": "Aula azul",
            "4": "Aula amarilla",
            "5": "Aula verde"
        }
        estudiante_vars["aula"].set(
            aulas.get(estudiante_vars["edad"].get(), "")
        )

    campo_edad.bind("<<ComboboxSelected>>", actualizar_aula)

    apoderado_vars = crear_responsable(
        contenido, "APODERADO (OBLIGATORIO)", "apoderado"
    )

    tutor_vars = crear_responsable(
        contenido, "TUTOR (OPCIONAL)", "tutor", opcional=True
    )

    apoderado = estudiante.get("apoderado", {})
    tutor = estudiante.get("tutor", {})

    for clave, variable in apoderado_vars.items():
        variable.set(apoderado.get(clave, ""))

    apoderado_vars["parentesco"].set(
        estudiante.get("apoderado_parentesco", "")
    )

    for clave, variable in tutor_vars.items():
        variable.set(tutor.get(clave, ""))

    tutor_vars["parentesco"].set(
        estudiante.get("tutor_parentesco", "")
    )

    tk.Label(
        contenido,
        text="El apoderado es obligatorio. Si no tiene tutor, "
             "deje vac?os todos los campos de esa secci?n.",
        bg=CREMA,
        fg=GRIS,
        font=("Segoe UI", 9, "italic"),
        wraplength=700
    ).pack(pady=7)

    def guardar_cambios():
        datos_estudiante = {
            clave: variable.get().strip()
            for clave, variable in estudiante_vars.items()
        }

        datos_apoderado = {
            clave: variable.get().strip()
            for clave, variable in apoderado_vars.items()
        }

        datos_tutor = {
            clave: variable.get().strip()
            for clave, variable in tutor_vars.items()
        }

        try:
            actualizado = editar_estudiante_completo(
                codigo,
                datos_estudiante,
                datos_apoderado,
                datos_tutor
            )

            messagebox.showinfo(
                "Actualizaci?n exitosa",
                "Los datos se actualizaron correctamente.\n\n"
                f"Estudiante: {actualizado['nombres']} "
                f"{actualizado['apellidos']}\n"
                f"Aula: {actualizado['aula']}\n"
                f"Secci?n: {actualizado['seccion']}",
                parent=ventana
            )

            ventana.destroy()
            al_guardar()

        except ValueError as error:
            messagebox.showerror(
                "No se pudo actualizar",
                str(error),
                parent=ventana
            )

    tk.Button(
        contenido,
        text="GUARDAR CAMBIOS",
        command=guardar_cambios,
        bg=VERDE,
        fg=BLANCO,
        activebackground=VERDE_OSCURO,
        activeforeground=BLANCO,
        relief="flat",
        cursor="hand2",
        font=("Segoe UI", 10, "bold"),
        pady=12
    ).pack(fill="x", padx=25, pady=18)

    ventana.transient(padre or raiz)
    ventana.grab_set()

def abrir_padron(raiz):
    ventana = tk.Toplevel(raiz)
    preparar_ventana(
        ventana,
        "Padrón general de estudiantes",
        1250,
        720
    )

    tk.Label(
        ventana,
        text="Estudiantes organizados por aula y sección. "
             "Desplace la tabla horizontalmente para consultar "
             "todos los datos.",
        bg=CREMA,
        fg=TEXTO,
        font=("Segoe UI", 9)
    ).pack(fill="x", padx=15, pady=10)

    pestanas = ttk.Notebook(ventana)
    pestanas.pack(fill="both", expand=True, padx=12, pady=10)

    columnas = [
        "codigo", "nombres", "apellidos", "edad", "seccion",
        "dni_apoderado", "nombres_apoderado", "apellidos_apoderado",
        "telefono_apoderado", "correo_apoderado", "parentesco_apoderado",
        "dni_tutor", "nombres_tutor", "apellidos_tutor",
        "telefono_tutor", "correo_tutor", "parentesco_tutor"
    ]

    encabezados = {
        "codigo": "Código",
        "nombres": "Nombres del estudiante",
        "apellidos": "Apellidos del estudiante",
        "edad": "Edad",
        "seccion": "Sección",
        "dni_apoderado": "DNI apoderado",
        "nombres_apoderado": "Nombres apoderado",
        "apellidos_apoderado": "Apellidos apoderado",
        "telefono_apoderado": "Teléfono apoderado",
        "correo_apoderado": "Correo apoderado",
        "parentesco_apoderado": "Parentesco apoderado",
        "dni_tutor": "DNI tutor",
        "nombres_tutor": "Nombres tutor",
        "apellidos_tutor": "Apellidos tutor",
        "telefono_tutor": "Teléfono tutor",
        "correo_tutor": "Correo tutor",
        "parentesco_tutor": "Parentesco tutor"
    }

    aulas = [
        ("Aula azul", "3"),
        ("Aula amarilla", "4"),
        ("Aula verde", "5")
    ]

    datos = obtener_datos_padron()
    tablas = {}

    def editar_seleccionado():
        nombre_aula = pestanas.tab(pestanas.select(), "text")
        tabla = tablas[nombre_aula]
        seleccion = tabla.selection()

        if not seleccion:
            messagebox.showwarning(
                "Seleccione un estudiante",
                "Seleccione un estudiante de la lista para editar.",
                parent=ventana
            )
            return

        valores = tabla.item(seleccion[0], "values")
        codigo = valores[0]

        def refrescar_lista():
            ventana.destroy()
            abrir_padron(raiz)

        abrir_edicion_estudiante(
            raiz, codigo, refrescar_lista, ventana
        )

    tk.Button(
        ventana,
        text="EDITAR ESTUDIANTE SELECCIONADO",
        command=editar_seleccionado,
        bg=VERDE,
        fg=BLANCO,
        activebackground=VERDE_OSCURO,
        activeforeground=BLANCO,
        relief="flat",
        cursor="hand2",
        font=("Segoe UI", 9, "bold"),
        padx=15,
        pady=9
    ).pack(anchor="e", padx=15, pady=(0, 8))

    for nombre_aula, edad in aulas:
        pagina = tk.Frame(pestanas, bg=BLANCO)
        pestanas.add(pagina, text=nombre_aula)

        registros = [
            estudiante for estudiante in datos
            if str(estudiante.get("edad", "")) == edad
        ]

        tk.Label(
            pagina,
            text=f"{nombre_aula.upper()}  |  "
                 f"{len(registros)} estudiante(s)",
            bg=BLANCO,
            fg=VERDE_OSCURO,
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", padx=12, pady=10)

        marco_tabla = tk.Frame(pagina, bg=BLANCO)
        marco_tabla.pack(fill="both", expand=True, padx=8, pady=5)

        tabla = ttk.Treeview(
            marco_tabla,
            columns=columnas,
            show="headings"
        )

        for columna in columnas:
            tabla.heading(
                columna,
                text=encabezados[columna]
            )

            tabla.column(
                columna,
                width=145,
                minwidth=110,
                anchor="center"
            )

        tabla.column("codigo", width=105)
        tabla.column("edad", width=65)
        tabla.column("seccion", width=80)

        scroll_vertical = ttk.Scrollbar(
            marco_tabla,
            orient="vertical",
            command=tabla.yview
        )

        scroll_horizontal = ttk.Scrollbar(
            marco_tabla,
            orient="horizontal",
            command=tabla.xview
        )

        tabla.configure(
            yscrollcommand=scroll_vertical.set,
            xscrollcommand=scroll_horizontal.set
        )

        tabla.grid(row=0, column=0, sticky="nsew")
        scroll_vertical.grid(row=0, column=1, sticky="ns")
        scroll_horizontal.grid(row=1, column=0, sticky="ew")

        marco_tabla.rowconfigure(0, weight=1)
        marco_tabla.columnconfigure(0, weight=1)

        for estudiante in registros:
            apoderado = estudiante.get("apoderado", {})
            tutor = estudiante.get("tutor", {})

            valores = [
                estudiante.get("codigo", ""),
                estudiante.get("nombres", ""),
                estudiante.get("apellidos", ""),
                estudiante.get("edad", ""),
                estudiante.get("seccion", ""),
                apoderado.get("dni", ""),
                apoderado.get("nombres", ""),
                apoderado.get("apellidos", ""),
                apoderado.get("telefono", ""),
                apoderado.get("correo", ""),
                estudiante.get("apoderado_parentesco", ""),
                tutor.get("dni", ""),
                tutor.get("nombres", ""),
                tutor.get("apellidos", ""),
                tutor.get("telefono", ""),
                tutor.get("correo", ""),
                estudiante.get("tutor_parentesco", "")
            ]

            tabla.insert("", "end", values=valores)

        tablas[nombre_aula] = tabla

    ventana.transient(raiz)
    ventana.grab_set()
