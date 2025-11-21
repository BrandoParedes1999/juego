import time
import random
import math
import pygame
import sys
from config_manager import DIFICULTADES, cargar_progreso, cargar_audio, registrar_puntuacion
from scenes.utils import ESTADO_COMPLETADO, ESTADO_FINAL, ESTADO_JUGANDO, ESTADO_MENU, ESTADO_PAUSA
from scenes.utils import cargar_imagenes_barco, ANCHO_PANTALLA, ALTO_PANTALLA, cargar_imagen_corazon

# Carga de Audio (Variables globales)
config = None 
SFX_ACIERTO, SFX_ERROR, SFX_VICTORIA, SFX_DERROTA, RUTA_MUSICA_NORMAL, RUTA_MUSICA_PELIGRO = None, None, None, None, None, None

def inicializar_audio_global(config_obj):
    global config, SFX_ACIERTO, SFX_ERROR, SFX_VICTORIA, SFX_DERROTA, RUTA_MUSICA_NORMAL, RUTA_MUSICA_PELIGRO
    config = config_obj
    SFX_ACIERTO, SFX_ERROR, SFX_VICTORIA, SFX_DERROTA, RUTA_MUSICA_NORMAL, RUTA_MUSICA_PELIGRO = cargar_audio(config)
    return config 

# Cargar la imagen de corazón (Necesaria para play_scene)
IMAGEN_CORAZON_GLOBAL = cargar_imagen_corazon()

class JuegoAhorcado:
    def __init__(self, palabras_datos, config):
        self.palabras_datos = palabras_datos
        self.config = config
        
        dif = DIFICULTADES[config.dificultad]
        self.max_errores = dif["max_errores"]
        self.tiempo_inicial_ronda = dif["tiempo"]
        self.tiempo_penalizacion = dif["penalizacion"]
        self.tiempo_bono = dif["bono"]
        
        self.puntuacion = 0
        self.letras_adivinadas = []
        self.letras_correctas = set()
        self.letras_incorrectas = set()
        self.teclado_letras = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"
        self.estado_juego = ESTADO_MENU
        self.racha_actual = 0
        self.juego_terminado = False
        self.botones_teclado = {} 
        
        # Carga de recursos
        self.IMAGENES_BARCO = cargar_imagenes_barco(self.max_errores)
        self.top_scores, self.progreso_galeria = cargar_progreso(config.escenario_actual, palabras_datos)
        self.palabras_pendientes = self._obtener_palabras_pendientes()
        
        # Timers
        self.tiempo_restante = 0
        self.tiempo_inicio_ronda = 0
        self.segundos_criticos_alcanzados = []
        self.tiempo_inicio_intro = 0
        self.tiempo_fin_partida = 0
        
        # Efectos
        self.efecto_vibracion_activo = False
        self.tiempo_vibracion_fin = 0
        self.ultimo_feedback_letra = None
        self.tiempo_feedback_fin = 0
        self.duracion_feedback = 0.3
        self.borde_peligro_activo = False

        self.reiniciar_ronda()
    
    def _obtener_palabras_pendientes(self):
        return [p for p, adivinada in self.progreso_galeria.items() if not adivinada]
        
    # ... (El resto de la clase sigue igual, ya que la lógica es robusta)
    def reiniciar_ronda(self):
        self.errores = 0
        self.letras_adivinadas.clear()
        self.letras_correctas.clear()
        self.letras_incorrectas.clear()
        self.juego_terminado = False
        self.efecto_vibracion_activo = False
        self.ultimo_feedback_letra = None
        self.segundos_criticos_alcanzados.clear()
        self.tiempo_fin_partida = 0
        self.racha_actual = 0
        self.borde_peligro_activo = False
        
        palabras_activas = self._obtener_palabras_pendientes()
            
        if not palabras_activas and len(self.palabras_datos) > 0:
            self.estado_juego = ESTADO_COMPLETADO
            return
            
        if palabras_activas:
            self.palabra_actual = random.choice(palabras_activas)
        else:
            if not self.palabras_datos:
                self.palabra_actual = "ERROR"
            else:
                self.palabra_actual = random.choice(list(self.palabras_datos.keys()))
        
        if RUTA_MUSICA_NORMAL and pygame.mixer.music.get_busy():
            pygame.mixer.music.load(RUTA_MUSICA_NORMAL)
            pygame.mixer.music.set_volume(self.config.volumen_musica)
            pygame.mixer.music.play(-1)
        
        self.tiempo_inicio_ronda = time.time()
        self.tiempo_restante = self.tiempo_inicial_ronda
        self.palabra_oculta = "_" * len(self.palabra_actual)
    
    def recompensar_tiempo(self, segundos_extra):
        self.tiempo_inicio_ronda += segundos_extra

    def actualizar_tiempo(self):
        if self.estado_juego != ESTADO_JUGANDO:
            return
            
        tiempo_transcurrido = time.time() - self.tiempo_inicio_ronda
        tiempo_actual = max(0, self.tiempo_inicial_ronda - tiempo_transcurrido)
        self.tiempo_restante = math.ceil(tiempo_actual)
        segundos_restantes = self.tiempo_restante
        
        if segundos_restantes <= 20 and 20 not in self.segundos_criticos_alcanzados:
            self.errores = min(self.errores + 1, self.max_errores - 1)
            self.segundos_criticos_alcanzados.append(20)
            self.activar_vibracion()
            self.borde_peligro_activo = True
            
            if RUTA_MUSICA_PELIGRO: 
                pygame.mixer.music.load(RUTA_MUSICA_PELIGRO)
                pygame.mixer.music.set_volume(self.config.volumen_musica)
                pygame.mixer.music.play(-1)

        if segundos_restantes <= 0:
            self.errores = self.max_errores 
            self.estado_juego = ESTADO_FINAL
            return "PERDIDO"
        
        return "JUGANDO"

    def verificar_letra(self, letra):
        if letra in self.letras_adivinadas or self.juego_terminado:
            return
        
        self.letras_adivinadas.append(letra)
        letra_correcta = False
        
        if letra in self.palabra_actual:
            letra_correcta = True
            self.letras_correctas.add(letra)
            self.puntuacion += 10
            self.racha_actual += 1
            
            nueva_palabra = "".join([letra if self.palabra_actual[i] == letra else self.palabra_oculta[i] for i in range(len(self.palabra_actual))])
            self.palabra_oculta = nueva_palabra
            
            if SFX_ACIERTO: SFX_ACIERTO.set_volume(self.config.volumen_sfx); SFX_ACIERTO.play()

        else:
            self.letras_incorrectas.add(letra)
            self.errores += 1
            self.activar_vibracion()
            self.tiempo_inicio_ronda -= self.tiempo_penalizacion
            self.racha_actual = 0
            
            if SFX_ERROR: SFX_ERROR.set_volume(self.config.volumen_sfx); SFX_ERROR.play()
            
        self.ultimo_feedback_letra = (letra, letra_correcta)
        self.tiempo_feedback_fin = time.time() + self.duracion_feedback
        
    def verificar_estado(self):
        if self.juego_terminado:
            return "GANADO" if "_" not in self.palabra_oculta else "PERDIDO" 
        
        if "_" not in self.palabra_oculta:
            self.juego_terminado = True
            self.puntuacion += 100 + (self.max_errores - self.errores) * 10
            self.progreso_galeria[self.palabra_actual] = True
            self.tiempo_fin_partida = time.time()
            return "GANADO"
        elif self.errores >= self.max_errores:
            self.juego_terminado = True
            self.tiempo_fin_partida = time.time()
            self.estado_juego = ESTADO_FINAL
            return "PERDIDO"
        return "JUGANDO"
    
    def activar_vibracion(self):
        self.efecto_vibracion_activo = True
        self.tiempo_vibracion_fin = time.time() + 0.2

    def obtener_posicion_vibracion(self):
        if self.efecto_vibracion_activo and time.time() < self.tiempo_vibracion_fin:
            return random.randint(-5, 5), random.randint(-5, 5)
        else:
            self.efecto_vibracion_activo = False
            return 0, 0