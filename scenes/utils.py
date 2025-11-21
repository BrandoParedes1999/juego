import pygame
import sys
import os
import math

# --- Colores ---
COLOR_FONDO = (245, 249, 250)
COLOR_PRINCIPAL = (3, 57, 108)
COLOR_ACENTO_PRIMARIO = (255, 165, 0)
COLOR_ACENTO_SECUNDARIO = (100, 149, 237)
COLOR_ERROR = (255, 70, 70)
COLOR_ACIERTO = (60, 179, 113)
COLOR_FONDO_CLARO = (255, 255, 255)
COLOR_PELIGRO = (255, 215, 0)
COLOR_BORDE_GLOW = (255, 100, 100, 150)
COLOR_GRIS_CLARO = (180, 180, 180)
COLOR_GRIS_OSCURO = (100, 100, 100)

# --- Configuración de Pantalla ---
ANCHO_PANTALLA = 800
ALTO_PANTALLA = 600
TIEMPO_TRANSICION_FADE = 0.3 # Duración del fade en segundos

# --- Estados del juego ---
ESTADO_MENU = 0
ESTADO_INTRO = 1 
ESTADO_JUGANDO = 2
ESTADO_FINAL = 3
ESTADO_TOP_SCORES = 4 
ESTADO_COMPLETADO = 5
ESTADO_CONFIGURACION = 6 
ESTADO_SELECCION_ESCENARIO = 7 
ESTADO_PAUSA = 8 
ESTADO_GALERIA = 9 # ¡NUEVO ESTADO!

# --- Función para obtener la ruta absoluta de los recursos ---
def resource_path(relative_path):
    """Obtiene la ruta absoluta para PyInstaller o entorno de desarrollo."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- Carga de Fuentes ---
def cargar_fuentes():
    try:
        FUENTE_TITULO = pygame.font.Font(resource_path("assets/Montserrat-Regular.ttf"), 60)
        FUENTE_PALABRA = pygame.font.Font(resource_path("assets/Montserrat-Regular.ttf"), 64)
        FUENTE_MEDIANA = pygame.font.Font(resource_path("assets/Montserrat-Regular.ttf"), 32)
        FUENTE_TEXTO_UI = pygame.font.Font(resource_path("assets/Montserrat-Regular.ttf"), 20)
        FUENTE_PEQUEÑA = pygame.font.Font(resource_path("assets/Montserrat-Regular.ttf"), 16)
        FUENTE_DATO = pygame.font.Font(None, 20)
    except:
        FUENTE_TITULO = pygame.font.Font(None, 60)
        FUENTE_PALABRA = pygame.font.Font(None, 64)
        FUENTE_MEDIANA = pygame.font.Font(None, 32)
        FUENTE_TEXTO_UI = pygame.font.Font(None, 20)
        FUENTE_PEQUEÑA = pygame.font.Font(None, 16)
        FUENTE_DATO = pygame.font.Font(None, 20)
    return FUENTE_TITULO, FUENTE_PALABRA, FUENTE_MEDIANA, FUENTE_TEXTO_UI, FUENTE_PEQUEÑA, FUENTE_DATO

# --- Carga de Imágenes ---
def cargar_imagenes_barco(max_errores):
    imagenes = []
    for i in range(max_errores + 1): 
        try:
            ruta = resource_path(f"assets/barco_{i}.png")
            imagen = pygame.image.load(ruta).convert_alpha()
            imagen_pequena = pygame.transform.scale(imagen, (200, 200)) 
            imagenes.append(imagen_pequena)
        except:
            print(f"Advertencia: No se encontró la imagen barco_{i}.png")
            pass
    return imagenes

IMAGEN_CORAZON_GLOBAL = None
def cargar_imagen_corazon():
    global IMAGEN_CORAZON_GLOBAL
    try:
        ruta = resource_path("assets/corazon.png")
        imagen = pygame.image.load(ruta).convert_alpha()
        IMAGEN_CORAZON_GLOBAL = pygame.transform.scale(imagen, (30, 30))
    except:
        print("Advertencia: No se encontró la imagen de Corazón. Usando fallback.")
        IMAGEN_CORAZON_GLOBAL = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(IMAGEN_CORAZON_GLOBAL, COLOR_ERROR, (15, 15), 15)
    return IMAGEN_CORAZON_GLOBAL

# Inicializar y devolver la pantalla (sin pygame.init() aquí)
def inicializar_pantalla():
    PANTALLA = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
    pygame.display.set_caption("El Ahorcado Cultural")
    return PANTALLA

# --- NUEVO: Función de Transición Fade ---
def ejecutar_fade(surface, clock, color=(0, 0, 0), direccion="out"):
    """Crea un efecto de desvanecimiento a un color (out) o desde un color (in)."""
    
    superficie_fade = pygame.Surface((ANCHO_PANTALLA, ALTO_PANTALLA))
    superficie_fade.fill(color)
    
    start_alpha = 0 if direccion == "in" else 255
    end_alpha = 255 if direccion == "in" else 0
    
    frames = int(60 * TIEMPO_TRANSICION_FADE)
    step = (end_alpha - start_alpha) / frames
    
    # Capturar el estado visual actual ANTES de iniciar el loop de fade
    fondo_estatico = surface.copy()
    
    for i in range(frames + 1):
        alpha = int(start_alpha + step * i)
        
        surface.blit(fondo_estatico, (0, 0)) # Dibujar la escena estática
        
        superficie_fade.set_alpha(alpha)
        surface.blit(superficie_fade, (0, 0)) # Dibujar el fade overlay
        
        pygame.display.flip()
        clock.tick(60)