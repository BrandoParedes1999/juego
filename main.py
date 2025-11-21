import pygame
import sys
import os
import time

# 1. Inicializa Pygame antes de importar cualquier cosa que use fuentes.
pygame.init() 
pygame.mixer.init() 

# 2. Importaciones
from scenes.utils import *
from ui_elements import Slider, wrap_text
from config_manager import Configuracion, cargar_datos_juego, ESCENARIOS, DIFICULTADES
from game_state import JuegoAhorcado, inicializar_audio_global, SFX_VICTORIA, SFX_DERROTA, RUTA_MUSICA_NORMAL
from scenes.play_scene import dibujar_interfaz, mostrar_contexto_adivinado
from scenes.final_scene import * # Incluye dibujar_galeria y dibujar_menu modificado


# --- 1. Inicialización Global y Carga de Configuración ---
PANTALLA = inicializar_pantalla() 
clock = pygame.time.Clock()

# Cargar configuración y datos
config = Configuracion()
PALABRAS_DATOS = cargar_datos_juego(config.escenario_actual)

# Inicializar audio
config = inicializar_audio_global(config)

# Crear instancia del juego
juego = JuegoAhorcado(PALABRAS_DATOS, config)
botones_menu_actuales = []
sliders_actuales = {}

scroll_y = 0  # <--- NUEVA VARIABLE: Posición vertical de desplazamiento
alto_contenido_galeria = ALTO_PANTALLA # Altura inicial del contenido

if RUTA_MUSICA_NORMAL:
    pygame.mixer.music.play(-1)

# --- 2. Bucle Principal (Game Loop) ---
while True:
    mouse_pos = pygame.mouse.get_pos()
    
    # Actualizar hover
    for boton in botones_menu_actuales:
        if hasattr(boton, 'verificar_hover'):
            boton.verificar_hover(mouse_pos)
    
    # --- Manejo de Eventos ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            config.guardar()
            pygame.quit()
            sys.exit()
            
        # --- NUEVO: Manejo de la Rueda del Mouse para la Galería ---
        if juego.estado_juego == ESTADO_GALERIA:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4: # Rueda hacia arriba
                    scroll_y = min(scroll_y + 40, 0) # Límite superior: scroll_y no puede ser positivo
                elif event.button == 5: # Rueda hacia abajo
                    scroll_y -= 40
        # Aplicar límite inferior al scroll
            limite_scroll = -(alto_contenido_galeria - ALTO_PANTALLA + 50) # +50 para margen inferior
            if alto_contenido_galeria > ALTO_PANTALLA:
                scroll_y = max(scroll_y, limite_scroll)
            else:
                scroll_y = 0 # Si el contenido cabe, no hay scroll
        
        if juego.estado_juego == ESTADO_CONFIGURACION:
            for slider in sliders_actuales.values():
                slider.manejar_evento(event)
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if juego.estado_juego == ESTADO_JUGANDO: juego.estado_juego = ESTADO_PAUSA
            elif juego.estado_juego == ESTADO_PAUSA: juego.estado_juego = ESTADO_JUGANDO
        
        # Eventos de JUGANDO
        if juego.estado_juego == ESTADO_JUGANDO:
            if event.type == pygame.KEYDOWN and event.unicode.isalpha():
                juego.verificar_letra(event.unicode.upper())
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for letra, rect in juego.botones_teclado.items():
                    if rect.collidepoint(event.pos):
                        juego.verificar_letra(letra)
        
        # Eventos de Menú y Pantallas Estáticas
        elif juego.estado_juego in [ESTADO_MENU, ESTADO_TOP_SCORES, ESTADO_COMPLETADO, ESTADO_CONFIGURACION, ESTADO_SELECCION_ESCENARIO, ESTADO_PAUSA, ESTADO_GALERIA]:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for boton in botones_menu_actuales:
                    if hasattr(boton, 'verificar_clic') and boton.verificar_clic(event.pos):
                        
                        # Transiciones con Fade OUT al salir del menú
                        if boton.accion in ["INICIAR", "TOP_SCORES", "CONFIG", "ESCENARIOS", "GALERIA"]:
                            ejecutar_fade(PANTALLA, clock, direccion="out")
                        
                        if boton.accion == "INICIAR":
                            juego.puntuacion = 0
                            juego.palabras_pendientes = juego._obtener_palabras_pendientes()
                            juego.reiniciar_ronda()
                            if juego.estado_juego != ESTADO_COMPLETADO: juego.estado_juego = ESTADO_INTRO; juego.tiempo_inicio_intro = 0
                        
                        elif boton.accion == "TOP_SCORES": juego.estado_juego = ESTADO_TOP_SCORES
                        elif boton.accion == "MENU": juego.estado_juego = ESTADO_MENU
                        elif boton.accion == "CONFIG":
                            juego.estado_juego = ESTADO_CONFIGURACION
                            sliders_actuales = {
                                'musica': Slider(350, 135, 250, 10, config.volumen_musica, 0.0, 1.0),
                                'sfx': Slider(350, 235, 250, 10, config.volumen_sfx, 0.0, 1.0)
                            }
                        elif boton.accion == "ESCENARIOS": juego.estado_juego = ESTADO_SELECCION_ESCENARIO
                        elif boton.accion == "GALERIA": 
                            ejecutar_fade(PANTALLA, clock, direccion="out")
                            juego.estado_juego = ESTADO_GALERIA
                            scroll_y = 0 # Resetear scroll al entrar
                        elif boton.accion.startswith("ESCENARIO_"):
                            nuevo_escenario = boton.accion.replace("ESCENARIO_", "")
                            if nuevo_escenario != config.escenario_actual:
                                config.escenario_actual = nuevo_escenario; config.guardar()
                                juego = JuegoAhorcado(cargar_datos_juego(config.escenario_actual), config)
                            juego.estado_juego = ESTADO_MENU
                        elif boton.accion == "GUARDAR":
                            config.volumen_musica = sliders_actuales['musica'].valor; config.volumen_sfx = sliders_actuales['sfx'].valor
                            config.guardar(); pygame.mixer.music.set_volume(config.volumen_musica)
                            juego = JuegoAhorcado(PALABRAS_DATOS, config)
                            juego.estado_juego = ESTADO_MENU
                        elif boton.accion == "CAMBIAR_DIF":
                            dificultades = list(DIFICULTADES.keys()); idx_actual = dificultades.index(config.dificultad)
                            config.dificultad = dificultades[(idx_actual + 1) % len(dificultades)]
                        elif boton.accion == "CONTINUAR": juego.estado_juego = ESTADO_JUGANDO

            if juego.estado_juego in [ESTADO_FINAL, ESTADO_COMPLETADO]:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    if juego.estado_juego == ESTADO_COMPLETADO:
                        juego.progreso_galeria = {p: False for p in juego.palabras_datos.keys()}
                        guardar_progreso(juego.top_scores, juego.progreso_galeria, juego.config.escenario_actual)
                    juego.estado_juego = ESTADO_MENU
                    if RUTA_MUSICA_NORMAL and not pygame.mixer.music.get_busy():
                        pygame.mixer.music.load(RUTA_MUSICA_NORMAL); pygame.mixer.music.set_volume(juego.config.volumen_musica); pygame.mixer.music.play(-1)
    
    # --- LÓGICA DE DIBUJO ---
    if juego.estado_juego == ESTADO_MENU: botones_menu_actuales = dibujar_menu(juego, PANTALLA)
    elif juego.estado_juego == ESTADO_INTRO: dibujar_introduccion(juego, PANTALLA)
    elif juego.estado_juego == ESTADO_TOP_SCORES: botones_menu_actuales = dibujar_top_scores(juego, PANTALLA)
    elif juego.estado_juego == ESTADO_COMPLETADO: dibujar_completado(juego, PANTALLA)
    elif juego.estado_juego == ESTADO_CONFIGURACION: botones_menu_actuales = dibujar_configuracion(juego, PANTALLA, sliders_actuales)
    elif juego.estado_juego == ESTADO_SELECCION_ESCENARIO: botones_menu_actuales = dibujar_seleccion_escenario(juego, PANTALLA)
    elif juego.estado_juego == ESTADO_PAUSA: botones_menu_actuales = dibujar_pausa(juego, PANTALLA)
    elif juego.estado_juego == ESTADO_GALERIA:
        # Llamar a la función con el scroll_y y capturar la altura total
        botones_menu_actuales, alto_contenido_galeria = dibujar_galeria(juego, PANTALLA, scroll_y) # <--- ACTUALIZADO
    
    elif juego.estado_juego == ESTADO_JUGANDO:
        juego.actualizar_tiempo()
        dibujar_interfaz(juego, PANTALLA)
        estado = juego.verificar_estado()
        
        if estado == "GANADO":
            if pygame.mixer.music.get_busy(): pygame.mixer.music.stop()
            if SFX_VICTORIA: SFX_VICTORIA.set_volume(config.volumen_sfx); SFX_VICTORIA.play()
            
            mostrar_contexto_adivinado(juego, clock, PANTALLA)
            
            if juego.estado_juego == ESTADO_COMPLETADO:
                juego.estado_juego = ESTADO_FINAL
                pantalla_final(juego, PANTALLA, f"¡GANASTE! Puntos: {juego.puntuacion}")
        
        elif estado == "PERDIDO":
            if pygame.mixer.music.get_busy(): pygame.mixer.music.stop()
            if SFX_DERROTA: SFX_DERROTA.set_volume(config.volumen_sfx); SFX_DERROTA.play()
            juego.estado_juego = ESTADO_FINAL
            pantalla_final(juego, PANTALLA, f"¡PERDISTE! Racha: {juego.puntuacion // 100}")
    
    # --- Manejo de FADE IN al volver a Menú/Juego ---
    if juego.estado_juego in [ESTADO_MENU, ESTADO_JUGANDO] and juego.tiempo_fin_partida != 0:
        ejecutar_fade(PANTALLA, clock, direccion="in")
        juego.tiempo_fin_partida = 0 

    if juego.estado_juego == ESTADO_FINAL:
        pygame.display.flip()
    elif juego.estado_juego != ESTADO_FINAL:
        pygame.display.flip()
        
    clock.tick(60)