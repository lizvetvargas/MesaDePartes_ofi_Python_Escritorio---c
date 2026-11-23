import os
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox

from configuracion import BASE
from archivo import buscar_archivados


VERDE_OSCURO = "#174D38"
VERDE = "#347A59"
VERDE_CLARO = "#DCEBDD"
CREMA = "#F5F3E9"
BLANCO = "#FFFFFF"
TEXTO = "#263B30"
GRIS = "#64756B"


class VentanaArchivo:

    def __init__(self, raiz):
        self.raiz = tk.Toplevel(raiz)
        self.raiz.title("Archivo Institucional | Santa Rita de Casia")
        self.raiz.geometry("1150x650")
        self.raiz.minsize(900, 500)
        self.raiz.configure(bg=CREMA)

        self.termino = tk.StringVar()

        self.crear_encabezado()
        self.crear_busqueda()
        self.crear_tabla()
        self.crear_estado()
        self.cargar_registros()

    def crear_encabezado(self):
        encabezado = tk.Frame(
            self.raiz,
            bg=VERDE_OSCURO,
            height=75
        )
        encabezado.pack(fill="x")
        encabezado.pack_propagate(False)

        tk.Label(
            encabezado,
            text="ARCHIVO INSTITUCIONAL",
            bg=VERDE_OSCURO,
            fg=BLANCO,
            font=("Segoe UI", 17, "bold")
        ).pack(side="left", padx=22, pady=20)

        tk.Label(
            encabezado,
            text="SANTA RITA DE CASIA",
            bg=VERDE_OSCURO,
            fg=VERDE_CLARO,
            font=("Segoe UI", 10, "bold")
        ).pack(side="right", padx=22)

    def crear_busqueda(self):
        marco = tk.Frame(self.raiz, bg=CREMA)
        marco.pack(fill="x", padx=18, pady=15)

        tk.Label(
            marco,
            text="Buscar expediente:",
            bg=CREMA,
            fg=TEXTO,
            font=("Segoe UI", 10, "bold")
        ).pack(side="left", padx=(0, 8))

        entrada = ttk.Entry(
            marco,
            textvariable=self.termino,
            width=42
        )
        entrada.pack(side="left", padx=5)
        entrada.bind(
            "<KeyRelease>",
            lambda evento: self.cargar_registros()
        )

        ttk.Button(
            marco,
            text="Buscar",
            command=self.cargar_registros
        ).pack(side="left", padx=5)

        ttk.Button(
            marco,
            text="Actualizar",
            command=self.actualizar
        ).pack(side="left", padx=5)

    def crear_tabla(self):
        contenedor = tk.Frame(self.raiz, bg=BLANCO)
        contenedor.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=(0, 12)
        )

        self.columnas = (
            "codigo",
            "fecha",
            "solicitante",
            "asunto",
            "area_destino",
            "fecha_archivo",
            "archivado_por"
        )

        self.tabla = ttk.Treeview(
            contenedor,
            columns=self.columnas,
            show="headings",
            selectmode="browse"
        )

        etiquetas = [
            "Código",
            "Recepción",
            "Solicitante",
            "Asunto",
            "Área",
            "Fecha de archivo",
            "Archivado por"
        ]

        anchos = [100, 135, 145, 220, 125, 145, 130]

        for columna, etiqueta, ancho in zip(
            self.columnas,
            etiquetas,
            anchos
        ):
            self.tabla.heading(columna, text=etiqueta)
            self.tabla.column(
                columna,
                width=ancho,
                minwidth=80,
                anchor="w"
            )

        barra = ttk.Scrollbar(
            contenedor,
            orient="vertical",
            command=self.tabla.yview
        )

        horizontal = ttk.Scrollbar(
            self.raiz,
            orient="horizontal",
            command=self.tabla.xview
        )

        self.tabla.configure(
            yscrollcommand=barra.set,
            xscrollcommand=horizontal.set
        )

        self.tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        horizontal.pack(fill="x", padx=18)

        self.tabla.bind(
            "<Double-1>",
            self.abrir_documento
        )

    def crear_estado(self):
        self.mensaje = tk.StringVar(
            value="Archivo institucional listo"
        )

        barra = tk.Label(
            self.raiz,
            textvariable=self.mensaje,
            bg=VERDE_OSCURO,
            fg=BLANCO,
            anchor="w",
            padx=12,
            pady=6
        )
        barra.pack(fill="x", side="bottom")

    def cargar_registros(self):
        for elemento in self.tabla.get_children():
            self.tabla.delete(elemento)

        registros = buscar_archivados(self.termino.get())

        for registro in registros:
            self.tabla.insert(
                "",
                "end",
                values=(
                    registro.get("codigo", ""),
                    registro.get("fecha", ""),
                    registro.get("solicitante", ""),
                    registro.get("asunto", ""),
                    registro.get("area_destino", ""),
                    registro.get("fecha_archivo", ""),
                    registro.get("archivado_por", "")
                ),
                tags=(registro.get("codigo", ""),)
            )

        self.mensaje.set(
            f"{len(registros)} expediente(s) archivado(s)"
        )

    def actualizar(self):
        self.termino.set("")
        self.cargar_registros()

    def abrir_documento(self, evento=None):
        seleccion = self.tabla.selection()

        if not seleccion:
            return

        codigo = self.tabla.item(
            seleccion[0],
            "values"
        )[0]

        registros = buscar_archivados(codigo)

        registro = next(
            (
                item for item in registros
                if item.get("codigo") == codigo
            ),
            None
        )

        if not registro or not registro.get("archivo"):
            messagebox.showwarning(
                "Documento",
                "Este expediente no tiene un documento adjunto."
            )
            return

        ruta = Path(registro["archivo"])

        if not ruta.is_absolute():
            ruta = BASE / ruta

        if not ruta.exists():
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
                str(error)
            )


def abrir_archivo(raiz):
    return VentanaArchivo(raiz)
