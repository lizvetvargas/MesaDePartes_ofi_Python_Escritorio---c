import os
import shutil
import uuid
import tkinter as tk

from pathlib import Path
from datetime import datetime
from tkinter import ttk, messagebox, filedialog

from persistencia import preparar, autenticar, cargar
from configuracion import BASE, ADJUNTOS
from ventana_archivo import abrir_archivo
from ventana_registros import abrir_estudiante, abrir_padron
from archivo import archivar

from servicios import (
    registrar, actualizar, eliminar, buscar, ordenar,
    seguimiento, resumen, exportar,
    ESTADOS, ESTADOS_GESTION, REVISIONES, TIPOS, AREAS, PRIORIDADES
)


VERDE_OSCURO = "#174D38"
VERDE = "#347A59"
VERDE_CLARO = "#DCEBDD"
CREMA = "#F5F3E9"
BLANCO = "#FFFFFF"
TEXTO = "#263B30"
GRIS = "#64756B"
DORADO = "#C6A45C"


class Ventana:

    def __init__(self, raiz, cuenta):
        self.raiz = raiz
        self.cuenta = cuenta
        self.codigo = None
        self.campos = {}
        self.filtros = {}
        self.orden_campo = "fecha"
        self.orden_inverso = True

        raiz.title("Mesa de Partes Digital | Santa Rita de Casia")
        raiz.geometry("1450x850")
        raiz.minsize(1150, 700)
        raiz.configure(bg=CREMA)

        self.configurar_estilos()
        self.crear_encabezado()
        self.crear_barra_acciones()
        self.crear_indicadores()
        self.crear_contenido()
        self.crear_barra_estado()

        self.refrescar()

    def configurar_estilos(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")

        estilo.configure(
            "Treeview",
            background=BLANCO,
            fieldbackground=BLANCO,
            foreground=TEXTO,
            rowheight=32,
            font=("Segoe UI", 9)
        )

        estilo.configure(
            "Treeview.Heading",
            background=VERDE_OSCURO,
            foreground=BLANCO,
            font=("Segoe UI", 9, "bold"),
            padding=8
        )

        estilo.map(
            "Treeview",
            background=[("selected", VERDE)],
            foreground=[("selected", BLANCO)]
        )

        estilo.configure(
            "TCombobox",
            padding=5,
            font=("Segoe UI", 9)
        )

        estilo.configure(
            "TEntry",
            padding=6,
            font=("Segoe UI", 9)
        )

        estilo.configure(
            "TButton",
            padding=(10, 7),
            font=("Segoe UI", 9)
        )

        estilo.map(
            "TButton",
            background=[("active", VERDE_CLARO)]
        )

    def crear_encabezado(self):
        cab = tk.Frame(
            self.raiz,
            bg=VERDE_OSCURO,
            height=82
        )
        cab.pack(fill="x")
        cab.pack_propagate(False)

        identidad = tk.Frame(cab, bg=VERDE_OSCURO)
        identidad.pack(side="left", padx=24, pady=12)

        tk.Label(
            identidad,
            text="SANTA RITA DE CASIA",
            bg=VERDE_OSCURO,
            fg=BLANCO,
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w")

        tk.Label(
            identidad,
            text="MESA DE PARTES DIGITAL",
            bg=VERDE_OSCURO,
            fg="#DCEBDD",
            font=("Segoe UI", 9)
        ).pack(anchor="w")

        tk.Label(
            cab,
            text=f"{self.cuenta['rol']}  |  {self.cuenta['usuario']}",
            bg=VERDE_OSCURO,
            fg=BLANCO,
            font=("Segoe UI", 10, "bold")
        ).pack(side="right", padx=24)

    def crear_barra_acciones(self):
        barra = tk.Frame(self.raiz, bg=VERDE_CLARO)
        barra.pack(fill="x")

        acciones = [
            ("＋ Nuevo", self.limpiar),
            ("Guardar", self.guardar),
            ("Editar", self.editar),
            ("Ver documento", self.ver_documento),
            ("Eliminar", self.borrar),
            ("Seguimiento", self.derivar),
            ("Archivar expediente", self.archivar_expediente),
            ("Resumen", self.ver_resumen),
            ("Exportar CSV", self.exportar_csv),
            ("Archivo institucional", lambda: abrir_archivo(self.raiz)),
            ("Registrar estudiante", lambda: abrir_estudiante(self.raiz)),
            ("Lista de estudiantes", lambda: abrir_padron(self.raiz))
        ]

        for nombre, funcion in acciones:
            ttk.Button(
                barra,
                text=nombre,
                command=funcion
            ).pack(side="left", padx=5, pady=8)

    def crear_indicadores(self):
        contenedor = tk.Frame(self.raiz, bg=CREMA)
        contenedor.pack(fill="x", padx=14, pady=(12, 5))

        definiciones = [
            ("Total de expedientes", "total", VERDE_OSCURO),
            ("Recibidos", "Recibido", VERDE),
            ("En revisión", "En revisión", "#A77D32"),
            ("Observados", "Observado", "#B66B42"),
            ("Finalizados", "Finalizado", "#527A69")
        ]

        self.indicadores = {}

        for titulo, clave, color in definiciones:
            tarjeta = tk.Frame(
                contenedor,
                bg=BLANCO,
                highlightbackground="#D8E2D9",
                highlightthickness=1,
                padx=14,
                pady=9
            )
            tarjeta.pack(
                side="left",
                fill="both",
                expand=True,
                padx=5
            )

            tk.Label(
                tarjeta,
                text=titulo,
                bg=BLANCO,
                fg=GRIS,
                font=("Segoe UI", 9)
            ).pack(anchor="w")

            valor = tk.Label(
                tarjeta,
                text="0",
                bg=BLANCO,
                fg=color,
                font=("Segoe UI", 21, "bold")
            )
            valor.pack(anchor="w", pady=(2, 0))

            self.indicadores[clave] = valor

    def crear_contenido(self):
        cuerpo = tk.Frame(self.raiz, bg=CREMA)
        cuerpo.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=10
        )

        izquierda = tk.Frame(
            cuerpo,
            bg=BLANCO,
            width=365,
            padx=14,
            pady=12
        )
        izquierda.pack(
            side="left",
            fill="y",
            padx=(0, 12)
        )
        izquierda.pack_propagate(False)

        tk.Label(
            izquierda,
            text="DATOS DEL EXPEDIENTE",
            bg=BLANCO,
            fg=VERDE_OSCURO,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(0, 3))

        tk.Label(
            izquierda,
            text="Complete los datos para registrar o actualizar un trámite.",
            bg=BLANCO,
            fg=GRIS,
            font=("Segoe UI", 8),
            wraplength=320,
            justify="left"
        ).pack(anchor="w", pady=(0, 9))

        formulario = tk.Frame(izquierda, bg=BLANCO)
        formulario.pack(fill="both", expand=True)

        definiciones = [
            ("solicitante", "Solicitante", None),
            ("documento", "Documento presentado", None),
            ("dni", "DNI", None),
            ("asunto", "Asunto", None),
            ("tipo_tramite", "Tipo de trámite", TIPOS),
            ("area_destino", "Área destino", AREAS),
            ("responsable", "Responsable", None),
            ("prioridad", "Prioridad", PRIORIDADES),
            ("estado", "Estado del trámite", ESTADOS_GESTION),
            ("revision", "Estado de revisión", REVISIONES),
            ("observaciones", "Observaciones", None)
        ]

        for fila, (clave, etiqueta, opciones) in enumerate(definiciones):
            tk.Label(
                formulario,
                text=etiqueta,
                bg=BLANCO,
                fg=TEXTO,
                font=("Segoe UI", 9)
            ).grid(
                row=fila,
                column=0,
                sticky="w",
                pady=4
            )

            if opciones:
                widget = ttk.Combobox(
                    formulario,
                    values=opciones,
                    state="readonly",
                    width=23
                )
                widget.set(opciones[0])

            elif clave == "observaciones":
                widget = tk.Text(
                    formulario,
                    width=24,
                    height=3,
                    wrap="word",
                    font=("Segoe UI", 9),
                    relief="solid",
                    borderwidth=1
                )

            else:
                widget = ttk.Entry(
                    formulario,
                    width=25
                )

            widget.grid(
                row=fila,
                column=1,
                sticky="ew",
                padx=(8, 0),
                pady=4
            )

            self.campos[clave] = widget

        formulario.columnconfigure(1, weight=1)

        separador = tk.Frame(
            izquierda,
            bg=VERDE_CLARO,
            height=2
        )
        separador.pack(fill="x", pady=9)

        tk.Label(
            izquierda,
            text="DOCUMENTO ADJUNTO",
            bg=BLANCO,
            fg=VERDE_OSCURO,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(0, 5))

        fila_archivo = tk.Frame(izquierda, bg=BLANCO)
        fila_archivo.pack(fill="x")

        self.archivo = tk.StringVar()

        ttk.Entry(
            fila_archivo,
            textvariable=self.archivo
        ).pack(side="left", fill="x", expand=True)

        ttk.Button(
            fila_archivo,
            text="Elegir",
            command=self.adjuntar
        ).pack(side="left", padx=(5, 0))

        derecha = tk.Frame(
            cuerpo,
            bg=BLANCO,
            padx=14,
            pady=12
        )
        derecha.pack(
            side="left",
            fill="both",
            expand=True
        )

        tk.Label(
            derecha,
            text="REGISTRO Y SEGUIMIENTO",
            bg=BLANCO,
            fg=VERDE_OSCURO,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w")

        tk.Label(
            derecha,
            text="Busque expedientes y aplique filtros para localizar trámites.",
            bg=BLANCO,
            fg=GRIS,
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(3, 9))

        self.crear_filtros(derecha)
        self.crear_tabla(derecha)

    def crear_filtros(self, contenedor):
        fila = tk.Frame(contenedor, bg=BLANCO)
        fila.pack(fill="x", pady=(0, 10))

        self.termino = tk.StringVar()

        ttk.Entry(
            fila,
            textvariable=self.termino
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 5)
        )

        self.termino.trace_add(
            "write",
            lambda *args: self.refrescar()
        )

        filtros = [
            ("estado", ["Todos"] + ESTADOS, 13),
            ("area", ["Todas"] + AREAS, 13),
            ("prioridad", ["Todas"] + PRIORIDADES, 12)
        ]

        for clave, opciones, ancho in filtros:
            variable = tk.StringVar(value=opciones[0])
            self.filtros[clave] = variable

            combo = ttk.Combobox(
                fila,
                textvariable=variable,
                values=opciones,
                state="readonly",
                width=ancho
            )
            combo.pack(side="left", padx=3)

            combo.bind(
                "<<ComboboxSelected>>",
                lambda evento: self.refrescar()
            )

        ttk.Button(
            fila,
            text="Limpiar filtros",
            command=self.limpiar_filtros
        ).pack(side="left", padx=(5, 0))

        self.resultado_filtro = tk.StringVar(
            value="Expedientes registrados"
        )

        tk.Label(
            contenedor,
            textvariable=self.resultado_filtro,
            bg=BLANCO,
            fg=GRIS,
            font=("Segoe UI", 8)
        ).pack(anchor="w", pady=(0, 5))

    def crear_tabla(self, contenedor):
        marco = tk.Frame(contenedor, bg=BLANCO)
        marco.pack(fill="both", expand=True)

        self.columnas = (
            "codigo", "fecha", "solicitante", "dni",
            "asunto", "area_destino", "prioridad", "estado"
        )

        self.tabla = ttk.Treeview(
            marco,
            columns=self.columnas,
            show="headings",
            selectmode="browse"
        )

        etiquetas = [
            "Código", "Fecha", "Solicitante", "DNI",
            "Asunto", "Área", "Prioridad", "Estado"
        ]

        anchos = [100, 135, 145, 90, 210, 125, 105, 120]

        for columna, etiqueta, ancho in zip(
            self.columnas,
            etiquetas,
            anchos
        ):
            self.tabla.heading(
                columna,
                text=etiqueta,
                command=lambda campo=columna: self.ordenar_por(campo)
            )

            self.tabla.column(
                columna,
                width=ancho,
                minwidth=75,
                anchor="w"
            )

        self.tabla.tag_configure(
            "Recibido",
            background="#EAF4EC"
        )
        self.tabla.tag_configure(
            "En_revision",
            background="#FFF4D9"
        )
        self.tabla.tag_configure(
            "Observado",
            background="#FCE9E2"
        )
        self.tabla.tag_configure(
            "Finalizado",
            background="#E4EFE9"
        )
        self.tabla.tag_configure(
            "normal",
            background=BLANCO
        )

        sy = ttk.Scrollbar(
            marco,
            orient="vertical",
            command=self.tabla.yview
        )

        sx = ttk.Scrollbar(
            contenedor,
            orient="horizontal",
            command=self.tabla.xview
        )

        self.tabla.configure(
            yscrollcommand=sy.set,
            xscrollcommand=sx.set
        )

        self.tabla.pack(
            side="left",
            fill="both",
            expand=True
        )
        sy.pack(side="right", fill="y")
        sx.pack(fill="x")

        self.tabla.bind(
            "<<TreeviewSelect>>",
            self.seleccionar
        )

        self.tabla.bind(
            "<Double-1>",
            lambda evento: self.editar()
        )

    def crear_barra_estado(self):
        barra = tk.Frame(
            self.raiz,
            bg=VERDE_OSCURO,
            height=28
        )
        barra.pack(fill="x", side="bottom")

        self.mensaje = tk.StringVar(
            value="Sistema local listo"
        )

        tk.Label(
            barra,
            textvariable=self.mensaje,
            bg=VERDE_OSCURO,
            fg=BLANCO,
            anchor="w",
            padx=14,
            pady=5,
            font=("Segoe UI", 8)
        ).pack(fill="x")

    def actualizar_indicadores(self):
        total, estados = resumen()

        self.indicadores["total"].config(text=str(total))

        for estado in ESTADOS:
            if estado in self.indicadores:
                self.indicadores[estado].config(
                    text=str(estados.get(estado, 0))
                )

    def valor(self, clave):
        widget = self.campos[clave]

        if isinstance(widget, tk.Text):
            return widget.get("1.0", "end").strip()

        return widget.get().strip()

    def datos(self):
        datos = {
            clave: self.valor(clave)
            for clave in self.campos
        }

        datos["archivo"] = self.archivo.get().strip()

        return datos

    def llenar(self, datos):
        for clave, widget in self.campos.items():
            valor = datos.get(clave, "")

            if isinstance(widget, tk.Text):
                widget.delete("1.0", "end")
                widget.insert("1.0", valor)

            elif isinstance(widget, ttk.Combobox):
                widget.set(valor)

            else:
                widget.delete(0, "end")
                widget.insert(0, valor)

        self.archivo.set(datos.get("archivo", ""))
        self.codigo = datos.get("codigo")

    def limpiar(self):
        self.codigo = None

        for clave, widget in self.campos.items():
            if isinstance(widget, tk.Text):
                widget.delete("1.0", "end")

            elif isinstance(widget, ttk.Combobox):
                valores = widget["values"]
                widget.set(valores[0] if valores else "")

            else:
                widget.delete(0, "end")

        self.archivo.set("")

        if hasattr(self, "tabla"):
            seleccion = self.tabla.selection()
            if seleccion:
                self.tabla.selection_remove(*seleccion)

        self.mensaje.set(
            "Formulario preparado para registrar un nuevo expediente."
        )

    def limpiar_filtros(self):
        self.termino.set("")

        for clave, variable in self.filtros.items():
            variable.set(
                "Todos" if clave == "estado" else "Todas"
            )

        self.refrescar()

    def adjuntar(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar documento",
            filetypes=[
                ("Todos los archivos", "*.*"),
                ("Documentos PDF", "*.pdf"),
                ("Documentos Word", "*.docx *.doc"),
                ("Imágenes", "*.png *.jpg *.jpeg")
            ]
        )

        if ruta:
            self.archivo.set(ruta)

    def guardar_adjunto(self, ruta):
        if not ruta:
            return ""

        origen = Path(ruta)

        if not origen.exists() or not origen.is_file():
            raise ValueError("El archivo adjunto no existe.")

        ADJUNTOS.mkdir(parents=True, exist_ok=True)

        try:
            if origen.resolve().is_relative_to(ADJUNTOS.resolve()):
                return str(origen.relative_to(BASE))
        except ValueError:
            pass

        nombre = f"{uuid.uuid4().hex}{origen.suffix.lower()}"
        destino = ADJUNTOS / nombre

        shutil.copy2(origen, destino)

        return str(destino.relative_to(BASE))

    def obtener_ruta_documento(self, archivo):
        if not archivo:
            return None

        ruta = Path(archivo)

        if not ruta.is_absolute():
            ruta = BASE / ruta

        return ruta

    def ver_documento(self):
        archivo = self.archivo.get().strip()

        if not archivo:
            messagebox.showwarning(
                "Documento",
                "Este expediente no tiene ningún documento adjunto."
            )
            return

        ruta = self.obtener_ruta_documento(archivo)

        if ruta is None or not ruta.exists():
            messagebox.showerror(
                "Documento no encontrado",
                "No se encuentra el archivo adjunto."
            )
            return

        try:
            os.startfile(str(ruta))
        except OSError as error:
            messagebox.showerror(
                "Error al abrir",
                f"No se pudo abrir el documento:\n{error}"
            )

    def editar(self):
        if not self.codigo:
            seleccion = self.tabla.selection()

            if not seleccion:
                messagebox.showwarning(
                    "Editar expediente",
                    "Seleccione primero un expediente de la tabla."
                )
                return

        self.mensaje.set(
            f"Modo de edición: expediente {self.codigo}. "
            "Modifique los datos y pulse Guardar."
        )

    def guardar(self):
        datos = self.datos()

        try:
            if datos["archivo"]:
                ruta = self.obtener_ruta_documento(datos["archivo"])

                if ruta is None or not ruta.exists():
                    raise ValueError(
                        "El documento adjunto seleccionado no existe."
                    )

                datos["archivo"] = self.guardar_adjunto(str(ruta))

            if self.codigo:
                actualizar(self.codigo, datos)
                texto = f"Expediente {self.codigo} actualizado."
            else:
                self.codigo = registrar(datos)
                texto = f"Expediente registrado: {self.codigo}"

            self.archivo.set(datos["archivo"])
            self.refrescar()
            self.mensaje.set(texto)

            messagebox.showinfo(
                "Mesa de Partes",
                texto
            )

        except (ValueError, OSError) as error:
            messagebox.showerror(
                "Error al guardar",
                str(error)
            )

    def borrar(self):
        if not self.codigo:
            messagebox.showwarning(
                "Eliminar",
                "Seleccione un expediente."
            )
            return

        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro de eliminar el expediente {self.codigo}?"
        )

        if confirmar:
            try:
                eliminar(self.codigo)
                self.limpiar()
                self.refrescar()
                self.mensaje.set("Expediente eliminado correctamente.")

            except ValueError as error:
                messagebox.showerror("Error", str(error))

    def derivar(self):
        if not self.codigo:
            messagebox.showwarning(
                "Seguimiento",
                "Seleccione un expediente."
            )
            return

        datos = self.datos()

        try:
            seguimiento(
                self.codigo,
                datos["estado"],
                datos["area_destino"],
                datos["responsable"],
                datos["observaciones"]
            )

            self.refrescar()
            self.mensaje.set(
                f"Seguimiento actualizado para {self.codigo}."
            )

            messagebox.showinfo(
                "Seguimiento",
                "Se actualizó el estado y la asignación del expediente."
            )

        except ValueError as error:
            messagebox.showerror("Error", str(error))

    def archivar_expediente(self):
        if not self.codigo:
            messagebox.showwarning("Archivo institucional", "Seleccione un expediente.")
            return

        confirmar = messagebox.askyesno(
            "Confirmar archivo",
            f"?Desea archivar el expediente {self.codigo}?\n\n"
            "Solo se pueden archivar expedientes finalizados."
        )

        if not confirmar:
            return

        responsable = self.cuenta.get("usuario", "") if isinstance(self.cuenta, dict) else ""

        try:
            codigo_archivado = self.codigo
            archivar(codigo_archivado, responsable)
            self.refrescar()
            self.mensaje.set(
                f"Expediente {codigo_archivado} archivado correctamente."
            )
            messagebox.showinfo(
                "Archivo institucional",
                f"El expediente {codigo_archivado} se archivo correctamente."
            )
        except ValueError as error:
            messagebox.showerror("No se pudo archivar", str(error))

    def filtrar_registros(self, registros):
        estado = self.filtros["estado"].get()
        area = self.filtros["area"].get()
        prioridad = self.filtros["prioridad"].get()

        if estado != "Todos":
            registros = [
                r for r in registros
                if r.get("estado", "") == estado
            ]

        if area != "Todas":
            registros = [
                r for r in registros
                if r.get("area_destino", "") == area
            ]

        if prioridad != "Todas":
            registros = [
                r for r in registros
                if r.get("prioridad", "") == prioridad
            ]

        return registros

    def clave_orden(self, registro):
        valor = str(registro.get(self.orden_campo, ""))

        if self.orden_campo == "fecha":
            try:
                return datetime.strptime(
                    valor,
                    "%d/%m/%Y %H:%M"
                )
            except ValueError:
                return datetime.min

        return valor.casefold()

    def refrescar(self):
        if not hasattr(self, "tabla"):
            return

        for item in self.tabla.get_children():
            self.tabla.delete(item)

        registros = buscar(self.termino.get())
        registros = self.filtrar_registros(registros)

        registros.sort(
            key=self.clave_orden,
            reverse=self.orden_inverso
        )

        for registro in registros:
            estado = registro.get("estado", "")

            if estado == "En revisión":
                etiqueta = "En_revision"
            elif estado in ("Recibido", "Observado", "Finalizado"):
                etiqueta = estado
            else:
                etiqueta = "normal"

            self.tabla.insert(
                "",
                "end",
                values=tuple(
                    registro.get(columna, "")
                    for columna in self.columnas
                ),
                tags=(etiqueta,)
            )

        self.resultado_filtro.set(
            f"{len(registros)} expediente(s) encontrado(s)"
        )

        self.actualizar_indicadores()

    def seleccionar(self, evento=None):
        seleccion = self.tabla.selection()

        if seleccion:
            valores = self.tabla.item(
                seleccion[0],
                "values"
            )

            codigo = valores[0]

            for registro in cargar():
                if registro.get("codigo") == codigo:
                    self.llenar(registro)
                    self.mensaje.set(
                        f"Expediente seleccionado: {codigo}"
                    )
                    break

    def ordenar_por(self, campo):
        if self.orden_campo == campo:
            self.orden_inverso = not self.orden_inverso
        else:
            self.orden_campo = campo
            self.orden_inverso = False

        self.refrescar()

    def ver_resumen(self):
        total, estados = resumen()

        mensaje = (
            f"TOTAL DE EXPEDIENTES: {total}\n\n"
            + "\n".join(
                f"{clave}: {valor}"
                for clave, valor in estados.items()
            )
        )

        messagebox.showinfo(
            "Resumen de expedientes",
            mensaje
        )

    def exportar_csv(self):
        ruta = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Archivo CSV", "*.csv")],
            initialfile="reporte_expedientes.csv"
        )

        if ruta:
            try:
                cantidad = exportar(ruta)

                messagebox.showinfo(
                    "Exportación",
                    f"Se exportaron {cantidad} expedientes."
                )

            except OSError as error:
                messagebox.showerror(
                    "Error de exportación",
                    str(error)
                )


def centrar_ventana(ventana, ancho, alto):
    ventana.update_idletasks()

    x = (ventana.winfo_screenwidth() - ancho) // 2
    y = (ventana.winfo_screenheight() - alto) // 2

    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")


def iniciar():
    preparar()

    raiz = tk.Tk()
    raiz.withdraw()

    login = tk.Toplevel(raiz)
    login.title("Acceso | Santa Rita de Casia")
    login.configure(bg=VERDE_OSCURO)
    login.resizable(False, False)

    centrar_ventana(login, 420, 370)

    cabecera = tk.Frame(
        login,
        bg=VERDE_OSCURO
    )
    cabecera.pack(fill="x", pady=(22, 15))

    tk.Label(
        cabecera,
        text="SANTA RITA DE CASIA",
        bg=VERDE_OSCURO,
        fg=BLANCO,
        font=("Segoe UI", 19, "bold")
    ).pack()

    tk.Label(
        cabecera,
        text="MESA DE PARTES DIGITAL",
        bg=VERDE_OSCURO,
        fg="#DCEBDD",
        font=("Segoe UI", 10)
    ).pack(pady=(4, 0))

    panel = tk.Frame(
        login,
        bg=BLANCO,
        padx=28,
        pady=22
    )
    panel.pack(
        fill="both",
        expand=True,
        padx=22,
        pady=(0, 22)
    )

    tk.Label(
        panel,
        text="Bienvenido al sistema",
        bg=BLANCO,
        fg=VERDE_OSCURO,
        font=("Segoe UI", 13, "bold")
    ).pack(anchor="w", pady=(0, 15))

    tk.Label(
        panel,
        text="Usuario",
        bg=BLANCO,
        fg=TEXTO,
        font=("Segoe UI", 9, "bold")
    ).pack(anchor="w")

    usuario = ttk.Entry(panel)
    usuario.pack(fill="x", pady=(5, 12))

    tk.Label(
        panel,
        text="Contraseña",
        bg=BLANCO,
        fg=TEXTO,
        font=("Segoe UI", 9, "bold")
    ).pack(anchor="w")

    clave = ttk.Entry(
        panel,
        show="*"
    )
    clave.pack(fill="x", pady=(5, 17))

    def entrar(event=None):
        cuenta = autenticar(
            usuario.get().strip(),
            clave.get()
        )

        if not cuenta:
            messagebox.showerror(
                "Acceso denegado",
                "Usuario o contraseña incorrectos."
            )
            clave.delete(0, "end")
            clave.focus_set()
            return

        login.destroy()
        raiz.deiconify()
        Ventana(raiz, cuenta)

    boton = tk.Button(
        panel,
        text="INGRESAR",
        command=entrar,
        bg=VERDE,
        fg=BLANCO,
        activebackground=VERDE_OSCURO,
        activeforeground=BLANCO,
        relief="flat",
        cursor="hand2",
        font=("Segoe UI", 10, "bold"),
        pady=9
    )
    boton.pack(fill="x")

    tk.Label(
        panel,
        text="Sistema administrativo institucional",
        bg=BLANCO,
        fg=GRIS,
        font=("Segoe UI", 8)
    ).pack(pady=(12, 0))

    clave.bind("<Return>", entrar)
    usuario.bind("<Return>", lambda evento: clave.focus_set())

    usuario.focus_set()

    login.protocol("WM_DELETE_WINDOW", raiz.destroy)

    raiz.mainloop()


if __name__ == "__main__":
    iniciar()

