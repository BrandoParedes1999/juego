import pygame
import time
import math
import sys
from scenes.utils import *
from ui_elements import Boton, wrap_text
from game_state import SFX_VICTORIA, RUTA_MUSICA_NORMAL, IMAGEN_CORAZON_GLOBAL # Importar IMAGEN_CORAZON_GLOBAL
from config_manager import TIEMPO_FLASH_FINAL

# Carga las fuentes una vez
FUENTES = cargar_fuentes()
FUENTE_PALABRA, FUENTE_MEDIANA, FUENTE_TEXTO_UI, FUENTE_PEQUEÑA, FUENTE_DATO = FUENTES[1], FUENTES[2], FUENTES[3], FUENTES[4], FUENTES[5]

# --- Dibujo del Teclado (Sin Cambios) ---
def dibujar_teclado(juego, surface):
    pos_x = ANCHO_PANTALLA / 2 - 270
    pos_y = 500
    espacio = 45 
    tamano_letra = 25 
    
    tiempo_actual = time.time()
    parpadeo_activo = juego.tiempo_fin_partida != 0 and (tiempo_actual < juego.tiempo_fin_partida + TIEMPO_FLASH_FINAL)
    es_parpadeo_visible = math.floor(tiempo_actual * 6) % 2 == 0
    estado_final = juego.verificar_estado() 
    juego.botones_teclado = {}

    for i, letra in enumerate(juego.teclado_letras):
        color_texto = COLOR_PRINCIPAL
        color_fondo_btn = COLOR_FONDO_CLARO
        grosor_borde = 1
        
        letra_en_palabra = letra in juego.palabra_actual
        letra_adivinada = letra in juego.letras_adivinadas

        if parpadeo_activo:
            if estado_final == "GANADO":
                if letra_adivinada and es_parpadeo_visible:
                    color_fondo_btn = COLOR_ACIERTO
                    color_texto = COLOR_FONDO
            else:
                if letra_en_palabra and not letra_adivinada and es_parpadeo_visible:
                    color_fondo_btn = COLOR_ERROR
                    color_texto = COLOR_FONDO
        else:
            if letra in juego.letras_correctas:
                color_fondo_btn = COLOR_ACIERTO
                color_texto = COLOR_FONDO 
                grosor_borde = 0
            elif letra in juego.letras_incorrectas:
                color_fondo_btn = COLOR_ERROR
                color_texto = COLOR_FONDO
                grosor_borde = 0
            
            if tiempo_actual < juego.tiempo_feedback_fin and juego.ultimo_feedback_letra and juego.ultimo_feedback_letra[0] == letra:
                color_fondo_btn = COLOR_ACIERTO if juego.ultimo_feedback_letra[1] else COLOR_ERROR
                color_texto = COLOR_FONDO
                grosor_borde = 0
        
        x = pos_x + (i % 13) * espacio
        y = pos_y + (i // 13) * espacio
        
        rect_btn = pygame.Rect(0, 0, tamano_letra * 1.5, tamano_letra * 1.5)
        rect_btn.center = (x, y)
        pygame.draw.rect(surface, color_fondo_btn, rect_btn, 0, 8) 
        
        if grosor_borde > 0 and color_fondo_btn == COLOR_FONDO_CLARO:
            pygame.draw.rect(surface, COLOR_ACENTO_SECUNDARIO, rect_btn, grosor_borde, 8) 
        
        texto = FUENTE_TEXTO_UI.render(letra, True, color_texto)
        letra_rect = texto.get_rect(center=(x, y))
        surface.blit(texto, letra_rect)
        juego.botones_teclado[letra] = rect_btn


# --- Dibujo de la Carta de la Palabra (Sin Cambios) ---
def dibujar_carta_palabra(juego, surface):
    ancho_carta_base = 300
    alto_carta = 350
    pos_carta_x = 50
    pos_carta_y = 50
    
    offset_x, offset_y = juego.obtener_posicion_vibracion()
    pos_carta_x += offset_x
    pos_carta_y += offset_y
    
    s = pygame.Surface((ancho_carta_base, alto_carta), pygame.SRCALPHA)
    s.fill(COLOR_FONDO_CLARO) 
    pygame.draw.rect(s, COLOR_PRINCIPAL, s.get_rect(), 2, border_radius=15) 

    try:
        imagen_ruta = juego.palabras_datos[juego.palabra_actual]['imagen']
        if not imagen_ruta: raise FileNotFoundError 
        imagen_palabra = pygame.image.load(resource_path(imagen_ruta)).convert_alpha()
        
        ancho_orig, alto_orig = imagen_palabra.get_size()
        max_ancho, max_alto = 280, 250 
        escala = min(max_ancho / ancho_orig, max_alto / alto_orig)
        nuevo_ancho = int(ancho_orig * escala)
        nuevo_alto = int(alto_orig * escala)
        
        imagen_palabra_pequena = pygame.transform.scale(imagen_palabra, (nuevo_ancho, nuevo_alto))
        imagen_palabra_rect = imagen_palabra_pequena.get_rect(center=(ancho_carta_base / 2, alto_carta / 2 - 30))
        s.blit(imagen_palabra_pequena, imagen_palabra_rect)
        
    except:
        texto_error = FUENTE_TEXTO_UI.render("Imagen no disponible", True, COLOR_ACENTO_SECUNDARIO)
        s.blit(texto_error, texto_error.get_rect(center=(ancho_carta_base / 2, alto_carta / 2 - 30)))
    
    pygame.draw.line(s, COLOR_ACENTO_SECUNDARIO, (10, alto_carta - 80), (ancho_carta_base - 10, alto_carta - 80), 1)
    texto_pista = FUENTE_TEXTO_UI.render("PISTA CULTURAL", True, COLOR_ACENTO_PRIMARIO)
    texto_pista_rect = texto_pista.get_rect(center=(ancho_carta_base / 2, alto_carta - 40))
    s.blit(texto_pista, texto_pista_rect)
    surface.blit(s, s.get_rect(x=pos_carta_x, y=pos_carta_y))


# --- Función Principal de Dibujo de Interfaz (ACTUALIZADA) ---
def dibujar_interfaz(juego, surface):
    surface.fill(COLOR_FONDO)
    
    offset_x, offset_y = juego.obtener_posicion_vibracion()
    
    # ... (código de borde peligro)
    if juego.borde_peligro_activo:
        tiempo_actual = time.time()
        if math.floor(tiempo_actual * 2) % 2 == 0: 
            glow_surf = pygame.Surface((ANCHO_PANTALLA, ALTO_PANTALLA), pygame.SRCALPHA)
            glow_surf.fill(COLOR_BORDE_GLOW)
            surface.blit(glow_surf, (0, 0))
    
    dibujar_carta_palabra(juego, surface)
    
    # --- DIBUJO DE VIDAS VISUALES (CORAZONES) ---
    for i in range(juego.max_errores):
        pos_x_corazon = ANCHO_PANTALLA - 50 - ((juego.max_errores - 1 - i) * 40) 
        
        if i < juego.max_errores - juego.errores:
            surface.blit(IMAGEN_CORAZON_GLOBAL, (pos_x_corazon, 50))
        else:
            # Corazón vacío (Vida perdida)
            pygame.draw.rect(surface, COLOR_GRIS_OSCURO, (pos_x_corazon, 50, 30, 30), 1)
    
    texto_palabra = FUENTE_PALABRA.render(" ".join(juego.palabra_oculta), True, COLOR_PRINCIPAL)
    texto_rect = texto_palabra.get_rect(center=(ANCHO_PANTALLA / 2, 400))
    surface.blit(texto_palabra, texto_rect)
    
    # DIBUJO DEL BARCO
    tiempo_flotacion = time.time()
    offset_flotacion_y = math.sin(tiempo_flotacion * 2.5) * 5
    
    if 0 <= juego.errores < len(juego.IMAGENES_BARCO):
        imagen_actual = juego.IMAGENES_BARCO[juego.errores]
        rect = imagen_actual.get_rect(center=(ANCHO_PANTALLA - 150 + offset_x, 280 + offset_y + offset_flotacion_y))
        surface.blit(imagen_actual, rect)

    color_tiempo = COLOR_ACIERTO
    if juego.tiempo_restante <= 20: color_tiempo = COLOR_PELIGRO
    if juego.tiempo_restante <= 10: color_tiempo = COLOR_ERROR

    texto_tiempo = FUENTE_MEDIANA.render(f"{juego.tiempo_restante}s", True, color_tiempo)
    surface.blit(texto_tiempo, (ANCHO_PANTALLA - 300, 20))
    
    texto_puntuacion = FUENTE_TEXTO_UI.render(f"PUNTOS: {juego.puntuacion}", True, COLOR_PRINCIPAL)
    surface.blit(texto_puntuacion, (ANCHO_PANTALLA - 150, 20))
    
    if juego.racha_actual > 0:
        texto_racha = FUENTE_TEXTO_UI.render(f"RACHA: x{juego.racha_actual}", True, COLOR_ACENTO_PRIMARIO)
        surface.blit(texto_racha, (ANCHO_PANTALLA - 150, 40))
    
    texto_pausa = FUENTE_PEQUEÑA.render("[ESC] Pausar", True, COLOR_GRIS_CLARO)
    surface.blit(texto_pausa, (10, 10))

    dibujar_teclado(juego, surface)


# --- Función para mostrar el Dato Cultural (Sin Cambios) ---
def mostrar_contexto_adivinado(juego, clock, surface):
    if juego.palabra_actual not in juego.palabras_datos:
        pygame.time.wait(1000)
        juego.recompensar_tiempo(juego.tiempo_bono)
        juego.reiniciar_ronda()
        juego.estado_juego = ESTADO_JUGANDO
        return
        
    info_palabra = juego.palabras_datos[juego.palabra_actual]
    dato_curioso = info_palabra['dato']
    juego.estado_juego = ESTADO_FINAL

    ancho_base = 300
    alto_carta = 350
    pos_carta_x = 50
    pos_carta_y = 50
    
    pygame.time.wait(1000)

    reverso_s = pygame.Surface((ancho_base, alto_carta), pygame.SRCALPHA)
    reverso_s.fill(COLOR_FONDO_CLARO)
    pygame.draw.rect(reverso_s, COLOR_PRINCIPAL, reverso_s.get_rect(), 2, border_radius=15)
    
    titulo_contexto = FUENTE_MEDIANA.render("DATO CULTURAL", True, COLOR_ACENTO_PRIMARIO)
    reverso_s.blit(titulo_contexto, titulo_contexto.get_rect(centerx=reverso_s.get_width()/2, y=20))
    
    area_texto_ajustado = pygame.Rect(10, 80, ancho_base - 20, alto_carta - 100)
    wrap_text(reverso_s, dato_curioso, FUENTE_DATO, COLOR_PRINCIPAL, area_texto_ajustado, align="center")
    
    dibujar_interfaz(juego, surface)
    fondo_estatico = surface.copy()
    
    transicion_pasos = 20
    for alpha in range(0, 255 + 1, 255 // transicion_pasos):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        surface.blit(fondo_estatico, (0, 0))
        reverso_transparente = reverso_s.copy()
        reverso_transparente.set_alpha(alpha)
        surface.blit(reverso_transparente, (pos_carta_x, pos_carta_y))
        pygame.display.flip()
        clock.tick(60)
        
    tiempo_inicio_contexto = time.time()
    duracion_contexto = 3.0

    while time.time() < tiempo_inicio_contexto + duracion_contexto:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        surface.blit(fondo_estatico, (0, 0))
        surface.blit(reverso_s, (pos_carta_x, pos_carta_y))
        pygame.display.flip()
        clock.tick(60)

    juego.recompensar_tiempo(juego.tiempo_bono)
    juego.reiniciar_ronda()
    juego.estado_juego = ESTADO_JUGANDO
    
    if RUTA_MUSICA_NORMAL and not pygame.mixer.music.get_busy():
        pygame.mixer.music.load(RUTA_MUSICA_NORMAL)
        pygame.mixer.music.set_volume(juego.config.volumen_musica)
        pygame.mixer.music.play(-1)