# Se muestra menu principal, reproduce la musica del menu, gestiona click de Jugar para arrancar la partida y Creditos para mostrar los autores.

from pathlib import Path
import sys
import pygame, pygame.mixer
from lib.Core import Juego
from lib.Colors import *
from lib.Var import (MENU_ANCHO, MENU_ALTO, BGM_MENU, VOLUMEN_MUSICA, VOLUMEN_SFX, SFX_CLICK)
from Creditos import mostrar_creditos

BASE = Path(__file__).parent.resolve()
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

def menu_inicial():
    # Se dibuja el menu principal y se maneja su ciclo de eventos.
    # Se inicializan mixer y reproduce la musica del menu en loop.
    # Se pintan tanto el titulo como los botones.
    # Al clickear en Jugar, entra en el loop del juego.
    # Al clickear en Reiniciar, se vuelve al loop del juego.
    # Al clickear en Salir, se vuelve al menu.
    # Al clickear en Creditos, se muestran autores y agradecimientos.
    
    pygame.init()

    # --- AUDIO: mixer ---
    if not pygame.mixer.get_init():
        pygame.mixer.init()

    # --- Ventana ---
    ANCHO, ALTO = MENU_ANCHO, MENU_ALTO
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Menú Principal")

    # --- Fuentes ---
    fuente_titulo = pygame.font.SysFont("Centhury Gothic", 130, bold=True)
    fuente_boton  = pygame.font.SysFont("Centhury Gothic", 50)

    # --- Título ---
    titulo      = fuente_titulo.render("Math Dash", True, DARK_BROWN)
    rect_titulo = titulo.get_rect(center=(ANCHO // 2, 150))

    # --- Botones ---
    texto_play = fuente_boton.render("JUGAR", True, WHITE)
    rect_play  = texto_play.get_rect(center=(ANCHO // 2, 350))

    texto_cred = fuente_boton.render("CRÉDITOS", True, WHITE)
    rect_cred  = texto_cred.get_rect(center=(ANCHO // 2, 430))

    # --- Música de menú (loop) ---
    try:
        pygame.mixer.music.load(str(BGM_MENU))
        pygame.mixer.music.set_volume(VOLUMEN_MUSICA)
        pygame.mixer.music.play(-1)
    except Exception:
        pass

    # --- SFX click ---
    sfx_click = None
    try:
        sfx_click = pygame.mixer.Sound(str(SFX_CLICK))
        sfx_click.set_volume(VOLUMEN_SFX)
    except Exception:
        pass

    reloj = pygame.time.Clock()
    esperando = True

    while esperando:
        pantalla.fill(BROWN)

        # Decoración: franjas
        for y in range(0, ALTO, 40):
            pygame.draw.line(pantalla, SECOND_GRAY, (0, y), (ANCHO, y), 1)

        # Título
        pantalla.blit(titulo, rect_titulo)

        # Botón JUGAR
        pygame.draw.rect(pantalla, SECOND_GRAY, rect_play.inflate(60, 30), border_radius=15)
        pantalla.blit(texto_play, rect_play)

        # Botón CRÉDITOS
        pygame.draw.rect(pantalla, SECOND_GRAY, rect_cred.inflate(60, 30), border_radius=15)
        pantalla.blit(texto_cred, rect_cred)

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                try: pygame.mixer.music.stop()
                except Exception: pass
                pygame.quit()
                sys.exit()

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                # CLICK EN JUGAR
                if rect_play.collidepoint(evento.pos):
                    if sfx_click: sfx_click.play()
                    try: pygame.mixer.music.fadeout(300)  # Evita superponer la música del menú con la del juego., desvaneciendo la musica del menu.
                    except Exception: pass

                    resultado = "reiniciar"
                    while resultado == "reiniciar":
                        juego = Juego(BASE)
                        resultado = juego.run()

                    # Al volver del juego: restablecer ventana y música del menú
                    pantalla = pygame.display.set_mode((ANCHO, ALTO))
                    try:
                        pygame.mixer.music.load(str(BGM_MENU))
                        pygame.mixer.music.set_volume(VOLUMEN_MUSICA)
                        pygame.mixer.music.play(-1)
                    except Exception:
                        pass

                # CLICK EN CRÉDITOS
                elif rect_cred.collidepoint(evento.pos):
                    if sfx_click: sfx_click.play()
                    mostrar_creditos()

        reloj.tick(30)

if __name__ == "__main__":
    menu_inicial()
