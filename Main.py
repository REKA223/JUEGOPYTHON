#Main.py
# Main.py
from pathlib import Path
import sys
from lib.Core import Juego
import pygame

BASE = Path(__file__).parent.resolve()
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

def menu_inicial():
    pygame.init()
    ANCHO, ALTO = 1000, 800
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Menú Principal")

    # Colores
    MARRON = (139, 69, 19)
    GRIS = (169, 169, 169)
    BLANCO = (255, 255, 255)
    #Marron oscuro tirando a negro 
    MARRON_OSCURO=(69,50,46)
    # Fuentes
    fuente_titulo = pygame.font.SysFont("Centhury Gothic", 130, bold=True)
    fuente_boton = pygame.font.SysFont("Centhury Gothic", 50)

    # Título
    titulo = fuente_titulo.render("Math Dash", True, MARRON_OSCURO)
    rect_titulo = titulo.get_rect(center=(ANCHO // 2, 150))

    # Botón Play
    texto_play = fuente_boton.render("JUGAR", True, BLANCO)
    rect_play = texto_play.get_rect(center=(ANCHO // 2, 350))

    reloj = pygame.time.Clock()
    esperando = True

    while esperando:
        pantalla.fill(MARRON)

        
        # Decoración: franjas horizontales
        for y in range(0, ALTO, 40):
            pygame.draw.line(pantalla, GRIS, (0, y), (ANCHO, y), 1)

        # Dibujar título
        pantalla.blit(titulo, rect_titulo)

        # Dibujar botón
        pygame.draw.rect(pantalla, GRIS, rect_play.inflate(60, 30), border_radius=15)
        pantalla.blit(texto_play, rect_play)

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if rect_play.collidepoint(evento.pos):
                    esperando = False
                    resultado = "reiniciar"
                    while resultado == "reiniciar":
                        juego = Juego(BASE)
                        resultado = juego.run()

        reloj.tick(30)
        
if __name__ == "__main__":
    menu_inicial()

