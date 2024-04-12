import random
import time
import tkinter as tk
from tkinter import messagebox

import unidecode

from juego_ahorcado.clasificacion import SistemaClasificacion
from juego_ahorcado.dialogo_nombre import NombreDialog
from juego_ahorcado.palabras import CATEGORIAS_PALABRAS


class JuegoAhorcado:
    """
    Clase para el juego del ahorcado.
    """
    def __init__(self, master):
        """
        Inicializa la ventana del juego y los atributos del juego.

        Parameters:
            master (Tk): La ventana principal del juego.
        """
        self.master = master  # Establece la ventana principal del juego
        self.inicializar_ventana()

        self.mostrado_bienvenida = False  # Bandera para controlar si se ha mostrado el mensaje de bienvenida
        self.categoria_actual, self.palabra_secreta = self.elegir_palabra()  # Selecciona una palabra al azar para el juego
        self.letras_adivinadas = []  # Lista para almacenar las letras que han sido adivinadas correctamente
        self.letras_falladas = []  # Lista para almacenar las letras que han sido incorrectamente propuestas
        self.fallos = 0  # Contador de los fallos del jugador
        self.puntos = 0  # Puntuación del jugador
        self.acumular_puntos_fallos = 0  # Contador para llevar un registro acumulado de los puntos de los fallos
        # Inicializar el sistema de clasificación
        self.sistema_clasificacion = SistemaClasificacion()
        # Cargar las puntuaciones guardadas
        self.sistema_clasificacion.cargar_puntuaciones()

        self.configurar_interfaz()

        # Mostrar mensaje de bienvenida si es la primera vez que se ejecuta el juego
        if not self.mostrado_bienvenida:
            self.mostrar_mensaje_bienvenida()
            self.mostrado_bienvenida = True

        # Iniciar contador de tiempo
        self.tiempo_inicio = time.time()
        self.tiempo_transcurrido_total = 0
        self.actualizar_tiempo()

    def inicializar_ventana(self):
        self.master.title("El Ahorcado")
        self.master.resizable(False, False)
        self.master.minsize(400, 250)
        self.master.maxsize(400, 250)
        self.centra_ventana()

    def centra_ventana(self):
        self.master.update_idletasks()
        width = self.master.winfo_width()
        height = self.master.winfo_height()
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        self.master.geometry(f"{width}x{height}+{x}+{y}")

    def configurar_interfaz(self):
        # Etiqueta para mostrar la categoría
        self.label_categoria = tk.Label(self.master, text="Categoría - " + self.categoria_actual)
        self.label_categoria.grid(row=0, column=0, columnspan=4, padx=10, pady=5)

        # Etiqueta para mostrar la palabra oculta
        self.label_palabra = tk.Label(self.master, text=self.mostrar_palabra_oculta())
        self.label_palabra.grid(row=1, column=0, columnspan=4, padx=10, pady=10)

        # Etiqueta para mostrar el número de fallos
        self.label_fallos = tk.Label(self.master, text=f"Fallos: {self.fallos}/8")
        self.label_fallos.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        # Etiqueta para mostrar las letras falladas
        self.label_letras_falladas = tk.Label(self.master, text="")
        self.label_letras_falladas.grid(row=2, column=0, columnspan=4, padx=10, pady=10)

        # Etiqueta para mostrar los puntos
        self.label_puntos = tk.Label(self.master, text=f"Puntos: {self.puntos}")
        self.label_puntos.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Etiqueta para mostrar el tiempo transcurrido
        self.label_tiempo = tk.Label(self.master, text="Tiempo: 1:00")
        self.label_tiempo.grid(row=0, column=3, padx=10, pady=10, sticky="e")

        # Frame para los botones del teclado
        self.frame_teclado = tk.Frame(self.master)
        self.frame_teclado.grid(row=4, column=0, columnspan=4, padx=10, pady=10)

        self.botones_teclado = []  # Lista para almacenar los botones del teclado
        letras = ["QWERTYUIOP", "ASDFGHJKLÑ", "ZXCVBNM"]
        for i, linea in enumerate(letras):
            for j, letra in enumerate(linea):
                # Crea un botón para cada letra del teclado
                boton = tk.Button(self.frame_teclado, text=letra, width=4, command=lambda l=letra: self.adivinar_letra(l))
                boton.grid(row=i, column=j)
                self.botones_teclado.append(boton)

    def guardar_puntuacion(self):
        nombre_jugador = self.obtener_nombre_jugador()
        if nombre_jugador is not None:  # Verifica si se proporcionó un nombre
            self.sistema_clasificacion.agregar_puntuacion(nombre_jugador, self.puntos)
            self.sistema_clasificacion.guardar_puntuaciones()

    def obtener_nombre_jugador(self):
        dialog = NombreDialog(self.master)  # Crea una instancia del diálogo personalizado
        return dialog.result  # Devuelve el resultado después de que se cierra el diálogo

    def mostrar_clasificacion(self):
        clasificacion = self.sistema_clasificacion.obtener_clasificacion()
        clasificacion_str = "\n".join(f"{i + 1}. {nombre}: {puntos}" for i, (nombre, puntos) in enumerate(clasificacion))
        messagebox.showinfo("Tabla de Clasificación", f"Tabla de Clasificación:\n{clasificacion_str}")

    def mostrar_mensaje_bienvenida(self):
        """
        Muestra un mensaje de bienvenida cuando se inicia el juego.
        """
        messagebox.showinfo("¡Bienvenido!",
                            "Dispones de 8 fallos y 1 minuto para resolver cada palabra.\nLetra acertada suma 1 punto.\nTexto resuelto suma 50 puntos.\n"
                            "+1 punto por segundo restante.\n-3 puntos por fallo.")

    def elegir_palabra(self):
        """
        Elige una palabra al azar de una categoría predefinida.

        Returns:
            str: La categoría seleccionada.
            str: La palabra seleccionada.
        """
        # Selección aleatoria de una categoría
        categoria = random.choice(list(CATEGORIAS_PALABRAS.keys()))
        # Selección aleatoria de una palabra de la categoría seleccionada
        palabra = random.choice(CATEGORIAS_PALABRAS[categoria]).upper()
        return categoria, palabra

    def mostrar_palabra_oculta(self):
        """
        Crea la representación visual de la palabra oculta, con guiones para las letras no adivinadas.

        Returns:
            str: La palabra oculta con guiones para las letras no adivinadas.
        """
        palabra_oculta = ""  # Inicializa una cadena vacía para la palabra oculta
        for letra in self.palabra_secreta:  # Itera sobre cada letra de la palabra secreta
            letra_normalizada = unidecode.unidecode(letra)  # Normaliza la letra para manejar caracteres especiales
            if letra_normalizada in [unidecode.unidecode(l) for l in self.letras_adivinadas]:  # Comprueba si la letra ha sido adivinada
                palabra_oculta += letra  # Si la letra ha sido adivinada, la agrega a la palabra oculta
            else:
                if letra == " ":  # Si la letra es un espacio, agrega un espacio a la palabra oculta
                    palabra_oculta += " "
                elif letra == "-":
                    palabra_oculta += "-"
                else:
                    palabra_oculta += "_"  # Si la letra no ha sido adivinada, agrega un guion bajo a la palabra oculta
        return " ".join(palabra_oculta)  # Retorna la palabra oculta como una cadena con espacios entre cada letra

    def adivinar_letra(self, letra):
        """
        Maneja la lógica cuando el jugador intenta adivinar una letra.

        Parameters:
            letra (str): La letra que el jugador intenta adivinar.
        """
        letra_original = letra  # Conserva la letra original antes de normalizarla
        letras_secretas = self.palabra_secreta  # Lista de letras de la palabra secreta

        # Normalizar la letra antes de compararla
        letra = unidecode.unidecode(letra) if letra != "Ñ" else letra

        if letra in letras_secretas:
            # Si la letra está en la palabra secreta, se agrega a las letras adivinadas, se suma 1 punto y se actualiza la interfaz
            self.letras_adivinadas.append(letra_original)
            self.puntos += 1
        else:
            # Si la letra no está en la palabra secreta, se agrega a las letras falladas, se incrementa el contador de fallos
            # y se acumulan los puntos de los fallos
            self.letras_falladas.append(letra_original)
            self.fallos += 1
            self.acumular_puntos_fallos += 3

        self.actualizar_interfaz()

        # Desactivar el botón presionado
        for boton in self.botones_teclado:
            if boton["text"] == letra_original:
                boton.config(state="disabled", bg="lightgray")  # Desactiva el botón y cambia el color de fondo

        letras_adivinadas_y_variantes = set(self.letras_adivinadas)
        letras_adivinadas_y_variantes.update(["Á", "É", "Í", "Ó", "Ú"])  # Agregar las variantes con tilde

        # Comprobar si la letra con tilde está en la palabra secreta y no está en las letras adivinadas,
        # en ese caso, se agrega a las letras adivinadas
        for l in letras_secretas:
            if unidecode.unidecode(l) == letra and l not in self.letras_adivinadas:
                self.letras_adivinadas.append(l)

        # Comprobar si el jugador ha perdido o ganado después de cada intento
        if self.fallos == 8:
            self.perder()  # Llama a la función para manejar la situación de perder
        elif all(l in letras_adivinadas_y_variantes or l == " " or l == "-" for l in self.palabra_secreta):
            self.ganar()  # Llama a la función para manejar la situación de ganar

    def actualizar_interfaz(self):
        """
        Actualiza la interfaz gráfica con la información más reciente del juego.
        """
        # Actualiza la etiqueta de la palabra oculta con la representación visual actualizada
        self.label_palabra.config(text=self.mostrar_palabra_oculta())
        # Actualiza la etiqueta de fallos con el conteo actualizado de fallos
        self.label_fallos.config(text=f"Fallos: {self.fallos}/8")
        # Actualiza la etiqueta de letras falladas con la lista actualizada de letras falladas
        self.label_letras_falladas.config(text=" ".join(self.letras_falladas))
        # Actualiza la etiqueta de puntos con el puntaje actualizado
        self.label_puntos.config(text=f"Puntos: {self.puntos}")

    def perder(self):
        """
        Maneja las acciones cuando el jugador pierde el juego.
        """
        self.tiempo_inicio = None  # Detener el tiempo
        # Muestra un mensaje indicando que el jugador perdió y su puntuación
        total_puntos = self.puntos - self.acumular_puntos_fallos
        if self.tiempo_transcurrido_total >= 60 and total_puntos <= 0:
            self.puntos = 0
            messagebox.showinfo("¡Perdiste!", f"Fin del juego\nSe ha agotado el tiempo\n"f"No has conseguido ningún punto...")
        if self.tiempo_transcurrido_total >= 60 and total_puntos > 0:
            # Si el jugador tenía puntos, se resta la acumulación de puntos por fallos de su puntuación total y se muestra un mensaje
            self.puntos -= self.acumular_puntos_fallos
            messagebox.showinfo("¡Perdiste!", f"Fin del juego\nSe ha agotado el tiempo\n"f"Has conseguido un total de: ¡{self.puntos} puntos!")
        elif total_puntos <= 0 < self.fallos >= 8:
            self.puntos = 0
            messagebox.showinfo("¡Perdiste!", f"Fin del juego\nHas superado los fallos permitidos\nNo has conseguido ningún punto...")
        else:
            # Si el jugador tenía puntos, se resta la acumulación de puntos por fallos de su puntuación total y se muestra un mensaje
            self.puntos -= self.acumular_puntos_fallos
            messagebox.showinfo("¡Perdiste!", f"Fin del juego\nHas superado los fallos permitidos\nHas conseguido un total de: ¡{self.puntos} puntos!")

        if self.puntos > 0:
            self.guardar_puntuacion()  # Guardar la puntuación cuando el jugador gana puntos
            self.mostrar_clasificacion()  # Mostrar la tabla de clasificación cuando el jugador ha ganado puntos
        # Reinicia la puntuación y el juego
        self.puntos = 0
        self.reset_juego()

    def ganar(self):
        """
        Maneja las acciones cuando el jugador gana el juego.
        """
        self.tiempo_inicio = None  # Detener el tiempo
        # Calcula los puntos ganados por el jugador
        self.puntos += 50 + (60 - self.tiempo_transcurrido_total) - self.acumular_puntos_fallos
        # Muestra un mensaje de felicitación al jugador
        messagebox.showinfo("¡Felicidades!", f"¡Correcto, a por la siguiente palabra!")
        # Reinicia el juego
        self.reset_juego()

    def restaurar_botones(self):
        """
        Restaura los botones del teclado al estado inicial.
        """
        for boton in self.botones_teclado:
            boton.config(state="normal", bg="SystemButtonFace")

    def reset_juego(self):
        """
        Reinicia el juego con una nueva palabra secreta y restablece los atributos del juego.
        """
        self.categoria_actual, self.palabra_secreta = self.elegir_palabra()
        self.letras_adivinadas = []
        self.letras_falladas = []
        self.fallos = 0
        self.acumular_puntos_fallos = 0
        self.actualizar_interfaz()
        self.tiempo_inicio = time.time()
        self.restaurar_botones()
        # Actualiza la etiqueta de la categoría con la nueva categoría seleccionada
        self.label_categoria.config(text="Categoría - " + self.categoria_actual)

    def actualizar_tiempo(self):
        """
        Actualiza el contador de tiempo y gestiona las acciones cuando se agota el tiempo.
        """
        # Calcula el tiempo transcurrido desde el inicio del juego
        if self.tiempo_inicio is not None:
            tiempo_transcurrido = int(time.time() - self.tiempo_inicio)
            self.tiempo_transcurrido_total = tiempo_transcurrido  # Actualiza el tiempo total transcurrido
        else:
            tiempo_transcurrido = self.tiempo_transcurrido_total  # Si el juego ha terminado, utiliza el tiempo total

        # Calcula el tiempo restante y lo muestra en el formato "minutos:segundos"
        tiempo_restante = max(0, 60 - tiempo_transcurrido)
        minutos = tiempo_restante // 60
        segundos = tiempo_restante % 60
        self.label_tiempo.config(text=f"Tiempo: {minutos}:{segundos:02d}")

        # Si queda tiempo restante, programa una llamada a actualizar_tiempo después de 1 segundo
        if tiempo_restante > 0:
            self.master.after(1000, self.actualizar_tiempo)
        else:
            # Si se agota el tiempo, se llama a la función perder y se programa otra llamada a actualizar_tiempo después de 1 segundo
            self.perder()
            self.master.after(1000, self.actualizar_tiempo)