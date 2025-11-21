import pygame
from scenes.utils import * # Importa colores y fuentes

# Carga las fuentes una vez
FUENTES = cargar_fuentes()
FUENTE_TEXTO_UI = FUENTES[3]
FUENTE_DATO = FUENTES[5]

# --- Clase Botón Mejorada ---
class Boton:
    def __init__(self, rect, texto, accion, color_fondo, color_texto, icono=None):
        self.rect = pygame.Rect(rect)
        self.texto = texto
        self.accion = accion
        self.color_fondo = color_fondo
        self.color_texto = color_texto
        self.icono = icono
        self.hover = False
        
    def dibujar(self, surface):
        # Efecto hover
        color = self.color_fondo
        if self.hover:
            color = tuple(min(c + 30, 255) for c in self.color_fondo)
        
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        
        # Sombra sutil
        sombra_rect = self.rect.copy()
        sombra_rect.y += 2
        pygame.draw.rect(surface, COLOR_GRIS_CLARO, sombra_rect, 2, border_radius=10)
        
        texto_render = FUENTE_TEXTO_UI.render(self.texto, True, self.color_texto)
        surface.blit(texto_render, texto_render.get_rect(center=self.rect.center))
        
    def verificar_clic(self, pos):
        return self.rect.collidepoint(pos)
    
    def verificar_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)

# --- Clase Slider (para volumen) ---
class Slider:
    def __init__(self, x, y, w, h, valor_inicial=0.5, min_val=0.0, max_val=1.0):
        self.rect = pygame.Rect(x, y, w, h)
        self.valor = valor_inicial
        self.min_val = min_val
        self.max_val = max_val
        self.arrastrando = False
        self.circulo_radio = 12
        
    def manejar_evento(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            circulo_x = self.rect.x + (self.valor - self.min_val) / (self.max_val - self.min_val) * self.rect.width
            circulo_rect = pygame.Rect(circulo_x - self.circulo_radio, 
                                       self.rect.centery - self.circulo_radio,
                                       self.circulo_radio * 2, self.circulo_radio * 2)
            if circulo_rect.collidepoint(event.pos):
                self.arrastrando = True
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.arrastrando = False
        
        elif event.type == pygame.MOUSEMOTION and self.arrastrando:
            pos_relativa = event.pos[0] - self.rect.x
            pos_relativa = max(0, min(pos_relativa, self.rect.width))
            self.valor = self.min_val + (pos_relativa / self.rect.width) * (self.max_val - self.min_val)
    
    def dibujar(self, surface):
        pygame.draw.rect(surface, COLOR_GRIS_CLARO, self.rect, border_radius=5)
        
        progreso_w = (self.valor - self.min_val) / (self.max_val - self.min_val) * self.rect.width
        progreso_rect = pygame.Rect(self.rect.x, self.rect.y, progreso_w, self.rect.height)
        pygame.draw.rect(surface, COLOR_ACENTO_PRIMARIO, progreso_rect, border_radius=5)
        
        circulo_x = self.rect.x + progreso_w
        pygame.draw.circle(surface, COLOR_FONDO_CLARO, (int(circulo_x), self.rect.centery), self.circulo_radio)
        pygame.draw.circle(surface, COLOR_PRINCIPAL, (int(circulo_x), self.rect.centery), self.circulo_radio, 2)

# --- Funciones de utilidad ---
def wrap_text(surface, text, font, color, rect, align="center", line_height_factor=1.2):
    # (El resto de la implementación de wrap_text va aquí, sin cambios)
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        if font.size(' '.join(current_line + [word]))[0] < rect.width - 20:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))
    
    total_height = len(lines) * font.size("Hg")[1] * line_height_factor
    start_y = rect.centery - total_height / 2
    
    for i, line in enumerate(lines):
        rendered_line = font.render(line, True, color)
        line_rect = rendered_line.get_rect()
        y_pos = start_y + i * font.size("Hg")[1] * line_height_factor
        
        if align == "center":
            line_rect.centerx = rect.centerx
        else:
            line_rect.left = rect.left + 10
        
        line_rect.top = y_pos
        surface.blit(rendered_line, line_rect)