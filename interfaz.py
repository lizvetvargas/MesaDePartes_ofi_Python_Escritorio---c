
import os
import shutil
import uuid
import tkinter as tk

from pathlib import Path
from tkinter import ttk, messagebox, filedialog

from persistencia import preparar, autenticar, cargar
from configuracion import BASE, ADJUNTOS

from servicios import (
    registrar, actualizar, eliminar, buscar, ordenar,
    seguimiento, resumen, exportar,
    ESTADOS, REVISIONES, TIPOS, AREAS, PRIORIDADES
)


class Ventana:

    def __init__(self, raiz, cuenta):
        self.raiz = raiz
        self.cuenta = cuenta
        self.codigo = None
        self.campos = {}

        raiz.title("Mesa de Partes Digital | Santa Rita de Casia")
        raiz.geometry("1240x750")
        raiz.minsize(1000, 620)
        raiz.configure(bg="#eef2f7")

        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure(
            "Treeview",
            rowheight=27,
            font=("Segoe UI", 9)
        )
        estilo.configure(
            "Treeview.Heading",
            font=("Segoe UI", 9, "bold")
        )

        cab = tk.Frame(raiz, bg="#102a43", height=72)
        cab.pack(fill="x")

        tk.Label(
            cab,
            text="MESA DE PARTES DIGITAL",
            bg="#102a43",
            fg="white",
            font=("Segoe UI", 18, "bold")
        ).pack(side="left", padx=22, pady=18)

        tk.Label(
            cab,
            text=f"{cuenta['rol']} | {cuenta['usuario']}",
            bg="#102a43",
            fg="#d9e2ec"
        ).pack(side="right", padx=20)

        acciones = tk.Frame(raiz, bg="#d9e2ec")
        acciones.pack(fill="x")

        botones = [
            ("Nuevo", self.limpiar),
            ("Guardar", self.guardar),
            ("Editar expediente", self.editar),
            ("Ver documento", self.ver_documento),
            ("Eliminar", self.borrar),
            ("Derivar / seguimiento", self.derivar),
            ("Resumen", self.ver_resumen),
            ("Exportar CSV", self.exportar_csv)
        ]

        for nombre, funcion in botones:
            ttk.Button(
                acciones,
                text=nombre,
                command=funcion
            ).pack(side="left", padx=4, pady=7)

        cuerpo = tk.Frame(raiz, bg="#eef2f7")
        cuerpo.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=12
        )

        izq = tk.Frame(
            cuerpo,
            bg="white",
            padx=12,
            pady=12,
            width=350
        )
        izq.pack(side="left", fill="y", padx=(0, 12))
        izq.pack_propagate(False)

        tk.Label(
            izq,
            text="DATOS DEL EXPEDIENTE",
            bg="white",
            fg="#102a43",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", pady=(0, 8))

        form = tk.Frame(izq, bg="white")
        form.pack(fill="both", expand=True)

        definiciones = [
            ("solicitante", "Solicitante", None),
            ("documento", "Documento presentado", None),
            ("dni", "DNI", None),
            ("asunto", "Asunto", None),
            ("tipo_tramite", "Tipo de trámite", TIPOS),
            ("area_destino", "Área destino", AREAS),
            ("responsable", "Responsable", None),
            ("prioridad", "Prioridad", PRIORIDADES),
            ("estado", "Estado del trámite", ESTADOS),
            ("revision", "Estado de revisión", REVISIONES),
            ("observaciones", "Observaciones", None)
        ]

        for fila, (clave, etiqueta, opciones) in enumerate(definiciones):

            tk.Label(
                form,
                text=etiqueta,
                bg="white",
                fg="#334e68"
            ).grid(
                row=fila,
                column=0,
                sticky="w",
                pady=4
            )

            if opciones:
                widget = ttk.Combobox(
                    form,
                    values=opciones,
                    state="readonly",
                    width=22
                )
                widget.set(opciones[0])

            elif clave == "observaciones":
                widget = tk.Text(
                    form,
                    width=23,
                    height=3,
                    wrap="word",
                    font=("Segoe UI", 9)
                )

            else:
                widget = ttk.Entry(form, width=25)

            widget.grid(
                row=fila,
                column=1,
                sticky="ew",
                padx=(6, 0),
                pady=4
            )

            self.campos[clave] = widget

        form.columnconfigure(1, weight=1)

        tk.Label(
            izq,
            text="Archivo adjunto",
            bg="white",
            fg="#334e68"
        ).pack(anchor="w", pady=(6, 2))

        fila_archivo = tk.Frame(izq, bg="white")
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
        ).pack(side="right", padx=(4, 0))

        der = tk.Frame(
            cuerpo,
            bg="white",
            padx=12,
            pady=12
        )
        der.pack(side="left", fill="both", expand=True)

        tk.Label(
            der,
            text="REGISTRO Y SEGUIMIENTO",
            bg="white",
            fg="#102a43",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w")

        tk.Label(
            der,
            text="Buscar por código, solicitante, DNI, asunto, área o estado",
            bg="white",
            fg="#334e68"
        ).pack(anchor="w", pady=(8, 2))

        buscaf = tk.Frame(der, bg="white")
        buscaf.pack(fill="x", pady=(0, 8))

        self.termino = tk.StringVar()

        ttk.Entry(
            buscaf,
            textvariable=self.termino
        ).pack(side="left", fill="x", expand=True)

        self.termino.trace_add(
            "write",
            lambda *args: self.refrescar()
        )

        ttk.Button(
            buscaf,
            text="Limpiar",
            command=lambda: self.termino.set("")
        ).pack(side="left", padx=4)

        self.columnas = (
            "codigo", "fecha", "solicitante", "dni",
            "asunto", "area_destino", "prioridad", "estado"
        )

        self.tabla = ttk.Treeview(
            der,
            columns=self.columnas,
            show="headings"
        )

        etiquetas = [
            "Código", "Fecha", "Solicitante", "DNI",
            "Asunto", "Área", "Prioridad", "Estado"
        ]

        anchos = [85, 120, 145, 80, 200, 105, 90, 105]

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
                minwidth=60
            )

        sy = ttk.Scrollbar(
            der,
            orient="vertical",
            command=self.tabla.yview
        )

        sx = ttk.Scrollbar(
            der,
            orient="horizontal",
            command=self.tabla.xview
        )

        self.tabla.configure(
            yscrollcommand=sy.set,
            xscrollcommand=sx.set
        )

        self.tabla.pack(fill="both", expand=True)
        sy.pack(side="right", fill="y")
        sx.pack(fill="x")

        self.tabla.bind(
            "<<TreeviewSelect>>",
            self.seleccionar
        )

        self.mensaje = tk.StringVar(
            value="Sistema local listo"
        )

        tk.Label(
            raiz,
            textvariable=self.mensaje,
            bg="#d9e2ec",
            fg="#334e68",
            anchor="w",
            padx=12,
            pady=5
        ).pack(fill="x")

        self.refrescar()

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
                widget.set(widget["values"][0])

            else:
                widget.delete(0, "end")

        self.archivo.set("")
        self.tabla.selection_remove(
            self.tabla.selection()
        )

        self.mensaje.set(
            "Complete los datos del nuevo expediente."
        )

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
                "No se encuentra el archivo adjunto.\n\n"
                "Compruebe su ubicación."
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
            messagebox.showwarning(
                "Editar expediente",
                "Primero seleccione un expediente de la tabla."
            )
            return

        messagebox.showinfo(
            "Editar expediente",
            f"Está editando el expediente {self.codigo}.\n\n"
            "Modifique los campos del formulario y pulse Guardar "
            "para conservar los cambios."
        )

    def guardar(self):

        datos = self.datos()

        try:

            if datos["archivo"]:
                ruta = self.obtener_ruta_documento(datos["archivo"])

                if ruta and ruta.exists():
                    datos["archivo"] = self.guardar_adjunto(
                        str(ruta)
                    )

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
            "Confirmar",
            f"¿Eliminar {self.codigo}?"
        )

        if confirmar:

            try:
                eliminar(self.codigo)
                self.limpiar()
                self.refrescar()

            except ValueError as error:
                messagebox.showerror(
                    "Error",
                    str(error)
                )

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

            messagebox.showinfo(
                "Seguimiento",
                "Se actualizó el estado y la asignación."
            )

        except ValueError as error:
            messagebox.showerror(
                "Error",
                str(error)
            )

    def refrescar(self):

        if not hasattr(self, "tabla"):
            return

        for item in self.tabla.get_children():
            self.tabla.delete(item)

        registros = ordenar(
            buscar(self.termino.get()),
            "fecha"
        )

        for registro in registros:
            self.tabla.insert(
                "",
                "end",
                values=tuple(
                    registro.get(columna, "")
                    for columna in self.columnas
                )
            )

        self.mensaje.set(
            f"{len(registros)} expediente(s) mostrado(s)."
        )

    def seleccionar(self, evento=None):

        seleccion = self.tabla.selection()

        if seleccion:

            codigo = self.tabla.item(
                seleccion[0],
                "values"
            )[0]

            for registro in cargar():

                if registro["codigo"] == codigo:
                    self.llenar(registro)

                    self.mensaje.set(
                        "Expediente seleccionado: " + codigo
                    )

                    break

    def ordenar_por(self, campo):

        for item in self.tabla.get_children():
            self.tabla.delete(item)

        registros = ordenar(
            buscar(self.termino.get()),
            campo
        )

        for registro in registros:
            self.tabla.insert(
                "",
                "end",
                values=tuple(
                    registro.get(columna, "")
                    for columna in self.columnas
                )
            )

    def ver_resumen(self):

        total, estados = resumen()

        mensaje = (
            f"Total de expedientes: {total}\n\n"
            + "\n".join(
                f"{clave}: {valor}"
                for clave, valor in estados.items()
            )
        )

        messagebox.showinfo(
            "Resumen",
            mensaje
        )

    def exportar_csv(self):

        ruta = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Archivo CSV", "*.csv")],
            initialfile="reporte_expedientes.csv"
        )

        if ruta:

            cantidad = exportar(ruta)

            messagebox.showinfo(
                "Exportación",
                f"Se exportaron {cantidad} expedientes."
            )


def iniciar():

    preparar()

    raiz = tk.Tk()
    raiz.withdraw()

    login = tk.Toplevel(raiz)
    login.title("Acceso al sistema")
    login.geometry("360x290")
    login.resizable(False, False)
    login.configure(bg="#102a43")

    tk.Label(
        login,
        text="MESA DE PARTES",
        bg="#102a43",
        fg="white",
        font=("Segoe UI", 18, "bold")
    ).pack(pady=(22, 4))

    tk.Label(
        login,
        text="Santa Rita de Casia",
        bg="#102a43",
        fg="#d9e2ec"
    ).pack(pady=(0, 14))

    panel = tk.Frame(
        login,
        bg="white",
        padx=22,
        pady=16
    )

    panel.pack(
        fill="both",
        expand=True,
        padx=18,
        pady=(0, 18)
    )

    tk.Label(
        panel,
        text="Usuario",
        bg="white"
    ).pack(anchor="w")

    usuario = ttk.Entry(panel)
    usuario.pack(fill="x", pady=(3, 8))

    tk.Label(
        panel,
        text="Contraseña",
        bg="white"
    ).pack(anchor="w")

    clave = ttk.Entry(
        panel,
        show="*"
    )

    clave.pack(fill="x", pady=(3, 10))

    def entrar(event=None):

        cuenta = autenticar(
            usuario.get().strip(),
            clave.get()
        )

        if not cuenta:
            messagebox.showerror(
                "Acceso",
                "Usuario o contraseña incorrectos."
            )
            return

        login.destroy()
        raiz.deiconify()
        Ventana(raiz, cuenta)

    ttk.Button(
        panel,
        text="Ingresar",
        command=entrar
    ).pack(fill="x")

    tk.Label(
        panel,
        text="Acceso inicial: admin / admin123",
        bg="white",
        fg="#627d98",
        font=("Segoe UI", 8)
    ).pack(pady=(7, 0))

    clave.bind("<Return>", entrar)
    usuario.focus_set()

    raiz.mainloop()
