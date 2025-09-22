import os, pygame

# --- Rutas ---
BASE = os.path.dirname(__file__)
SPRITE_DIR = os.path.join(BASE, "Sprite")
PERS_DIR   = os.path.join(SPRITE_DIR, "Personaje")
IMG_FONDO  = os.path.join(SPRITE_DIR, "fondo.png")
IMG_DER    = os.path.join(PERS_DIR, "derecha.png")
IMG_IZQ    = os.path.join(PERS_DIR, "izquierda.png")

# --- Config ---
PLAYER_H    = 160
ANIM_SPEED  = 0.14
MOVE_SPEED  = 320
BG_SPEED    = 140   # px/seg de desplazamiento del fondo (ajustá a gusto)

def cargar_y_escalar(path, alto_destino):
    img = pygame.image.load(path).convert_alpha()
    w, h = img.get_size()
    esc = alto_destino / h
    return pygame.transform.smoothscale(img, (int(w*esc), int(h*esc)))

def main():
    pygame.init()

    # Fondo
    bg_raw = pygame.image.load(IMG_FONDO)   # sin convertir para conocer tamaño
    ANCHO, ALTO = bg_raw.get_size()
    screen = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Runner: animación + fondo en loop")
    bg = bg_raw.convert()                    # ahora sí

    clock = pygame.time.Clock()
    font  = pygame.font.Font(None, 24)

    # Personaje: frames exactos
    frame_izq = cargar_y_escalar(IMG_IZQ, PLAYER_H)
    frame_der = cargar_y_escalar(IMG_DER, PLAYER_H)
    frames = [frame_izq, frame_der]

    GROUND_Y = int(ALTO * 0.82)

    x = ANCHO // 2
    y = GROUND_Y
    anim_idx = 0
    anim_t   = 0.0

    # Offset vertical del fondo para el loop
    bg_off = 0.0

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        # Eventos
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        # Movimiento lateral (no afecta animación)
        k = pygame.key.get_pressed()
        if k[pygame.K_LEFT]:  x -= MOVE_SPEED * dt
        if k[pygame.K_RIGHT]: x += MOVE_SPEED * dt
        x = max(30, min(ANCHO - 30, x))

        # Animación SIEMPRE activa
        anim_t += dt
        if anim_t >= ANIM_SPEED:
            anim_t = 0.0
            anim_idx ^= 1  # 0 <-> 1

        # --- DESPUÉS (que BAJE) ---
        bg_off = (bg_off + BG_SPEED * dt) % ALTO
        y1 = int(bg_off)          # invertimos el signo
        y2 = y1 - ALTO            # segunda copia arriba
        screen.blit(bg, (0, y1))
        screen.blit(bg, (0, y2))


        # Personaje
        frame = frames[anim_idx]
        rect  = frame.get_rect(midbottom=(x, y))
        screen.blit(frame, rect)

        # HUD
        screen.blit(font.render("Animación constante | ←/→ mueve | ESC sale",
                                True, (255,255,255)), (12, 12))
        pygame.display.flip()

        if k[pygame.K_ESCAPE]:
            running = False

    pygame.quit()

if __name__ == "__main__":
    main()
