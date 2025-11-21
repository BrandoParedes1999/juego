import json
import os
import pygame
import random
from scenes.utils import resource_path

# --- Constantes Globales ---
MAX_TOP_SCORES = 5
TIEMPO_FLASH_FINAL = 1.5
TIEMPO_INTRO_MAX = 3.0

# --- SISTEMA DE ESCENARIOS ---
ESCENARIOS = {
    "carmen": {
        "nombre": "Ciudad del Carmen",
        "archivo_datos": "datos_juego.json",
        "archivo_progreso": "progreso_carmen.json",
        "descripcion": "Descubre la historia pirata y petrolera de Carmen"
    },
    "campeche": {
        "nombre": "San Francisco de Campeche",
        "archivo_datos": "datos_campeche.json",
        "archivo_progreso": "progreso_campeche.json",
        "descripcion": "Explora las murallas y fortificaciones coloniales"
    },
    "merida": {
        "nombre": "Mérida, Yucatán",
        "archivo_datos": "datos_merida.json",
        "archivo_progreso": "progreso_merida.json",
        "descripcion": "Sumérgete en la cultura maya y henequenera"
    }
}

# --- CONFIGURACIÓN DE DIFICULTAD ---
DIFICULTADES = {
    "facil": {
        "tiempo": 45,
        "max_errores": 4,
        "penalizacion": 3,
        "bono": 15,
        "nombre": "Fácil"
    },
    "normal": {
        "tiempo": 30,
        "max_errores": 3,
        "penalizacion": 5,
        "bono": 10,
        "nombre": "Normal"
    },
    "dificil": {
        "tiempo": 20,
        "max_errores": 2,
        "penalizacion": 7,
        "bono": 20,
        "nombre": "Difícil"
    }
}

# --- Clase de Configuración ---
class Configuracion:
    def __init__(self):
        self.ruta_config = 'config.json'
        self.volumen_musica = 0.25
        self.volumen_sfx = 0.7
        self.escenario_actual = "carmen"
        self.dificultad = "normal"
        self.pantalla_completa = False
        self.cargar()
    
    def cargar(self):
        if os.path.exists(self.ruta_config):
            try:
                with open(self.ruta_config, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.volumen_musica = data.get('volumen_musica', 0.25)
                    self.volumen_sfx = data.get('volumen_sfx', 0.7)
                    self.escenario_actual = data.get('escenario_actual', 'carmen')
                    self.dificultad = data.get('dificultad', 'normal')
                    self.pantalla_completa = data.get('pantalla_completa', False)
            except:
                self.guardar()
        else:
            self.guardar()

    # ... (El resto de funciones de guardar y datos sigue igual)
    def guardar(self):
        data = {
            'volumen_musica': self.volumen_musica,
            'volumen_sfx': self.volumen_sfx,
            'escenario_actual': self.escenario_actual,
            'dificultad': self.dificultad,
            'pantalla_completa': self.pantalla_completa
        }
        with open(self.ruta_config, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

def cargar_datos_juego(escenario_id):
    archivo = ESCENARIOS.get(escenario_id, ESCENARIOS['carmen'])["archivo_datos"]
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de datos '{archivo}'.")
        return {}

def cargar_progreso(escenario_id, palabras_datos):
    archivo = ESCENARIOS[escenario_id]["archivo_progreso"]
    default_progress = {palabra: False for palabra in palabras_datos.keys()}
    default_scores = []
    
    if os.path.exists(archivo):
        try:
            with open(archivo, 'r') as f:
                data = json.load(f)
                progress = {**default_progress, **data.get('progress', {})}
                return data.get('scores', default_scores), progress
        except:
            pass
    
    return default_scores, default_progress

def guardar_progreso(scores, progress, escenario_id):
    archivo = ESCENARIOS[escenario_id]["archivo_progreso"]
    data = {'scores': scores, 'progress': progress}
    with open(archivo, 'w') as f:
        json.dump(data, f)

def registrar_puntuacion(score, scores_list):
    scores_list.append(score)
    scores_list.sort(reverse=True)
    return scores_list[:MAX_TOP_SCORES]

# --- Inicialización de Audio ---
def cargar_audio(config):
    pygame.mixer.init()
    SFX_ACIERTO = None
    SFX_ERROR = None
    SFX_VICTORIA = None
    SFX_DERROTA = None
    RUTA_MUSICA_NORMAL = None
    RUTA_MUSICA_PELIGRO = None
    
    try:
        SFX_ACIERTO = pygame.mixer.Sound(resource_path("assets/sonidos/clic.wav"))
        SFX_ERROR = pygame.mixer.Sound(resource_path("assets/sonidos/error.wav"))
        SFX_VICTORIA = pygame.mixer.Sound(resource_path("assets/sonidos/victoria.wav"))
        SFX_DERROTA = pygame.mixer.Sound(resource_path("assets/sonidos/derrota.wav"))
        
        # Se asume que musica_fondo.wav o musica_fondo.mp3 existe.
        RUTA_MUSICA_NORMAL = resource_path("assets/sonidos/musica_fondo.mp3")
        RUTA_MUSICA_PELIGRO = resource_path("assets/sonidos/musica_peligro.wav")
        
        pygame.mixer.music.load(RUTA_MUSICA_NORMAL)
        pygame.mixer.music.set_volume(config.volumen_musica)
    except:
        print("Advertencia: Audio no disponible")
    
    return SFX_ACIERTO, SFX_ERROR, SFX_VICTORIA, SFX_DERROTA, RUTA_MUSICA_NORMAL, RUTA_MUSICA_PELIGRO