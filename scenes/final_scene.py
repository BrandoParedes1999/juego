import pygame
import sys
import time
from scenes.utils import *
from ui_elements import Boton, Slider, wrap_text
from config_manager import ESCENARIOS, DIFICULTADES, registrar_puntuacion, guardar_progreso, TIEMPO_INTRO_MAX
from game_state import SFX_DERROTA, SFX_VICTORIA, RUTA_MUSICA_NORMAL


# Carga las fuentes
FUENTES = cargar_fuentes()
FUENTE_TITULO, FUENTE_MEDIANA, FUENTE_TEXTO_UI, FUENTE_PEQUEÑA = FUENTES[0], FUENTES[2], FUENTES[3], FUENTES[4]
IMAGEN_FONDO_FINAL = None
try:
    IMAGEN_FONDO_FINAL = pygame.image.load(resource_path("assets/fondo_final.png")).convert()
    IMAGEN_FONDO_FINAL = pygame.transform.scale(IMAGEN_FONDO_FINAL, (ANCHO_PANTALLA, ALTO_PANTALLA))
except:
    pass

# --- Intro y Pausa ---
def dibujar_introduccion(juego, surface):
    surface.fill(COLOR_FONDO)
    
    if juego.tiempo_inicio_intro == 0:
        juego.tiempo_inicio_intro = time.time()

    tiempo_transcurrido = time.time() - juego.tiempo_inicio_intro
    
    if tiempo_transcurrido >= TIEMPO_INTRO_MAX:
        # La función main.py debe llamar a ejecutar_fade(direccion="out") antes de cambiar el estado
        juego.estado_juego = ESTADO_JUGANDO
        juego.tiempo_inicio_intro = 0
        return
    
    titulo = FUENTE_TITULO.render("¡LISTO PARA NAVEGAR!", True, COLOR_PRINCIPAL)
    escenario_nombre = ESCENARIOS[juego.config.escenario_actual]["nombre"]
    mensaje1 = FUENTE_MEDIANA.render(f"Descubre: {escenario_nombre}", True, COLOR_ACENTO_PRIMARIO)
    mensaje2 = FUENTE_TEXTO_UI.render(f"Iniciando en {int(TIEMPO_INTRO_MAX - tiempo_transcurrido) + 1}...", True, COLOR_PRINCIPAL)
    mensaje3 = FUENTE_MEDIANA.render("Presiona ESPACIO para saltar...", True, COLOR_ACENTO_SECUNDARIO)
    
    surface.blit(titulo, titulo.get_rect(center=(ANCHO_PANTALLA / 2, ALTO_PANTALLA / 2 - 100)))
    surface.blit(mensaje1, mensaje1.get_rect(center=(ANCHO_PANTALLA / 2, ALTO_PANTALLA / 2)))
    surface.blit(mensaje2, mensaje2.get_rect(center=(ANCHO_PANTALLA / 2, ALTO_PANTALLA / 2 + 50)))
    
    pygame.draw.rect(surface, COLOR_FONDO_CLARO, (ANCHO_PANTALLA/2 - 200, ALTO_PANTALLA - 100, 400, 50), border_radius=5)
    surface.blit(mensaje3, mensaje3.get_rect(center=(ANCHO_PANTALLA / 2, ALTO_PANTALLA - 75)))

def dibujar_pausa(juego, surface):
    overlay = pygame.Surface((ANCHO_PANTALLA, ALTO_PANTALLA), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))
    
    titulo = FUENTE_TITULO.render("PAUSA", True, COLOR_FONDO_CLARO)
    surface.blit(titulo, titulo.get_rect(center=(ANCHO_PANTALLA / 2, ALTO_PANTALLA / 2 - 100)))
    
    botones = []
    
    btn_continuar = Boton((ANCHO_PANTALLA / 2 - 150, ALTO_PANTALLA / 2 - 20, 300, 60),
                          "CONTINUAR", "CONTINUAR", COLOR_ACIERTO, COLOR_FONDO_CLARO)
    btn_continuar.dibujar(surface)
    botones.append(btn_continuar)
    
    btn_menu = Boton((ANCHO_PANTALLA / 2 - 150, ALTO_PANTALLA / 2 + 60, 300, 60),
                     "SALIR AL MENÚ", "MENU", COLOR_ERROR, COLOR_FONDO_CLARO)
    btn_menu.dibujar(surface)
    botones.append(btn_menu)
    
    texto_esc = FUENTE_PEQUEÑA.render("[ESC] para continuar", True, COLOR_GRIS_CLARO)
    surface.blit(texto_esc, texto_esc.get_rect(center=(ANCHO_PANTALLA / 2, ALTO_PANTALLA - 50)))
    return botones

# --- Menú Principal (Modificado para incluir GALERÍA) ---
def dibujar_menu(juego, surface):
    surface.fill(COLOR_FONDO)
    
    titulo = FUENTE_TITULO.render("AHORCADO CULTURAL", True, COLOR_PRINCIPAL)
    escenario_nombre = ESCENARIOS[juego.config.escenario_actual]["nombre"]
    subtitulo = FUENTE_MEDIANA.render(escenario_nombre, True, COLOR_ACENTO_PRIMARIO)
    
    surface.blit(titulo, titulo.get_rect(center=(ANCHO_PANTALLA / 2, ALTO_PANTALLA / 2 - 150)))
    surface.blit(subtitulo, subtitulo.get_rect(center=(ANCHO_PANTALLA / 2, ALTO_PANTALLA / 2 - 90)))
    
    high_score = juego.top_scores[0] if juego.top_scores else 0
    texto_high_score = FUENTE_TEXTO_UI.render(f"MEJOR PUNTAJE: {high_score}", True, COLOR_GRIS_CLARO)
    surface.blit(texto_high_score, texto_high_score.get_rect(center=(ANCHO_PANTALLA / 2, ALTO_PANTALLA / 2 - 40)))

    botones_menu = []
    
    btn_iniciar = Boton((ANCHO_PANTALLA / 2 - 150, ALTO_PANTALLA / 2 + 10, 300, 50), 
                        "INICIAR JUEGO", "INICIAR", COLOR_ACIERTO, COLOR_FONDO_CLARO)
    btn_iniciar.dibujar(surface)
    botones_menu.append(btn_iniciar)
    
    btn_escenarios = Boton((ANCHO_PANTALLA / 2 - 150, ALTO_PANTALLA / 2 + 70, 300, 50),
                           "CAMBIAR ESCENARIO", "ESCENARIOS", COLOR_ACENTO_PRIMARIO, COLOR_FONDO_CLARO)
    btn_escenarios.dibujar(surface)
    botones_menu.append(btn_escenarios)
    
    btn_config = Boton((ANCHO_PANTALLA / 2 - 150, ALTO_PANTALLA / 2 + 130, 300, 50),
                       "CONFIGURACIÓN", "CONFIG", COLOR_GRIS_OSCURO, COLOR_FONDO_CLARO)
    btn_config.dibujar(surface)
    botones_menu.append(btn_config)
    
    btn_scores = Boton((ANCHO_PANTALLA / 2 - 150, ALTO_PANTALLA / 2 + 190, 300, 50),
                       "MEJORES PUNTUACIONES", "TOP_SCORES", COLOR_GRIS_OSCURO, COLOR_FONDO_CLARO)
    btn_scores.dibujar(surface)
    botones_menu.append(btn_scores)
    
    btn_galeria = Boton((ANCHO_PANTALLA / 2 - 150, ALTO_PANTALLA / 2 + 250, 300, 50),
                        "GALERÍA DE SECRETOS", "GALERIA", COLOR_ACENTO_SECUNDARIO, COLOR_FONDO_CLARO)
    btn_galeria.dibujar(surface)
    botones_menu.append(btn_galeria)
    
    return botones_menu

# --- NUEVA FUNCIÓN: GALERÍA DE COLECCIONABLES ---
def dibujar_galeria(juego, surface, scroll_y): # <--- AÑADIR scroll_y
    """Muestra la galería de palabras adivinadas y sus datos curiosos con scroll."""
    surface.fill(COLOR_FONDO)
    
    titulo = FUENTE_TITULO.render("GALERÍA DE SECRETOS", True, COLOR_PRINCIPAL)
    escenario_nombre = ESCENARIOS[juego.config.escenario_actual]["nombre"]
    subtitulo = FUENTE_MEDIANA.render(f"Escenario: {escenario_nombre}", True, COLOR_ACENTO_PRIMARIO)
    
    surface.blit(titulo, titulo.get_rect(center=(ANCHO_PANTALLA / 2, 60)))
    surface.blit(subtitulo, subtitulo.get_rect(center=(ANCHO_PANTALLA / 2, 110)))
    
    botones = []
    
    # Configuración de las tarjetas
    tarjetas_por_fila = 3
    tarjeta_ancho = 200
    tarjeta_alto = 150
    margen_x = 50
    margen_y = 150
    espacio_total_tarjetas = tarjetas_por_fila * tarjeta_ancho
    espacio_total_margen = margen_x * 2
    espacio_entre_tarjetas = (ANCHO_PANTALLA - espacio_total_tarjetas - espacio_total_margen) // (tarjetas_por_fila - 1)
    
    palabras_lista = list(juego.palabras_datos.keys())
    
    # Altura del contenido total (para calcular el límite de scroll)
    num_filas = math.ceil(len(palabras_lista) / tarjetas_por_fila)
    ALTO_CONTENIDO = margen_y + num_filas * (tarjeta_alto + 30)
    
    # --- Dibujar Tarjetas ---
    for i, palabra in enumerate(palabras_lista):
        adivinada = juego.progreso_galeria.get(palabra, False)
        
        fila = i // tarjetas_por_fila
        columna = i % tarjetas_por_fila
        
        x = margen_x + columna * (tarjeta_ancho + espacio_entre_tarjetas)
        
        # *** APLICAR SCROLL A LA POSICIÓN Y ***
        y = margen_y + fila * (tarjeta_alto + 30) + scroll_y # <--- CLAVE DEL SCROLL
        
        rect = pygame.Rect(x, y, tarjeta_ancho, tarjeta_alto)
        
        # Optimización: Solo dibujar tarjetas visibles (y > 150 (bajo el subtítulo) y y < ALTO_PANTALLA)
        if rect.bottom < 150 or rect.top > ALTO_PANTALLA:
            continue

        # Dibujo de la tarjeta
        color_fondo = COLOR_ACIERTO if adivinada else COLOR_GRIS_OSCURO
        pygame.draw.rect(surface, color_fondo, rect, border_radius=10)
        
        if adivinada:
            texto_palabra = FUENTE_MEDIANA.render(palabra, True, COLOR_FONDO_CLARO)
            surface.blit(texto_palabra, texto_palabra.get_rect(center=(rect.centerx, rect.top + 25)))
            
            dato_curioso = juego.palabras_datos[palabra]['dato']
            dato_abreviado = dato_curioso[:70] + '...' if len(dato_curioso) > 70 else dato_curioso
            
            texto_dato = FUENTE_PEQUEÑA.render(dato_abreviado, True, COLOR_FONDO_CLARO)
            surface.blit(texto_dato, texto_dato.get_rect(center=(rect.centerx, rect.centery + 30)))
            
        else:
            texto_bloqueado = FUENTE_MEDIANA.render("?", True, COLOR_FONDO_CLARO)
            texto_desc = FUENTE_PEQUEÑA.render("PALABRA BLOQUEADA", True, COLOR_FONDO_CLARO)
            surface.blit(texto_bloqueado, texto_bloqueado.get_rect(center=(rect.centerx, rect.centery - 10)))
            surface.blit(texto_desc, texto_desc.get_rect(center=(rect.centerx, rect.centery + 30)))
            
    # Botón Volver (posición fija en la parte superior)
    btn_volver = Boton((10, 10, 100, 40), "MENÚ", "MENU", COLOR_ERROR, COLOR_FONDO_CLARO)
    btn_volver.dibujar(surface)
    botones.append(btn_volver)
    
    return botones, ALTO_CONTENIDO # <--- Devolver la altura total del contenido


def pantalla_final(juego, surface, mensaje):
    score = juego.puntuacion
    juego.top_scores = registrar_puntuacion(score, juego.top_scores)
    guardar_progreso(juego.top_scores, juego.progreso_galeria, juego.config.escenario_actual)

    if IMAGEN_FONDO_FINAL:
        surface.blit(IMAGEN_FONDO_FINAL, (0, 0))
    else:
        surface.fill(COLOR_FONDO)
    
    color_mensaje = COLOR_ACIERTO if mensaje.startswith('¡GANASTE!') else COLOR_ERROR
    
    superficie_texto = pygame.Surface((ANCHO_PANTALLA, 250), pygame.SRCALPHA)
    superficie_texto.fill((255, 255, 255, 180))
    surface.blit(superficie_texto, (0, ALTO_PANTALLA/2 - 125))

    texto = FUENTE_TITULO.render(mensaje, True, color_mensaje)
    rect = texto.get_rect(center=(ANCHO_PANTALLA / 2, ALTO_PANTALLA / 2 - 50))
    surface.blit(texto, rect)
    
    texto_puntuacion = FUENTE_MEDIANA.render(f"Puntuación final: {score}", True, COLOR_PRINCIPAL)
    rect_puntuacion = texto_puntuacion.get_rect(center=(ANCHO_PANTALLA / 2, ALTO_PANTALLA / 2 + 20))
    surface.blit(texto_puntuacion, rect_puntuacion)
    
    texto_reiniciar = FUENTE_TEXTO_UI.render("Presiona ENTER para volver al MENÚ", True, COLOR_PRINCIPAL)
    rect_reiniciar = texto_reiniciar.get_rect(center=(ANCHO_PANTALLA / 2, ALTO_PANTALLA / 2 + 100))
    surface.blit(texto_reiniciar, rect_reiniciar)


def dibujar_top_scores(juego, surface):
    surface.fill(COLOR_FONDO)
    
    escenario_nombre = ESCENARIOS[juego.config.escenario_actual]["nombre"]
    titulo = FUENTE_TITULO.render("TOP 5 PUNTUACIONES", True, COLOR_PRINCIPAL)
    subtitulo = FUENTE_TEXTO_UI.render(escenario_nombre, True, COLOR_ACENTO_PRIMARIO)
    
    surface.blit(titulo, titulo.get_rect(center=(ANCHO_PANTALLA / 2, 60)))
    surface.blit(subtitulo, subtitulo.get_rect(center=(ANCHO_PANTALLA / 2, 100)))
    
    header_font = FUENTE_MEDIANA
    texto_rank = header_font.render("RANK", True, COLOR_ACENTO_PRIMARIO)
    texto_score = header_font.render("PUNTOS", True, COLOR_ACENTO_PRIMARIO)
    
    surface.blit(texto_rank, (ANCHO_PANTALLA / 2 - 200, 150))
    surface.blit(texto_score, (ANCHO_PANTALLA / 2 + 100, 150))
    
    pygame.draw.line(surface, COLOR_ACENTO_SECUNDARIO, (ANCHO_PANTALLA / 2 - 200, 190), 
                     (ANCHO_PANTALLA / 2 + 250, 190), 2)
    
    score_font = FUENTE_MEDIANA
    y_start = 220
    line_height = 50
    
    for i, score in enumerate(juego.top_scores):
        rank_color = COLOR_PRINCIPAL
        if i == 0: rank_color = COLOR_PELIGRO
        
        texto_rank_num = score_font.render(f"#{i + 1}", True, rank_color)
        texto_score_num = score_font.render(f"{score}", True, rank_color)
        
        surface.blit(texto_rank_num, (ANCHO_PANTALLA / 2 - 200, y_start + i * line_height))
        surface.blit(texto_score_num, (ANCHO_PANTALLA / 2 + 100, y_start + i * line_height))
    
    btn_regresar = Boton((10, 10, 100, 40), "MENÚ", "MENU", COLOR_ERROR, COLOR_FONDO_CLARO)
    btn_regresar.dibujar(surface)
    
    return [btn_regresar]

# ... (El resto de funciones: dibujar_configuracion, dibujar_seleccion_escenario, dibujar_pausa, etc.)
def dibujar_configuracion(juego, surface, sliders):
    surface.fill(COLOR_FONDO)
    
    titulo = FUENTE_TITULO.render("CONFIGURACIÓN", True, COLOR_PRINCIPAL)
    surface.blit(titulo, titulo.get_rect(center=(ANCHO_PANTALLA / 2, 60)))
    
    y_pos = 140
    espacio = 100
    
    texto_musica = FUENTE_MEDIANA.render("Volumen Música", True, COLOR_PRINCIPAL)
    surface.blit(texto_musica, (100, y_pos))
    valor_musica = FUENTE_TEXTO_UI.render(f"{int(juego.config.volumen_musica * 100)}%", True, COLOR_ACENTO_PRIMARIO)
    surface.blit(valor_musica, (650, y_pos + 5))
    sliders['musica'].dibujar(surface)
    
    y_pos += espacio
    texto_sfx = FUENTE_MEDIANA.render("Volumen Efectos", True, COLOR_PRINCIPAL)
    surface.blit(texto_sfx, (100, y_pos))
    valor_sfx = FUENTE_TEXTO_UI.render(f"{int(juego.config.volumen_sfx * 100)}%", True, COLOR_ACENTO_PRIMARIO)
    surface.blit(valor_sfx, (650, y_pos + 5))
    sliders['sfx'].dibujar(surface)
    
    y_pos += espacio
    texto_dif = FUENTE_MEDIANA.render("Dificultad", True, COLOR_PRINCIPAL)
    surface.blit(texto_dif, (100, y_pos))
    dif_actual = DIFICULTADES[juego.config.dificultad]["nombre"]
    valor_dif = FUENTE_TEXTO_UI.render(dif_actual, True, COLOR_ACENTO_PRIMARIO)
    surface.blit(valor_dif, (650, y_pos + 5))
    
    botones = []
    
    btn_dif = Boton((350, y_pos - 5, 250, 40), "Cambiar Dificultad", "CAMBIAR_DIF", 
                    COLOR_ACENTO_SECUNDARIO, COLOR_FONDO_CLARO)
    btn_dif.dibujar(surface)
    botones.append(btn_dif)
    
    btn_guardar = Boton((ANCHO_PANTALLA / 2 - 150, ALTO_PANTALLA - 120, 300, 60),
                        "GUARDAR Y VOLVER", "GUARDAR", COLOR_ACIERTO, COLOR_FONDO_CLARO)
    btn_guardar.dibujar(surface)
    botones.append(btn_guardar)
    
    texto_info = FUENTE_PEQUEÑA.render("Los cambios se aplicarán al guardar", True, COLOR_GRIS_CLARO)
    surface.blit(texto_info, texto_info.get_rect(center=(ANCHO_PANTALLA / 2, ALTO_PANTALLA - 50)))
    
    return botones

def dibujar_seleccion_escenario(juego, surface):
    surface.fill(COLOR_FONDO)
    
    titulo = FUENTE_TITULO.render("SELECCIONAR ESCENARIO", True, COLOR_PRINCIPAL)
    surface.blit(titulo, titulo.get_rect(center=(ANCHO_PANTALLA / 2, 60)))
    
    botones = []
    y_pos = 150
    
    for escenario_id, datos in ESCENARIOS.items():
        es_actual = (escenario_id == juego.config.escenario_actual)
        color = COLOR_ACIERTO if es_actual else COLOR_ACENTO_SECUNDARIO
        
        btn = Boton((ANCHO_PANTALLA / 2 - 250, y_pos, 500, 80),
                    "", f"ESCENARIO_{escenario_id}", color, COLOR_FONDO_CLARO)
        
        pygame.draw.rect(surface, color, btn.rect, border_radius=10)
        
        texto_nombre = FUENTE_MEDIANA.render(datos["nombre"], True, COLOR_FONDO_CLARO)
        surface.blit(texto_nombre, texto_nombre.get_rect(centerx=btn.rect.centerx, y=btn.rect.y + 10))
        
        texto_desc = FUENTE_PEQUEÑA.render(datos["descripcion"], True, COLOR_FONDO_CLARO)
        surface.blit(texto_desc, texto_desc.get_rect(centerx=btn.rect.centerx, y=btn.rect.y + 45))
        
        if es_actual:
            texto_actual = FUENTE_PEQUEÑA.render("★ ACTUAL ★", True, COLOR_PELIGRO)
            surface.blit(texto_actual, texto_actual.get_rect(centerx=btn.rect.centerx, y=btn.rect.y + 65))
        
        botones.append(btn)
        y_pos += 100
    
    btn_volver = Boton((10, 10, 100, 40), "VOLVER", "MENU", COLOR_ERROR, COLOR_FONDO_CLARO)
    btn_volver.dibujar(surface)
    botones.append(btn_volver)
    
    return botones

def dibujar_pausa(juego, surface):
    overlay = pygame.Surface((ANCHO_PANTALLA, ALTO_PANTALLA), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))
    
    titulo = FUENTE_TITULO.render("PAUSA", True, COLOR_FONDO_CLARO)
    surface.blit(titulo, titulo.get_rect(center=(ANCHO_PANTALLA / 2, ALTO_PANTALLA / 2 - 100)))
    
    botones = []
    
    btn_continuar = Boton((ANCHO_PANTALLA / 2 - 150, ALTO_PANTALLA / 2 - 20, 300, 60),
                          "CONTINUAR", "CONTINUAR", COLOR_ACIERTO, COLOR_FONDO_CLARO)
    btn_continuar.dibujar(surface)
    botones.append(btn_continuar)
    
    btn_menu = Boton((ANCHO_PANTALLA / 2 - 150, ALTO_PANTALLA / 2 + 60, 300, 60),
                     "SALIR AL MENÚ", "MENU", COLOR_ERROR, COLOR_FONDO_CLARO)
    btn_menu.dibujar(surface)
    botones.append(btn_menu)
    
    texto_esc = FUENTE_PEQUEÑA.render("[ESC] para continuar", True, COLOR_GRIS_CLARO)
    surface.blit(texto_esc, texto_esc.get_rect(center=(ANCHO_PANTALLA / 2, ALTO_PANTALLA - 50)))
    return botones

def dibujar_completado(juego, surface):
    surface.fill(COLOR_PRINCIPAL)
    
    titulo = FUENTE_TITULO.render("¡MISIÓN CUMPLIDA!", True, COLOR_PELIGRO)
    escenario_nombre = ESCENARIOS[juego.config.escenario_actual]["nombre"]
    subtitulo = FUENTE_MEDIANA.render(f"¡Has descubierto todos los secretos de {escenario_nombre}!", 
                                      True, COLOR_ACIERTO)
    
    surface.blit(titulo, titulo.get_rect(center=(ANCHO_PANTALLA / 2, ALTO_PANTALLA / 2 - 100)))
    surface.blit(subtitulo, subtitulo.get_rect(center=(ANCHO_PANTALLA / 2, ALTO_PANTALLA / 2)))

    texto_puntuacion = FUENTE_MEDIANA.render(f"Puntuación Total: {juego.puntuacion}", True, COLOR_FONDO_CLARO)
    rect_puntuacion = texto_puntuacion.get_rect(center=(ANCHO_PANTALLA / 2, ALTO_PANTALLA / 2 + 60))
    surface.blit(texto_puntuacion, rect_puntuacion)
    
    texto_reiniciar = FUENTE_TEXTO_UI.render("Presiona ENTER para volver al MENÚ", True, COLOR_FONDO_CLARO)
    rect_reiniciar = texto_reiniciar.get_rect(center=(ANCHO_PANTALLA / 2, ALTO_PANTALLA - 75))
    surface.blit(texto_reiniciar, rect_reiniciar)