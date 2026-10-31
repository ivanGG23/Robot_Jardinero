"""Vista inicial del jardín. Ejecutar con: python interfaz.py."""

import tkinter as tk
from tkinter import messagebox, ttk

from jardin import COLUMNAS, FILAS, TOTAL_PLANTAS, Jardin, generar_jardin


TAMANO_CELDA = 60
MARGEN = 30


class AplicacionJardin:
    """Muestra un mapa fijo hasta que se pulsa Generar mapa."""

    def __init__(self, ventana: tk.Tk):
        self.ventana = ventana
        ventana.title("Robot Jardinero")
        ventana.resizable(False, False)
        self.jardin: Jardin | None = None
        self.sedientas = tk.StringVar(value="2")
        self.normales = tk.StringVar()
        self.estado = tk.StringVar()

        contenido = ttk.Frame(ventana, padding=16)
        contenido.grid()
        ttk.Label(contenido, text="Robot Jardinero", font=("Arial", 18, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        controles = ttk.Frame(contenido)
        controles.grid(row=1, column=0, sticky="w", pady=12)
        ttk.Label(controles, text="Plantas sedientas:").grid(row=0, column=0)
        self.selector = ttk.Combobox(
            controles, textvariable=self.sedientas, values=tuple(range(6)),
            state="readonly", width=3,
        )
        self.selector.grid(row=0, column=1, padx=8)
        self.selector.bind("<<ComboboxSelected>>", self.actualizar_cantidad)
        ttk.Label(controles, textvariable=self.normales).grid(row=0, column=2, padx=8)
        ttk.Button(controles, text="Generar mapa", command=self.nuevo_mapa).grid(
            row=0, column=3, padx=8
        )

        self.lienzo = tk.Canvas(
            contenido, width=COLUMNAS * TAMANO_CELDA + 2 * MARGEN,
            height=FILAS * TAMANO_CELDA + 2 * MARGEN,
            background="white", highlightthickness=0,
        )
        self.lienzo.grid(row=2, column=0)
        ttk.Label(
            contenido,
            text="N: normal (1)   S: sedienta (2)   B: base   L: llave\n"
                 "Gris: obstáculo   R: robot en la base   Plantas: todas secas",
            justify="left",
        ).grid(row=3, column=0, sticky="w", pady=(10, 4))
        ttk.Label(contenido, textvariable=self.estado).grid(
            row=4, column=0, sticky="w"
        )
        self.actualizar_cantidad()
        self.nuevo_mapa()

    def actualizar_cantidad(self, evento=None):
        """El selector prepara la configuración; el botón la aplica al mapa."""
        cantidad = int(self.sedientas.get())
        self.normales.set(f"Normales: {TOTAL_PLANTAS - cantidad}")
        self.estado.set("Pulsa Generar mapa para aplicar la selección.")

    def nuevo_mapa(self):
        """Sustituye el mapa completo por otro generado con la selección actual."""
        try:
            nuevo = generar_jardin(int(self.sedientas.get()))
        except (ValueError, RuntimeError) as error:
            messagebox.showerror("No se pudo generar el jardín", str(error), parent=self.ventana)
            return
        self.jardin = nuevo
        self.dibujar_jardin()
        cantidad = sum(planta.agua_necesaria == 2 for planta in nuevo.plantas)
        self.estado.set(
            f"Mapa actual: {cantidad} sedientas y {TOTAL_PLANTAS - cantidad} normales."
        )

    def dibujar_jardin(self):
        """Dibuja cada celda y, al final, el robot sobre la base."""
        if self.jardin is None:
            return
        self.lienzo.delete("all")
        plantas = {planta.posicion: planta for planta in self.jardin.plantas}
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
                color, etiqueta = "#edf5e8", ""
                if posicion in self.jardin.obstaculos:
                    color = "#667085"
                elif posicion in plantas:
                    sedienta = plantas[posicion].agua_necesaria == 2
                    color = "#f8b66a" if sedienta else "#f6dc91"
                    etiqueta = "S" if sedienta else "N"
                elif posicion == self.jardin.base:
                    color, etiqueta = "#b9d7ff", "B"
                elif posicion == self.jardin.llave:
                    color, etiqueta = "#90dce5", "L"
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
