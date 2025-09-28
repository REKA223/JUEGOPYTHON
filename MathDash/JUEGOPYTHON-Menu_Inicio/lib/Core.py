# Apartado que contiene la logica del juego
import pygame, random
from lib.Var import *
from lib.Colors import *
from pathlib import Path
from .utils import cargar_imagen, escalar_a_tamaño
from lib.Preguntas.preguntas import GestorPreguntas, Pregunta


# ------------------------- JUGADOR -------------------------

import pygame

class Jugador(pygame.sprite.Sprite):
    def __init__(
        self,
        frames,                 # lista de superficies (frame_izq, frame_der) o anims
        x_positions,            # lista con las X de cada carril 
        carril_inicial_idx,     # índice inicial (0, 1 o 2)
        suelo_y,                # coordenada Y del suelo 
        velocidad_anim=0.12,    # segundos entre cambios de frame
        invulnerabilidad=0.9,   # segundos de invulnerabilidad tras daño
        cooldown_cambio=0.18    # tiempo mínimo entre cambios de carril
    ):
        super().__init__()
        self.frames = frames
        self.frame_idx = 0
        self._anim_t = 0.0
        self._velocidad_anim = float(velocidad_anim)

        self.x_positions = list(x_positions)
        self._carril = int(carril_inicial_idx)
        self.suelo_y = int(suelo_y)

        # imagen/rect inicial
        self.image = self.frames[self.frame_idx]
        self.rect = self.image.get_rect(midbottom=(self.x_positions[self._carril], self.suelo_y))

        # estado
        self._vidas = 3
        self._invulnerable = 0.0         # cuenta regresiva (seg)
        self._invul_total = float(invulnerabilidad)
        self._cooldown_cambio = float(cooldown_cambio)
        self._timer_cambio = 0.0         # cuenta regresiva (seg)

    # ------------ INPUT (izq/der) ------------
    def manejar_entrada(self, teclas, dt: float):
        self._timer_cambio = max(0.0, self._timer_cambio - dt)
        movio = False
        if self._timer_cambio == 0.0:
            if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
                movio = self._mover_carril(-1)
            elif teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
                movio = self._mover_carril(+1)
        if movio:
            self._timer_cambio = self._cooldown_cambio

    def _mover_carril(self, delta: int) -> bool:
        nuevo = max(0, min(len(self.x_positions) - 1, self._carril + delta))
        if nuevo != self._carril:
            self._carril = nuevo
            return True
        return False

    # ------------ UPDATE (animación/posición/estado) ------------
    def actualizar(self, dt: float):
        # animación simple: alterna frames cada self._velocidad_anim
        self._anim_t += dt
        if self._anim_t >= self._velocidad_anim:
            self._anim_t = 0.0
            self.frame_idx = 1 - self.frame_idx  # 0 <-> 1
            self.image = self.frames[self.frame_idx]

        # fijar posición en el carril actual y pegado al “suelo”
        self.rect.midbottom = (self.x_positions[self._carril], self.suelo_y)

        # bajar invulnerabilidad / cooldown
        if self._invulnerable > 0.0:
            self._invulnerable = max(0.0, self._invulnerable - dt)
        if self._timer_cambio > 0.0:
            self._timer_cambio = max(0.0, self._timer_cambio - dt)

    # ------------ RENDER ------------
    def dibujar(self, surface: pygame.Surface):
        # parpadeo cuando está invulnerable
        if self._invulnerable > 0.0:
            # blink ~10 Hz: alterna visibilidad
            if int(self._invulnerable * 20) % 2 == 0:
                img = self.image.copy()
                img.set_alpha(150)
                surface.blit(img, self.rect)
            else:
                surface.blit(self.image, self.rect)
        else:
            surface.blit(self.image, self.rect)

    # ------------ VIDA / CONSULTAS ------------
    def perder_vida(self):
        if self._invulnerable == 0.0 and self._vidas > 0:
            self._vidas -= 1
            self._invulnerable = self._invul_total

    def get_vidas(self) -> int:
        return self._vidas

    def get_rect(self) -> pygame.Rect:
        return self.rect




# ------- PREGUNTA --------------
class Pregunta:
    def __init__(self, enunciado, valor_izq, valor_der, carril_correcto):
        # carril_correcto: "izq" | "der"
        self.enunciado = enunciado
        self.valor_izq = valor_izq
        self.valor_der = valor_der
        self.carril_correcto = carril_correcto

class GestorPreguntas:
    def __init__(self, operaciones=("suma", "resta", "mul"), rango=(1, 12)):
        self.operaciones = tuple(operaciones) if operaciones else ("suma",)
        self.rango = rango
        self.pregunta_actual = None
        self._rnd = random.Random()

    def _generar_operacion(self, operaciones, rango):
        a = self._rnd.randint(rango[0], rango[1])
        b = self._rnd.randint(rango[0], rango[1])
        if not operaciones:
            op = "suma"
        else:
            op = operaciones[self._rnd.randrange(len(operaciones))]

        if op == "suma":
            res = a + b
            texto = f"{a} + {b} = ?"
        elif op == "resta":
            if b > a:
                a, b = b, a
            res = a - b
            texto = f"{a} - {b} = ?"
        else:
            res = a * b
            texto = f"{a} × {b} = ?"

        delta = self._rnd.choice([-2, -1, 1, 2])
        distractor = res + delta
        if distractor == res:
            distractor += 1

        #carril correcto aleatorio
        if self._rnd.random() < 0.5:
            return Pregunta(texto, res, distractor, "izq")
        else:
            return Pregunta(texto, distractor, res, "der")

    def siguiente_pregunta(self, operaciones, rango_operandos):
        self.pregunta_actual = self._generar_operacion(operaciones, rango_operandos)
        return self.pregunta_actual

    def evaluar_eleccion(self, carril):
        return self.pregunta_actual is not None and carril == self.pregunta_actual.carril_correcto
    
# ------BALDOSA DE RESPUESTA--------
class BaldosaRespuesta:
    def __init__(self, valor, x_centro, y_top, ancho, alto, color_fondo, color_borde, fuente):
        self.valor = valor
        self.color_fondo = color_fondo
        self.color_borde = color_borde
        self.fuente = fuente

        self.rect = pygame.Rect(0, 0, int(ancho), int(alto))
        self.rect.centerx = int(x_centro)   
        self.rect.top = int(y_top)

    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, self.color_fondo, self.rect, border_radius=12)
        pygame.draw.rect(pantalla, self.color_borde, self.rect, width=3, border_radius=12)
        txt = self.fuente.render(str(self.valor), True, WHITE)
        pantalla.blit(
            txt,
            (self.rect.centerx - txt.get_width() // 2,
             self.rect.centery - txt.get_height() // 2)
        )


# ---------- PROGRESIÓN -----------------------
class ParametrosNivel:
    def __init__(self, nivel, puntaje_minimo, velocidad_juego, intervalo_preguntas, intervalo_obstaculos, rango_operandos):
        self.nivel = nivel
        self.puntaje_minimo = puntaje_minimo
        self.velocidad_juego = velocidad_juego
        self.intervalo_preguntas = intervalo_preguntas
        self.intervalo_obstaculos = intervalo_obstaculos
        self.rango_operandos = rango_operandos

# Tabla de niveles
NIVELES_PREDEF = [
    ParametrosNivel(nivel=1, puntaje_minimo=0,   velocidad_juego=5.0, intervalo_preguntas=1.8, intervalo_obstaculos=1.6, rango_operandos=(1, 10)),
    ParametrosNivel(nivel=2, puntaje_minimo=1000, velocidad_juego=6.0, intervalo_preguntas=1.4, intervalo_obstaculos=1.4, rango_operandos=(1, 15)),
    ParametrosNivel(nivel=3, puntaje_minimo=2000, velocidad_juego=7.0, intervalo_preguntas=1.1, intervalo_obstaculos=1.2, rango_operandos=(1, 20)),
]

class Progresion:
 # Se ajusta la dificultad del juego en base al puntaje obtenido, cada 500 pts se realiza un aumento de velocidad en la caida de las baldosas

    def __init__(self):
        self.DIFF_STEP_PUNTOS = DIFF_STEP_PUNTOS
        self.CAIDA_BASE_PX_S  = CAIDA_BASE_PX_S
        self.CAIDA_STEP_PX_S  = CAIDA_STEP_PX_S
        self.CAIDA_MAX_PX_S   = CAIDA_MAX_PX_S
        self.PREG_BASE_S      = PREGUNTA_BASE_S
        self.PREG_STEP_S      = PREGUNTA_STEP_S
        self.PREG_MIN_S       = PREGUNTA_MIN_S
        self.OBST_BASE_S      = OBST_BASE_S
        self.OBST_STEP_S      = OBST_STEP_S
        self.OBST_MIN_S       = OBST_MIN_S

        # Valores “vivos” iniciales
        self.velocidad_juego       = self.CAIDA_BASE_PX_S
        self.intervalo_preguntas   = self.PREG_BASE_S
        self.intervalo_obstaculos  = self.OBST_BASE_S

    def actualizar_por_puntaje(self, puntaje: int) -> None:
        # Recalcula velocidad e intervalos según el puntaje actual.
        # Sube por escalones cada DIFF_STEP_PUNTOS.
        
        nivel = max(0, puntaje // self.DIFF_STEP_PUNTOS)

        # Velocidad: base + nivel*step, acotada por un máximo
        self.velocidad_juego = min(
            self.CAIDA_BASE_PX_S + nivel * self.CAIDA_STEP_PX_S,
            self.CAIDA_MAX_PX_S
        )

        # Intervalos: base - nivel*step, acotados por un mínimo
        self.intervalo_preguntas = max(
            self.PREG_BASE_S - nivel * self.PREG_STEP_S,
            self.PREG_MIN_S
        )
        self.intervalo_obstaculos = max(
            self.OBST_BASE_S - nivel * self.OBST_STEP_S,
            self.OBST_MIN_S
        )

            
# ------------------------- HELPERS DE DIBUJO (HUD) -------------------------
def dibujar_vidas(pantalla, vidas, x=300, y=25, w=24, h=24, gap=8):
    import pygame
    for i in range(vidas):
        r = pygame.Rect(x + i*(w+gap), y, w, h)
        pygame.draw.rect(pantalla, LIFE_RED, r, border_radius=6)
        pygame.draw.rect(pantalla, BORDER_DK, r, width=2, border_radius=6)

def dibujar_carriles(pantalla, x_positions, y_top, y_bottom, color=(60, 60, 70)):
    import pygame
    for x in x_positions:
        pygame.draw.line(pantalla, color, (x, y_top), (x, y_bottom), width=2)

#-----------------------fondo------------------------------------
class FondoScroll:
    """
    Scroll vertical infinito SIEMPRE hacia abajo, sin escalar la imagen.
    La imagen del fondo DEBE tener exactamente el tamaño de pantalla.
    """
    def __init__(self, imagen_surface, tamaño_pantalla, velocidad_px_s=160):
        self._w, self._h = tamaño_pantalla

        self._img = imagen_surface
        self._vel = float(velocidad_px_s)
        self._y1, self._y2 = 0.0, float(self._h)
    def get_velocidad(self):
        return self._vel

    def set_velocidad(self, px_por_seg):
        self._vel = float(px_por_seg)

    # -------- LÓGICA --------
    def actualizar(self, dt):
        dy = self._vel * dt
        self._y1 += dy
        self._y2 += dy
        #loop infinito hacia abajo
        if self._y1 >= self._h:
            self._y1 = self._y2 - self._h
        if self._y2 >= self._h:
            self._y2 = self._y1 - self._h

    def dibujar(self, pantalla):
        pantalla.blit(self._img, (0, int(self._y1)))
        pantalla.blit(self._img, (0, int(self._y2)))

#---------------------- JUEGO ---------------------------
class Juego:
    # Bucle principal del juego
    '''
    Gestiona recursos, entrada del jugador, generación y movimiento de
    baldosas/obstáculos, detección de colisiones, puntaje, vidas, pausa
    y Game Over. También controla la música y los efectos de sonido
    durante la partida.
    '''
    def __init__(self, carpeta_base: Path, ancho=1500, alto=1000, fps=60):
        if not pygame.get_init():
            pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # SFX
        self.sfx_ok = self.sfx_bad = self.sfx_hit = self.sfx_pause = None
        try:
            self.sfx_ok  = pygame.mixer.Sound(str(SFX_OK));  self.sfx_ok.set_volume(VOLUMEN_SFX)
            self.sfx_bad = pygame.mixer.Sound(str(SFX_BAD)); self.sfx_bad.set_volume(VOLUMEN_SFX)
            self.sfx_hit = pygame.mixer.Sound(str(SFX_HIT)); self.sfx_hit.set_volume(VOLUMEN_SFX)
            self.sfx_pause = pygame.mixer.Sound(str(SFX_CLICK))
            self.sfx_pause.set_volume(VOLUMEN_SFX * 0.9)  # un toque más bajo
        except Exception:
            pass
        
        # Música ingame
        try:
            pygame.mixer.music.load(str(BGM_GAME))
            pygame.mixer.music.set_volume(VOLUMEN_MUSICA)
            pygame.mixer.music.play(-1)
        except Exception:
            pass

        self.pregunta_activa = False
        self.pausado = False
        self.game_over = False
        self.game_over_timer = 0.0

        #fuente para el enunciado
        self.fuente_enunciado = pygame.font.SysFont("Century Gothic", 64, bold=True)

        #fuente grande para el cartel
        self.fuente_game_over = pygame.font.SysFont(None, 96)
        
        #ventana fija igual al fondo
        self.ANCHO, self.ALTO, self.FPS = ancho, alto, fps

        #tamaño fijo del personaje en pantalla
        self.TAM_PERSONAJE = TAM_PERSONAJE  # (ancho, alto)

        # Carriles
        self.X_IZQ  = int(self.ANCHO * LANE_X_LEFT)
        self.X_CEN  = int(self.ANCHO * LANE_X_CENTER)
        self.X_DER  = int(self.ANCHO * LANE_X_RIGHT)
        self.CARRILES = [self.X_IZQ, self.X_CEN, self.X_DER]
        self.SUELO_Y = int(self.ALTO * SUELO_Y_RATIO)
        self.BASE = carpeta_base
        
        self.CARPETA_SPRITES = CARPETA_SPRITES
        self.CARPETA_PERSONAJE = CARPETA_PERSONAJE 

        #pygame.init()
        self.pantalla = pygame.display.set_mode((self.ANCHO, self.ALTO))
        pygame.display.set_caption("Juego Educativo - Carriles")
        self.reloj = pygame.time.Clock()
        self.progresion = Progresion()
        #carga y entidades
        self._cargar_recursos()
        self._crear_entidades()

        # --- Math Runner state ---
        self.puntaje = 0
        self.fuente = pygame.font.SysFont(None, 48)

        self.gestor = GestorPreguntas(
            operaciones= OPERACIONES, rango=RANGO_OPERANDOS) 
            # rango de operandos inicial   
            # genera preguntas
        self.baldosas = []      # opciones de respuesta (izq/der)
        self.obstaculos = []    # obstáculos que caen
        self.tiempo_preguntas = 0.0
        self.tiempo_obstaculos = 0.0
        self.enunciado_actual = ""
        self.answer_grace_timer = 0.0
        self.corriendo = True
        self.reiniciar = False
        self.pausado = False
        self.game_over = False

    # -------recursos-------
    def _cargar_recursos(self):
        #fondo
        fondo_img = cargar_imagen(FONDO_FILE, con_alpha=False)
        self.fondo = FondoScroll(fondo_img, (self.ANCHO, self.ALTO), velocidad_px_s=180)

        #personaje
        frame_izq = cargar_imagen(self.CARPETA_PERSONAJE / "izquierda.png")
        frame_der = cargar_imagen(self.CARPETA_PERSONAJE / "derecha.png")
        frame_izq = escalar_a_tamaño(frame_izq, *self.TAM_PERSONAJE)
        frame_der = escalar_a_tamaño(frame_der, *self.TAM_PERSONAJE)
        self.frames_personaje = [frame_izq, frame_der]

    # -------crear objetos de juego--------------
    def _crear_entidades(self):
        self.jugador = Jugador(
            frames=self.frames_personaje,
            x_positions=self.CARRILES,
            carril_inicial_idx=1,
            suelo_y=self.SUELO_Y,
            velocidad_anim=ANIM_FRAME_SECONDS,
            invulnerabilidad=INVULNERABLE_SECONDS,
            cooldown_cambio=COOLDOWN_CAMBIO_SECONDS,    
        )

    def _render_text_wrapped(self, text: str, font: pygame.font.Font, color: tuple[int,int,int], max_width: int):
    #Devuelve una lista de superficies de texto, envueltas para no exceder max_width.
        if not text:
            return []
        words = text.split(" ")
        lines = []
        current = ""

        for w in words:
            test = (current + " " + w) if current else w
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(font.render(current, True, color))
                current = w

        if current:
            lines.append(font.render(current, True, color))
        return lines

    
    def _spawn_pregunta(self):
        # Genera una nueva pregunta y las 2 baldosas de respuesta.
        preg = self.gestor.siguiente_pregunta(
            operaciones=OPERACIONES,
            rango_operandos=RANGO_OPERANDOS  
        )


        self.enunciado_actual = preg.enunciado
        color_fondo = TILE_FILL
        color_borde = TILE_BORDER
        ancho, alto, y_top = BALDOSA_ANCHO, BALDOSA_ALTO, int(self.ALTO * BALDOSA_Y_TOP_P)

        self.baldosas = [
            BaldosaRespuesta( # Baldosa del carril izquierdo
                valor=preg.valor_izq,
                x_centro=self.X_IZQ,   
                y_top=y_top,
                ancho=ancho,
                alto=alto,
                color_fondo=color_fondo,
                color_borde=color_borde,
                fuente=self.fuente,
            ),
            BaldosaRespuesta( # Baldosa del carril derecho
                valor=preg.valor_der,
                x_centro=self.X_DER,   
                y_top=y_top,
                ancho=ancho,
                alto=alto,
                color_fondo=color_borde,  
                color_borde=color_borde,
                fuente=self.fuente,
            ),
        ]
        self.pregunta_activa = True


    # -------crear obstáculo--------------
    def _lane_idx_for_x(self, x):
        return min(range(len(self.CARRILES)), key=lambda i: abs(self.CARRILES[i] - x))

    def _spawn_obstaculo(self):
        r = pygame.Rect(0, 0, OBST_W, OBST_H)
    
        # Elegir carril
        carril_x = random.choice([self.X_IZQ, self.X_CEN, self.X_DER])
        r.centerx = carril_x
    
        # Altura base (aparece arriba de la pantalla)
        y_top = -r.height - 40
    
        # Evitar superposición con baldosas en el mismo carril
        # Tomo la Y de las baldosas (top) en ese carril
        mismo_carril = [
            b for b in self.baldosas
            if abs(b.rect.centerx - carril_x) <= self.ANCHO * 0.02   # tolerancia horizontal
        ]
        if mismo_carril:
            top_mas_alto = min(b.rect.top for b in mismo_carril)
            y_top = min(y_top, top_mas_alto - OBST_GAP_VERTICAL_PX - r.height)
    
        r.top = y_top
        self.obstaculos.append(r)




    # -------loop principal----------
    def run(self):
        # estado limpio al iniciar cada partida
        self.reiniciar = False
        self.corriendo = True
        self.pausado   = False

        while self.corriendo:
            dt = self.reloj.tick(self.FPS) / 1000.0
            self._eventos()
            if not self.pausado and not self.game_over:
                self._actualizar(dt)
            self._dibujar()

        return "reiniciar" if self.reiniciar else "salir"




    # -----partes del loop---------------
    def _eventos(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                # cerrar ventana para salir del juego, NO para reiniciar
                self.reiniciar = False
                self.corriendo = False

            elif e.type == pygame.KEYDOWN and e.key == pygame.K_p and not self.game_over:
                if self.sfx_pause:
                    self.sfx_pause.play()
                self.pausado = not self.pausado
                try:
                    if self.pausado:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                except Exception:
                    pass

            # --- GAME OVER ---
            elif self.game_over and e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = e.pos
                if hasattr(self, "rect_reintentar") and self.rect_reintentar.collidepoint(mx, my):
                    self.reiniciar = True
                    self.corriendo = False
                elif hasattr(self, "rect_salir") and self.rect_salir.collidepoint(mx, my):
                    self.reiniciar = False
                    self.corriendo = False

            # --- PAUSA ---
            elif self.pausado and e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = e.pos
                if hasattr(self, "rect_reanudar") and self.rect_reanudar.collidepoint(mx, my):
                    self.pausado = False
                elif hasattr(self, "rect_salir") and self.rect_salir.collidepoint(mx, my):
                    self.reiniciar = False
                    self.corriendo = False        

      

    def _actualizar(self, dt: float):
        # velocidad del juego según nivel
        self.progresion.actualizar_por_puntaje(self.puntaje)
        # Entrada + jugador
        teclas = pygame.key.get_pressed()
        self.jugador.manejar_entrada(teclas, dt)
        self.jugador.actualizar(dt)
        self.answer_grace_timer = max(0.0, self.answer_grace_timer - dt)


        # Timers (preguntas / obstáculos)
        self.tiempo_preguntas += dt
        self.tiempo_obstaculos += dt

        if self.tiempo_preguntas >= self.progresion.intervalo_preguntas and not self.baldosas:
            self.tiempo_preguntas = 0.0
            self._spawn_pregunta()

        if self.tiempo_obstaculos >= self.progresion.intervalo_obstaculos:
            self.tiempo_obstaculos = 0.0
            self._spawn_obstaculo()

        # Movimiento descendente
        vel = self.progresion.velocidad_juego  
        for b in self.baldosas:
            b.rect.move_ip(0, vel * dt)
        # --- Penalizar si la correcta pasó sin tocarla ---
        if self.pregunta_activa and self.baldosas and getattr(self.gestor, "pregunta_actual", None):
            # X del carril correcto según el gestor
            x_correcta = self.X_IZQ if self.gestor.pregunta_actual.carril_correcto == "izq" else self.X_DER
            # Baldosa “correcta” = la más cercana a esa X
            baldosa_correcta = min(self.baldosas, key=lambda b: abs(b.rect.centerx - x_correcta))
            # Si ya pasó por debajo del jugador se pierde la vida
            if baldosa_correcta.rect.top > self.jugador.get_rect().bottom:
                self.jugador.perder_vida()
                if self.sfx_bad:
                    self.sfx_bad.play()
                self.baldosas.clear()
                self.enunciado_actual = ""
                self.pregunta_activa = False
    
        self.baldosas = [b for b in self.baldosas if b.rect.top < self.ALTO + 20]

        for r in self.obstaculos:
            r.move_ip(0, vel * dt)

        self.obstaculos = [r for r in self.obstaculos if r.top < self.ALTO + 50]

        # Colisiones
        jr = self.jugador.get_rect()

        # a) Respuestas (prioridad)
        if self.baldosas:
            tocadas = [b for b in self.baldosas if jr.colliderect(b.rect)]
            if tocadas:
                carril = (
                    "izq"
                    if abs(tocadas[0].rect.centerx - self.X_IZQ)
                    <= abs(tocadas[0].rect.centerx - self.X_DER)
                    else "der"
                )
                if self.gestor.evaluar_eleccion(carril):
                    self.puntaje += PUNTAJE_CORRECTA
                    if self.sfx_ok : self.sfx_ok.play()
                else:
                    self.jugador.perder_vida()
                    if self.sfx_bad : self.sfx_bad.play()

                self.baldosas.clear()
                self.enunciado_actual = ""
                self.pregunta_activa = False
                self.answer_grace_timer = ANSWER_GRACE_SECONDS   # 300 ms sin colisión con obstáculos


        # b) Obstáculos
        for r in list(self.obstaculos):
            if self.answer_grace_timer <= 0.0 and jr.colliderect(r):
                self.jugador.perder_vida()
                if self.sfx_hit:
                    self.sfx_hit.play()
                self.obstaculos.remove(r)


        # Fondo
        self.fondo.actualizar(dt)

        # --- Disparar GAME OVER cuando no quedan vidas ---
        if self.jugador.get_vidas() <= 0 and not self.game_over:
            self.game_over = True
            self.pausado = False
            self.game_over_timer = 0.0

    def _dibujar(self):
        # Fondo
        self.fondo.dibujar(self.pantalla)


        # Baldosas de respuesta (encima)
        for b in self.baldosas:
            b.dibujar(self.pantalla)

        # Obstáculos (al fondo)
        for r in self.obstaculos:
            pygame.draw.rect(self.pantalla, OBST_FILL, r, border_radius=8)
            pygame.draw.rect(self.pantalla, OBST_BORDER, r, width=2, border_radius=8)

        # Jugador + vidas
        self.jugador.dibujar(self.pantalla)
        dibujar_vidas(self.pantalla, self.jugador.get_vidas())

        # HUD: puntaje + enunciado
        if not hasattr(self, "fuente"):
            self.fuente = pygame.font.SysFont(None, 48)

        puntos = self.fuente.render(f"Puntos: {self.puntaje}", True, WHITE)
        self.pantalla.blit(puntos, (20, 20))

        # --- Enunciado grande en recuadro ---
        if getattr(self, "enunciado_actual", ""):
            # Configuracion
            max_text_w = int(self.ANCHO * 0.75)   # ancho máximo del texto dentro del recuadro
            txt_color  = WHITE                    # blanco para el texto
            box_color  = TRANSPARENCIA            # negro semitransparente (RGBA)
            border_col = WHITE                    # borde blanco
            pad_x, pad_y = 24, 16                 # padding interno del recuadro
            line_gap = 6                          # espacio entre líneas

            # Partir en líneas
            lines = self._render_text_wrapped(self.enunciado_actual, self.fuente_enunciado, txt_color, max_text_w)
            if lines:
                # Medidas del recuadro según líneas
                text_h_total = sum(s.get_height() for s in lines) + line_gap * (len(lines) - 1)
                text_w_max   = max(s.get_width() for s in lines)
                panel_w      = text_w_max + pad_x * 2
                panel_h      = text_h_total + pad_y * 2

                # Rect centrado en la parte superior
                panel_rect = pygame.Rect(0, 0, panel_w, panel_h)
                panel_rect.center = (self.ANCHO // 2, int(self.ALTO * 0.11))

                # Superficie con alpha para el fondo
                panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
                panel_surf.fill((0, 0, 0, 0))  # transparente
                pygame.draw.rect(panel_surf, box_color, panel_surf.get_rect(), border_radius=16)

                # Borde (sobre la pantalla para que quede nítido)
                self.pantalla.blit(panel_surf, panel_rect.topleft)
                pygame.draw.rect(self.pantalla, border_col, panel_rect, width=2, border_radius=16)

                # Blitear líneas centradas dentro del panel
                y = panel_rect.top + pad_y
                for surf in lines:
                    r = surf.get_rect(centerx=panel_rect.centerx, top=y)
                    self.pantalla.blit(surf, r)
                    y += surf.get_height() + line_gap


        if self.game_over:
            # Capa oscura semitransparente
            overlay = pygame.Surface((self.ANCHO, self.ALTO))
            overlay.set_alpha(160)
            overlay.fill(BLACK)
            self.pantalla.blit(overlay, (0, 0))

            

        # Pausa
        if self.pausado:
            overlay = pygame.Surface((self.ANCHO, self.ALTO))
            overlay.set_alpha(180)
            overlay.fill(DARK)
            self.pantalla.blit(overlay, (0, 0))

            fuente = pygame.font.SysFont(None, 72)
            txt_pausa = fuente.render("PAUSA", True, HUD_EMPH)
            rect_pausa = txt_pausa.get_rect(center=(self.ANCHO // 2, self.ALTO // 2 - 120))
            self.pantalla.blit(txt_pausa, rect_pausa)

            fuente_btn = pygame.font.SysFont(None, 48)
            txt_reanudar = fuente_btn.render("Reanudar", True, WHITE)
            txt_salir = fuente_btn.render("Salir", True, WHITE)

            self.rect_reanudar = txt_reanudar.get_rect(center=(self.ANCHO // 2, self.ALTO // 2))
            self.rect_salir = txt_salir.get_rect(center=(self.ANCHO // 2, self.ALTO // 2 + 80))

            pygame.draw.rect(self.pantalla, BTN_GREEN, self.rect_reanudar.inflate(40, 20), border_radius=12)
            pygame.draw.rect(self.pantalla, BTN_RED, self.rect_salir.inflate(40, 20), border_radius=12)

            self.pantalla.blit(txt_reanudar, self.rect_reanudar)
            self.pantalla.blit(txt_salir, self.rect_salir)

        # Game Over
        if self.game_over:
            overlay = pygame.Surface((self.ANCHO, self.ALTO))
            overlay.set_alpha(180)
            overlay.fill(DARK_RED)
            self.pantalla.blit(overlay, (0, 0))

            fuente = pygame.font.SysFont(None, 72)
            txt_over = fuente.render("GAME OVER", True, RED)
            rect_over = txt_over.get_rect(center=(self.ANCHO // 2, self.ALTO // 2 - 120))
            self.pantalla.blit(txt_over, rect_over)

            fuente_btn = pygame.font.SysFont(None, 48)
            txt_reintentar = fuente_btn.render("Reintentar", True, WHITE)
            txt_salir = fuente_btn.render("Salir", True, WHITE)

            self.rect_reintentar = txt_reintentar.get_rect(center=(self.ANCHO // 2, self.ALTO // 2))
            self.rect_salir = txt_salir.get_rect(center=(self.ANCHO // 2, self.ALTO // 2 + 80))

            pygame.draw.rect(self.pantalla, BTN_GREEN, self.rect_reintentar.inflate(40, 20), border_radius=12)
            pygame.draw.rect(self.pantalla, BTN_RED, self.rect_salir.inflate(40, 20), border_radius=12)

            self.pantalla.blit(txt_reintentar, self.rect_reintentar)
            self.pantalla.blit(txt_salir, self.rect_salir)

            # Textos
            txt_score = self.fuente.render(f"Puntaje final: {self.puntaje}", True, WHITE)
            rect_sc = txt_score.get_rect(center=(self.ANCHO // 2, self.ALTO // 2 - 200))
            self.pantalla.blit(txt_score, rect_sc)
        pygame.display.flip()

