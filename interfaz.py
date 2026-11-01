"""Vista inicial del jardín. Ejecutar con: python interfaz.py."""

import tkinter as tk
from tkinter import messagebox, ttk

from jardin import COLUMNAS, FILAS, TOTAL_PLANTAS, generar_jardin


TAMANO_CELDA = 60
MARGEN = 30
CAPACIDAD_TANQUE = 3


class AplicacionJardin:
    """Muestra un mapa fijo hasta que se pulsa Generar mapa."""

    def __init__(self, ventana):
        self.ventana = ventana
        ventana.title("Robot Jardinero")
        ventana.resizable(False, False)

        self.jardin = None
        self.sedientas = tk.StringVar(value="2")
        self.normales = tk.StringVar()
        self.estado = tk.StringVar()
        self.agua_inicial = tk.StringVar(value="3")
        self.meta_agua = tk.StringVar(value="Cualquier nivel")
        self.velocidad = tk.StringVar(value="Normal")
        self.agua_tanque = tk.IntVar(value=3)
        self.nivel_tanque = tk.StringVar()
        self.resumen = tk.StringVar()

        contenido = ttk.Frame(ventana, padding=16)
        contenido.grid()
        titulo = ttk.Label(
            contenido, text="Robot Jardinero", font=("Arial", 18, "bold")
        )
        titulo.grid(row=0, column=0, sticky="w")
        controles = ttk.Frame(contenido)
        controles.grid(row=1, column=0, sticky="w", pady=12)
        etiqueta_sedientas = ttk.Label(controles, text="Plantas sedientas:")
        etiqueta_sedientas.grid(row=0, column=0)
        self.selector = ttk.Combobox(
            controles, textvariable=self.sedientas, values=[0, 1, 2, 3, 4, 5],
            state="readonly", width=3,
        )
        self.selector.grid(row=0, column=1, padx=8)
        self.selector.bind("<<ComboboxSelected>>", self.actualizar_cantidad)
        etiqueta_normales = ttk.Label(controles, textvariable=self.normales)
        etiqueta_normales.grid(row=0, column=2, padx=8)
        boton_generar = ttk.Button(
            controles, text="Generar mapa", command=self.nuevo_mapa
        )
        boton_generar.grid(row=0, column=3, padx=8)

        ancho_jardin = COLUMNAS * TAMANO_CELDA + 2 * MARGEN
        alto_jardin = FILAS * TAMANO_CELDA + 2 * MARGEN
        self.lienzo = tk.Canvas(
            contenido, width=ancho_jardin,
            height=alto_jardin,
            background="white", highlightthickness=0,
        )
        self.lienzo.grid(row=2, column=0)
        leyenda = ttk.Label(
            contenido,
            text="N: normal (1)   S: sedienta (2)   B: base   L: llave\n"
                 "Gris: obstáculo   R: robot en la base   Plantas: todas secas",
            justify="left",
        )
        leyenda.grid(row=3, column=0, sticky="w", pady=(10, 4))
        etiqueta_estado = ttk.Label(contenido, textvariable=self.estado)
        etiqueta_estado.grid(row=4, column=0, sticky="w")
        self.crear_panel_configuracion(contenido)
        self.actualizar_cantidad()
        self.nuevo_mapa()
        self.actualizar_configuracion()

    def crear_panel_configuracion(self, contenido):
        """Agrupa las entradas sin cambiar la distribución del jardín."""
        panel = ttk.LabelFrame(contenido, text="Configuración", padding=12)
        panel.grid(row=1, column=1, rowspan=4, sticky="n", padx=(16, 0), pady=12)
        etiqueta_agua = ttk.Label(panel, text="Agua inicial (unidades):")
        etiqueta_agua.grid(row=0, column=0, sticky="w")
        self.selector_agua = ttk.Combobox(
            panel, textvariable=self.agua_inicial, values=[0, 1, 2, 3],
            state="readonly", width=20,
        )
        self.selector_agua.grid(row=1, column=0, sticky="ew", pady=(4, 12))
        self.selector_agua.bind("<<ComboboxSelected>>", self.actualizar_configuracion)
        etiqueta_meta = ttk.Label(panel, text="Agua requerida en la meta:")
        etiqueta_meta.grid(row=2, column=0, sticky="w")
        self.selector_meta = ttk.Combobox(
            panel, textvariable=self.meta_agua, values=["Cualquier nivel", "Lleno", "Vacío"],
            state="readonly", width=20,
        )
        self.selector_meta.grid(row=3, column=0, sticky="ew", pady=(4, 12))
        self.selector_meta.bind("<<ComboboxSelected>>", self.actualizar_configuracion)
        etiqueta_velocidad = ttk.Label(panel, text="Velocidad de animación:")
        etiqueta_velocidad.grid(row=4, column=0, sticky="w")
        self.selector_velocidad = ttk.Combobox(
            panel, textvariable=self.velocidad, values=["Lenta", "Normal", "Rápida"],
            state="readonly", width=20,
        )
        self.selector_velocidad.grid(row=5, column=0, sticky="ew", pady=(4, 12))
        self.selector_velocidad.bind("<<ComboboxSelected>>", self.actualizar_configuracion)
        etiqueta_tanque = ttk.Label(panel, text="Tanque al inicio:")
        etiqueta_tanque.grid(row=6, column=0, sticky="w")
        self.barra_tanque = ttk.Progressbar(
            panel, variable=self.agua_tanque, maximum=CAPACIDAD_TANQUE,
            mode="determinate", length=200,
        )
        self.barra_tanque.grid(row=7, column=0, sticky="ew", pady=4)
        etiqueta_nivel = ttk.Label(panel, textvariable=self.nivel_tanque)
        etiqueta_nivel.grid(row=8, column=0, sticky="w")
        separador = ttk.Separator(panel)
        separador.grid(row=9, column=0, sticky="ew", pady=12)
        titulo_resumen = ttk.Label(
            panel, text="Resumen del escenario", font=("Arial", 10, "bold")
        )
        titulo_resumen.grid(row=10, column=0, sticky="w")
        etiqueta_resumen = ttk.Label(
            panel, textvariable=self.resumen, justify="left", wraplength=220
        )
        etiqueta_resumen.grid(row=11, column=0, sticky="w", pady=6)
        aviso = ttk.Label(
            panel, text="La velocidad se aplicará cuando se integre la animación.",
            wraplength=220, justify="left",
        )
        aviso.grid(row=12, column=0, sticky="w", pady=(8, 0))

    def obtener_configuracion(self):
        """Devuelve valores simples para conectar después el modelo y la animación."""

        meta_elegida = self.meta_agua.get()
        if meta_elegida == "Lleno":
            agua_final = 3
        elif meta_elegida == "Vacío":
            agua_final = 0
        else:
            agua_final = None 

        velocidad_elegida = self.velocidad.get()
        if velocidad_elegida == "Lenta":
            intervalo = 1000
        elif velocidad_elegida == "Normal":
            intervalo = 500
        else:
            intervalo = 200

        configuracion = {}
        configuracion["agua_inicial"] = int(self.agua_inicial.get())
        configuracion["agua_final"] = agua_final
        configuracion["intervalo_ms"] = intervalo
        return configuracion

    def actualizar_configuracion(self, evento=None):
        """Actualiza la vista del inicio; no mueve al robot ni regenera el mapa."""
        configuracion = self.obtener_configuracion()
        agua = configuracion["agua_inicial"]
        self.agua_tanque.set(agua)
        self.nivel_tanque.set(f"{agua} / {CAPACIDAD_TANQUE} unidades")
        self.actualizar_resumen()

    def actualizar_resumen(self):
        """Describe el mapa actual, no una proporción pendiente de generar."""
        if self.jardin is None:
            return
        sedientas = self.contar_sedientas()
        configuracion = self.obtener_configuracion()
        intervalo = configuracion["intervalo_ms"]
        self.resumen.set(
            f"Mapa: {sedientas} sedientas, {TOTAL_PLANTAS - sedientas} normales.\n"
            f"Agua inicial: {self.agua_inicial.get()} de {CAPACIDAD_TANQUE}.\n"
            f"Meta: regar todas y volver a la base.\n"
            f"Agua final: {self.meta_agua.get()}.\n"
            f"Velocidad: {self.velocidad.get()} ({intervalo} ms por acción)."
        )

    def contar_sedientas(self):
        """Cuenta las plantas sedientas del mapa que se está mostrando."""
        cantidad = 0
        if self.jardin is not None:
            for planta in self.jardin.plantas:
                if planta.agua_necesaria == 2:
                    cantidad = cantidad + 1
        return cantidad

    def actualizar_cantidad(self, evento=None):
        """El selector prepara la configuración; el botón la aplica al mapa."""
        cantidad = int(self.sedientas.get())
        self.normales.set(f"Normales: {TOTAL_PLANTAS - cantidad}")
        self.estado.set("Pulsa Generar mapa para aplicar la selección.")

    def nuevo_mapa(self):
        """Sustituye el mapa completo por otro generado con la selección actual."""
        try:
            cantidad_elegida = int(self.sedientas.get())
            nuevo = generar_jardin(cantidad_elegida)
        except (ValueError, RuntimeError) as error:
            messagebox.showerror("No se pudo generar el jardín", str(error), parent=self.ventana)
            return
        self.jardin = nuevo
        self.dibujar_jardin()
        cantidad = self.contar_sedientas()
        self.estado.set(
            f"Mapa actual: {cantidad} sedientas y {TOTAL_PLANTAS - cantidad} normales."
        )
        self.actualizar_resumen()

    def dibujar_jardin(self):
        """Dibuja cada celda y, al final, el robot sobre la base."""
        if self.jardin is None:
            return
        self.lienzo.delete("all")
        plantas = {}
        for planta in self.jardin.plantas:
            plantas[planta.posicion] = planta
        for indice in range(COLUMNAS):
            self.lienzo.create_text(
                MARGEN + (indice + 0.5) * TAMANO_CELDA, MARGEN / 2, text=str(indice)
            )
        for fila in range(FILAS):
            self.lienzo.create_text(
                MARGEN / 2, MARGEN + (fila + 0.5) * TAMANO_CELDA, text=str(fila)
            )
            for columna in range(COLUMNAS):
                posicion = (fila, columna)
                color = "#edf5e8"
                etiqueta = ""
                if posicion in self.jardin.obstaculos:
                    color = "#667085"
                elif posicion in plantas:
                    planta = plantas[posicion]
                    if planta.agua_necesaria == 2:
                        color = "#f8b66a"
                        etiqueta = "S"
                    else:
                        color = "#f6dc91"
                        etiqueta = "N"
                elif posicion == self.jardin.base:
                    color = "#b9d7ff"
                    etiqueta = "B"
                elif posicion == self.jardin.llave:
                    color = "#90dce5"
                    etiqueta = "L"
                x = MARGEN + columna * TAMANO_CELDA
                y = MARGEN + fila * TAMANO_CELDA
                self.lienzo.create_rectangle(
                    x, y, x + TAMANO_CELDA, y + TAMANO_CELDA,
                    fill=color, outline="#a4b09e", tags="celda",
                )
                if etiqueta:
                    self.lienzo.create_text(
                        x + TAMANO_CELDA / 2, y + 13,
                        text=etiqueta, font=("Arial", 12, "bold"), tags="elemento",
                    )
        fila, columna = self.jardin.base
        x = MARGEN + columna * TAMANO_CELDA
        y = MARGEN + fila * TAMANO_CELDA
        self.lienzo.create_oval(
            x + 17, y + 27, x + 43, y + 53,
            fill="#3046a5", outline="white", tags="robot",
        )
        self.lienzo.create_text(
            x + 30, y + 40, text="R", fill="white",
            font=("Arial", 11, "bold"), tags="robot",
        )


def main():
    ventana = tk.Tk()
    AplicacionJardin(ventana)
    ventana.mainloop()


if __name__ == "__main__":
    main()
