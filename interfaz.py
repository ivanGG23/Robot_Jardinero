"""Ventana del Robot Jardinero: configuración, búsqueda y animación.

Ejecutar con: python interfaz.py
"""

import tkinter as tk
from tkinter import messagebox, ttk

from busqueda import resolver
from jardin import COLUMNAS, FILAS, TOTAL_PLANTAS, generar_jardin
from modelo import Escenario, simular_plan


TAMANO_CELDA = 60
MARGEN = 30
CAPACIDAD_TANQUE = 3


class AplicacionJardin:
    """Muestra un mapa fijo hasta que se pulsa Generar mapa; resuelve y anima el plan."""

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
        self.resultados = tk.StringVar(value="Sin resultados. Pulsa Resolver.")

        # Plan actual y animación.
        self.resultado = None          # Resultado de la última búsqueda con solución
        self.trayectoria = []          # estados del plan, incluido el inicial
        self.paso = 0                  # posición actual dentro de la trayectoria
        self.trabajo_animacion = None  # identificador del after de la animación

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
        boton_resolver = ttk.Button(
            controles, text="Resolver", command=self.resolver_plan
        )
        boton_resolver.grid(row=0, column=4, padx=4)
        self.boton_repetir = ttk.Button(
            controles, text="Repetir animación", command=self.iniciar_animacion,
            state="disabled",
        )
        self.boton_repetir.grid(row=0, column=5, padx=4)

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
                 "Gris: obstáculo   Círculo azul con R: robot   Verde: planta regada",
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
        """Agrupa las entradas y los resultados sin cambiar la distribución del jardín."""
        panel = ttk.LabelFrame(contenido, text="Configuración", padding=12)
        panel.grid(row=1, column=1, rowspan=4, sticky="n", padx=(16, 0), pady=12)
        etiqueta_agua = ttk.Label(panel, text="Agua inicial (unidades):")
        etiqueta_agua.grid(row=0, column=0, sticky="w")
        self.selector_agua = ttk.Combobox(
            panel, textvariable=self.agua_inicial, values=[0, 1, 2, 3],
            state="readonly", width=20,
        )
        self.selector_agua.grid(row=1, column=0, sticky="ew", pady=(4, 12))
        self.selector_agua.bind("<<ComboboxSelected>>", self.cambio_configuracion)
        etiqueta_meta = ttk.Label(panel, text="Agua requerida en la meta:")
        etiqueta_meta.grid(row=2, column=0, sticky="w")
        self.selector_meta = ttk.Combobox(
            panel, textvariable=self.meta_agua, values=["Cualquier nivel", "Lleno", "Vacío"],
            state="readonly", width=20,
        )
        self.selector_meta.grid(row=3, column=0, sticky="ew", pady=(4, 12))
        self.selector_meta.bind("<<ComboboxSelected>>", self.cambio_configuracion)
        etiqueta_velocidad = ttk.Label(panel, text="Velocidad de animación:")
        etiqueta_velocidad.grid(row=4, column=0, sticky="w")
        self.selector_velocidad = ttk.Combobox(
            panel, textvariable=self.velocidad, values=["Lenta", "Normal", "Rápida"],
            state="readonly", width=20,
        )
        self.selector_velocidad.grid(row=5, column=0, sticky="ew", pady=(4, 12))
        self.selector_velocidad.bind("<<ComboboxSelected>>", self.actualizar_configuracion)
        etiqueta_tanque = ttk.Label(panel, text="Tanque:")
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
        separador_resultados = ttk.Separator(panel)
        separador_resultados.grid(row=12, column=0, sticky="ew", pady=12)
        titulo_resultados = ttk.Label(
            panel, text="Resultados de la búsqueda", font=("Arial", 10, "bold")
        )
        titulo_resultados.grid(row=13, column=0, sticky="w")
        etiqueta_resultados = ttk.Label(
            panel, textvariable=self.resultados, justify="left", wraplength=220
        )
        etiqueta_resultados.grid(row=14, column=0, sticky="w", pady=6)

    def obtener_configuracion(self):
        """Devuelve valores simples para conectar el modelo y la animación."""

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

    def cambio_configuracion(self, evento=None):
        """Agua inicial o final: el plan calculado deja de ser válido."""
        self.invalidar_plan()
        self.actualizar_configuracion()
        self.estado.set("Configuración cambiada. Pulsa Resolver para calcular un plan.")

    def actualizar_configuracion(self, evento=None):
        """Actualiza el tanque y el resumen; no mueve al robot ni regenera el mapa."""
        agua = self.obtener_configuracion()["agua_inicial"]
        if not self.trayectoria:
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
        self.invalidar_plan()
        cantidad = self.contar_sedientas()
        self.estado.set(
            f"Mapa actual: {cantidad} sedientas y {TOTAL_PLANTAS - cantidad} normales. "
            "Pulsa Resolver."
        )
        self.actualizar_resumen()

    # ------------------------------------------------------------------
    # Búsqueda
    # ------------------------------------------------------------------

    def invalidar_plan(self):
        """Descarta el plan, detiene la animación y muestra el estado inicial."""
        self.detener_animacion()
        self.resultado = None
        self.trayectoria = []
        self.paso = 0
        self.resultados.set("Sin resultados. Pulsa Resolver.")
        self.boton_repetir.state(["disabled"])
        self.mostrar_estado(None)

    def resolver_plan(self):
        """Busca el plan con IDA* y, si existe, lo anima."""
        self.invalidar_plan()
        configuracion = self.obtener_configuracion()
        escenario = Escenario(
            self.jardin, configuracion["agua_inicial"], configuracion["agua_final"]
        )
        self.estado.set("Calculando el plan...")
        self.resultados.set("Calculando...")
        self.ventana.update_idletasks()   # muestra el aviso antes de buscar
        resultado = resolver(escenario)

        if not resultado.hay_solucion:
            self.estado.set(resultado.mensaje)
            self.resultados.set(
                f"{resultado.mensaje}\n"
                f"Estados alcanzables revisados: {resultado.nodos_expandidos}\n"
                f"Tiempo de búsqueda: {resultado.tiempo:.3f} s"
            )
            return

        self.resultado = resultado
        self.trayectoria = simular_plan(escenario, resultado.plan)
        self.resultados.set(
            f"Costo total: {resultado.costo}\n"
            f"  Movimientos: {resultado.movimientos}\n"
            f"  Riegos: {resultado.riegos}\n"
            f"  Rellenos: {resultado.rellenos}\n"
            f"Nodos expandidos: {resultado.nodos_expandidos}\n"
            f"Tiempo de búsqueda: {resultado.tiempo:.3f} s\n"
            f"Plantas regadas: {resultado.plantas_regadas} de {TOTAL_PLANTAS}\n"
            f"Agua consumida: {resultado.agua_consumida}\n"
            f"Agua restante: {resultado.agua_restante}\n"
            f"Agua desperdiciada: {resultado.agua_desperdiciada}\n"
            f"Meta cumplida: {'sí' if resultado.meta_cumplida else 'no'}"
        )
        self.boton_repetir.state(["!disabled"])
        self.iniciar_animacion()

    # ------------------------------------------------------------------
    # Animación
    # ------------------------------------------------------------------

    def iniciar_animacion(self):
        """Reproduce el plan desde el estado inicial (sirve también para repetir)."""
        if not self.trayectoria:
            return
        self.detener_animacion()
        self.paso = 0
        self.mostrar_estado(self.trayectoria[0])
        self.estado.set(f"Plan encontrado: {self.resultado.costo} acciones.")
        self.trabajo_animacion = self.ventana.after(
            self.obtener_configuracion()["intervalo_ms"], self.avanzar_animacion
        )

    def detener_animacion(self):
        if self.trabajo_animacion is not None:
            self.ventana.after_cancel(self.trabajo_animacion)
            self.trabajo_animacion = None

    def avanzar_animacion(self):
        """Muestra el siguiente estado del plan calculado por la búsqueda."""
        self.trabajo_animacion = None
        plan = self.resultado.plan
        self.paso += 1
        self.mostrar_estado(self.trayectoria[self.paso])
        if self.paso < len(plan):
            self.estado.set(f"Paso {self.paso} de {len(plan)}: {plan[self.paso - 1]}")
            self.trabajo_animacion = self.ventana.after(
                self.obtener_configuracion()["intervalo_ms"], self.avanzar_animacion
            )
        else:
            self.estado.set(
                f"Plan completado en {len(plan)} acciones. "
                "Las cinco plantas están regadas y el robot volvió a la base."
            )

    # ------------------------------------------------------------------
    # Dibujo
    # ------------------------------------------------------------------

    def mostrar_estado(self, estado):
        """Dibuja el jardín y el tanque para un estado del modelo.

        Con estado None se muestra el inicio: robot en la base, plantas secas y
        el agua inicial elegida.
        """
        if estado is None:
            agua = int(self.agua_inicial.get())
        else:
            agua = estado.agua
        self.agua_tanque.set(agua)
        self.nivel_tanque.set(f"{agua} / {CAPACIDAD_TANQUE} unidades")
        self.dibujar_jardin(estado)

    def dibujar_jardin(self, estado=None):
        """Dibuja cada celda y, al final, el robot en su posición actual."""
        if self.jardin is None:
            return
        self.lienzo.delete("all")
        plantas = {}
        for indice, planta in enumerate(self.jardin.plantas):
            plantas[planta.posicion] = (indice, planta)
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
                regada = False
                if posicion in self.jardin.obstaculos:
                    color = "#667085"
                elif posicion in plantas:
                    indice, planta = plantas[posicion]
                    regada = estado is not None and estado.regadas[indice]
                    if regada:
                        color = "#8fd19e"
                    elif planta.agua_necesaria == 2:
                        color = "#f8b66a"
                    else:
                        color = "#f6dc91"
                    etiqueta = "S" if planta.agua_necesaria == 2 else "N"
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
                if regada:
                    self.lienzo.create_text(
                        x + TAMANO_CELDA / 2, y + TAMANO_CELDA - 8,
                        text="regada", font=("Arial", 8), tags="elemento",
                    )
        fila, columna = self.jardin.base if estado is None else estado.posicion
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