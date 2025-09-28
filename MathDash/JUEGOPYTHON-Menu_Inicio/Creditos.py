# Apartado de Creditos para mostrar autores del programa y agradecimiento
import pygame
from lib.Colors import *
from lib.Var import MENU_ANCHO, MENU_ALTO

def mostrar_creditos():
    """
    Pantalla de créditos simple.
    - Rueda del mouse: hace scroll
    - ESC o botón 'Volver': sale
    """
    pygame.init()
    pantalla = pygame.display.set_mode((MENU_ANCHO, MENU_ALTO))
    pygame.display.set_caption("Créditos")

    clock = pygame.time.Clock()

    # Fondo base
    def dibujar_fondo():
        pantalla.fill(BROWN)
        for y in range(0, MENU_ALTO, 40):
            pygame.draw.line(pantalla, SECOND_GRAY, (0, y), (MENU_ANCHO, y), 1)

    # Fuentes 
    font_title = pygame.font.SysFont("Century Gothic", 72, bold=True)
    font_name  = pygame.font.SysFont("Century Gothic", 36)
    font_small = pygame.font.SysFont("Century Gothic", 24)

    # Contenido de créditos 
    titulo = "Créditos"
    integrantes = [
        ("Boveda Leandro", "Programación / Lógica"),
        ("Caballero Marisa", "Arte / UI"),
        ("Ianello Marcos", "Nivelación / Diseño"),
        ("Mardyks Lautaro", "Testing / QA"),
    ]
    especiales = [
        "Docente: Vilaboa Pablo",
        "Cátedra: Programacion en Python",
        "Año: 2025",
    ]

    # Pre-render de textos
    titulo_surf = font_title.render(titulo, True, DARK_BROWN)
    titulo_rect = titulo_surf.get_rect(center=(MENU_ANCHO // 2, 110))

    # Panel scrollable (simple)
    contenido = []
    y = 0
    # Sección Integrantes
    contenido.append((font_name.render("Integrantes", True, WHITE), (0, y)))
    y += 50
    for nom, rol in integrantes:
        linea = f"• {nom} — {rol}"
        surf = font_small.render(linea, True, WHITE)
        contenido.append((surf, (0, y)))
        y += 32

    y += 20
    # Sección Agradecimientos / info
    contenido.append((font_name.render("Agradecimientos", True, WHITE), (0, y)))
    y += 50
    for linea in especiales:
        surf = font_small.render(f"• {linea}", True, WHITE)
        contenido.append((surf, (0, y)))
        y += 32

    panel_w = int(MENU_ANCHO * 0.7)
    panel_h = y + 20
    panel_surf = pygame.Surface((panel_w, max(panel_h, MENU_ALTO//2)), pygame.SRCALPHA)
    panel_surf.fill((0, 0, 0, 0))  # transparente
    for surf, (lx, ly) in contenido:
        panel_surf.blit(surf, (20 + lx, 20 + ly))

    # Posición del panel en pantalla y scroll
    panel_rect = panel_surf.get_rect(center=(MENU_ANCHO // 2, MENU_ALTO // 2 + 40))
    offset_y   = 0
    max_scroll = max(0, panel_surf.get_height() - int(MENU_ALTO * 0.55))

    # Botón Volver
    btn_text = pygame.font.SysFont("Century Gothic", 40, bold=True).render("Volver", True, WHITE)
    btn_rect = btn_text.get_rect(center=(MENU_ANCHO // 2, MENU_ALTO - 80))
    btn_box  = btn_rect.inflate(60, 24)

    corriendo = True
    while corriendo:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                corriendo = False
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                corriendo = False
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if btn_box.collidepoint(e.pos):
                    corriendo = False
            elif e.type == pygame.MOUSEWHEEL:
                # Scroll vertical con rueda
                offset_y = min(max(offset_y - e.y * 30, -max_scroll), 0)

        # Dibujo
        dibujar_fondo()
        pantalla.blit(titulo_surf, titulo_rect)

        # Marco del panel
        panel_area = panel_surf.get_rect().move(panel_rect.x, panel_rect.y + offset_y)
        # Sombra ligera
        sombra = panel_area.inflate(12, 12)
        pygame.draw.rect(pantalla, DARK, sombra, border_radius=18)
        # Panel
        pygame.draw.rect(pantalla, SECOND_GRAY, panel_area, border_radius=14)
        pantalla.blit(panel_surf, (panel_area.x, panel_area.y))

        # Botón volver
        pygame.draw.rect(pantalla, BTN_RED, btn_box, border_radius=12)
        pygame.draw.rect(pantalla, OBST_BORDER, btn_box, width=2, border_radius=12)
        pantalla.blit(btn_text, btn_rect)

        pygame.display.flip()
        clock.tick(60)

    return "menu"
