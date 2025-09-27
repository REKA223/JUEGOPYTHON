# lib/Core.py
import pygame
from pathlib import Path
from .utils import cargar_imagen, escalar_a_tamaño

# ------------------------- JUGADOR -------------------------

class Jugador:
    def __init__(self, frames, x_positions, carril_inicial_idx, suelo_y,
                 velocidad_anim=0.14, invulnerabilidad=1.0):
        if len(frames) < 2: raise ValueError("Se esperan >=2 frames")
        if len(x_positions) != 3: raise ValueError("Se esperan 3 carriles")
        if not (0 <= carril_inicial_idx < 3): raise IndexError("Carril inicial inválido")
        self._frames = frames
        self._x_positions = x_positions
        self._carril = carril_inicial_idx
        self._suelo_y = suelo_y

        self._indice_anim = 0
        self._tiempo_anim = 0.0
        self._velocidad_anim = float(velocidad_anim)

        self._vidas_max = 3
        self._vidas = 3
        self._invulnerable = False
        self._timer_invul = 0.0
        self._invulnerabilidad = float(invulnerabilidad)

        x = self._x_positions[self._carril]
        self._rect = self._frames[0].get_rect(midbottom=(x, self._suelo_y))

        self._cooldown_cambio = 0.15
        self._timer_cambio = 0.0

    def get_vidas(self):
        return self._vidas

    def set_vidas(self, valor):
        v = int(valor)
        if v < 0: v = 0
        if v > self._vidas_max: v = self._vidas_max
        self._vidas = v

    def get_vidas_max(self):
        return self._vidas_max

    def get_carril(self):
        return self._carril#0,1,2

    def set_carril(self, idx):
        i = int(idx)
        if 0 <= i <= 2:
            self._carril = i

    def get_rect(self):
        return self._rect

    def get_invulnerable(self):
        return self._invulnerable

    def get_velocidad_anim(self):
        return self._velocidad_anim

    def set_velocidad_anim(self, v):
        self._velocidad_anim = float(v)

    def perder_vida(self):
        if (not self._invulnerable) and self._vidas > 0:
            self._vidas -= 1
            self._invulnerable = True
            self._timer_invul = self._invulnerabilidad

    def mover_izquierda(self):
        self._mover_carril(-1)

    def mover_derecha(self):
        self._mover_carril(+1)

    def manejar_entrada(self, teclas, dt):
        self._timer_cambio = max(0.0, self._timer_cambio - dt)
        movio = False
        if self._timer_cambio == 0.0:
            if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
                movio = self._mover_carril(-1)
            elif teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
                movio = self._mover_carril(+1)
        if movio:
            self._timer_cambio = self._cooldown_cambio

    def _mover_carril(self, delta):
        nuevo = self._carril + delta
        if 0 <= nuevo <= 2:
            self._carril = nuevo
            return True
        return False

    def vivo(self):
        return self._vidas > 0

    def actualizar(self, dt):
        self._tiempo_anim += dt
        if self._tiempo_anim >= self._velocidad_anim:
            self._tiempo_anim = 0.0
            self._indice_anim ^= 1
        # invulnerabilidad
        if self._invulnerable:
            self._timer_invul -= dt
            if self._timer_invul <= 0.0:
                self._invulnerable = False
        #posicionar rect
        x = self._x_positions[self._carril]
        self._rect = self._frames[self._indice_anim].get_rect(midbottom=(x, self._suelo_y))

    def dibujar(self, pantalla):
        visible = True
        if self._invulnerable:
            ticks = int(pygame.time.get_ticks() * 0.01)
            visible = (ticks % 2) == 0
        if visible:
            pantalla.blit(self._frames[self._indice_anim], self._rect)

    def colisiona_con(self, rect):
        return self._rect.colliderect(rect)



# -------PREGUNTA--------------
class Pregunta:
    def __init__(self, enunciado, valor_izq, valor_der, carril_correcto):
        # carril_correcto: "izq" | "der"
        self.enunciado = enunciado
        self.valor_izq = valor_izq
        self.valor_der = valor_der
        self.carril_correcto = carril_correcto

class GestorPreguntas:
    def __init__(self, azar=None):
        import random
        self._rnd = azar or random.Random()
        self.pregunta_actual = None

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
        self.rect = pygame.Rect(0, 0, ancho, alto)
        self.rect.centerx = x_centro
        self.rect.top = y_top
        self.color_fondo = color_fondo
        self.color_borde = color_borde
        self.fuente = fuente

    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, self.color_fondo, self.rect, border_radius=10)
        pygame.draw.rect(pantalla, self.color_borde, self.rect, width=2, border_radius=10)
        txt = self.fuente.render(str(self.valor), True, (255, 255, 255))
        pantalla.blit(txt, txt.get_rect(center=self.rect.center))

# ----------PROGRESIÓN-----------------------
class ParametrosNivel:
    def __init__(self, nivel, puntaje_minimo, velocidad_juego, intervalo_preguntas, intervalo_obstaculos, rango_operandos):
        self.nivel = nivel
        self.puntaje_minimo = puntaje_minimo
        self.velocidad_juego = velocidad_juego
        self.intervalo_preguntas = intervalo_preguntas
        self.intervalo_obstaculos = intervalo_obstaculos
        self.rango_operandos = rango_operandos

#tabla de niveles
NIVELES_PREDEF = [
    ParametrosNivel(nivel=1, puntaje_minimo=0,   velocidad_juego=5.0, intervalo_preguntas=1.8, intervalo_obstaculos=1.6, rango_operandos=(1, 10)),
    ParametrosNivel(nivel=2, puntaje_minimo=300, velocidad_juego=6.0, intervalo_preguntas=1.4, intervalo_obstaculos=1.4, rango_operandos=(1, 15)),
    ParametrosNivel(nivel=3, puntaje_minimo=700, velocidad_juego=7.0, intervalo_preguntas=1.1, intervalo_obstaculos=1.2, rango_operandos=(1, 20)),
]

class Progresion:
    def __init__(self, niveles=None):
        self.niveles = niveles if niveles is not None else NIVELES_PREDEF
        self.idx_actual = 0
        self.aplicar(self.niveles[0])

    def aplicar(self, p):
        self.nivel = p.nivel
        self.velocidad_juego = p.velocidad_juego
        self.intervalo_preguntas = p.intervalo_preguntas
        self.intervalo_obstaculos = p.intervalo_obstaculos
        self.rango_operandos = p.rango_operandos

    def actualizar_por_puntaje(self, puntaje):
        i = self.idx_actual
        n = len(self.niveles)

        while i + 1 < n and puntaje >= self.niveles[i + 1].puntaje_minimo:
            i += 1
        while i > 0 and puntaje < self.niveles[i].puntaje_minimo:
            i -= 1
        if i != self.idx_actual:
            self.idx_actual = i
            self.aplicar(self.niveles[i])
            
# ------------------------- HELPERS DE DIBUJO (HUD) -------------------------
def dibujar_vidas(pantalla, vidas, x=20, y=20, w=24, h=24, gap=8):
    import pygame
    for i in range(vidas):
        r = pygame.Rect(x + i*(w+gap), y, w, h)
        pygame.draw.rect(pantalla, (220, 60, 60), r, border_radius=6)
        pygame.draw.rect(pantalla, (120, 20, 20), r, width=2, border_radius=6)

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

#----------------------JUEGO---------------------------
class Juego:
    def __init__(self, carpeta_base: Path, ancho=1536, alto=1024, fps=60):
        #ventana fija igual al fondo
        self.ANCHO, self.ALTO, self.FPS = ancho, alto, fps

        #tamaño fijo del personaje en pantalla
        self.TAM_PERSONAJE = (128, 128)  # (ancho, alto)

        # Carriles
        self.X_IZQ  = int(self.ANCHO * 0.20)
        self.X_CEN  = int(self.ANCHO * 0.50)
        self.X_DER  = int(self.ANCHO * 0.80)
        self.CARRILES = [self.X_IZQ, self.X_CEN, self.X_DER]
        self.SUELO_Y = int(self.ALTO * 0.82)
        self.BASE = carpeta_base
        
        self.CARPETA_SPRITES = self.BASE / "Sprite"
        self.CARPETA_PERSONAJE = self.CARPETA_SPRITES / "Personaje"

        pygame.init()
        self.pantalla = pygame.display.set_mode((self.ANCHO, self.ALTO))
        pygame.display.set_caption("Juego Educativo - Carriles")
        self.reloj = pygame.time.Clock()

        #carga y entidades
        self._cargar_recursos()
        self._crear_entidades()

        # --- Math Runner state ---
        self.puntaje = 0
        self.fuente = pygame.font.SysFont(None, 48)

        self.gestor = GestorPreguntas()   # genera preguntas

        self.baldosas = []      # opciones de respuesta (izq/der)
        self.obstaculos = []    # obstáculos que caen
        self.tiempo_preguntas = 0.0
        self.tiempo_obstaculos = 0.0
        self.enunciado_actual = ""

        self.corriendo = True

    # -------recursos-------
    def _cargar_recursos(self):
        #fondo
        fondo_img = cargar_imagen(self.CARPETA_SPRITES / "fondo.png", con_alpha=False)
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
            velocidad_anim=0.12,
            invulnerabilidad=0.9,
        )
    
    def _spawn_pregunta(self):
        preg = self.gestor.siguiente_pregunta(
            operaciones=["suma", "resta", "multiplicacion"],
            rango_operandos=(1, 9)  # o self.progresion.rango_operandos
        )

        # guardar enunciado (en tu modelo es "enunciado", no "texto")
        self.enunciado_actual = getattr(preg, "enunciado", getattr(preg, "texto", ""))

        # estilos base
        color_fondo = (40, 120, 200)
        color_borde = (20, 60, 120)
        ancho, alto, y_top = 260, 70, -100

        self.baldosas = [
            BaldosaRespuesta(
                valor=preg.valor_izq,
                x_centro=self.X_IZQ,
                y_top=y_top,
                ancho=ancho,
                alto=alto,
                color_fondo=color_fondo,
                color_borde=color_borde,
                fuente=self.fuente,
            ),
            BaldosaRespuesta(
                valor=preg.valor_der,
                x_centro=self.X_DER,
                y_top=y_top,
                ancho=ancho,
                alto=alto,
                color_fondo=color_fondo,
                color_borde=color_borde,
                fuente=self.fuente,
            ),
        ]
        
    def _spawn_obstaculo(self):
        import random
        r = pygame.Rect(0, 0, 120, 50)
        r.centerx = random.choice([self.X_IZQ, self.X_CEN, self.X_DER])
        r.top = -r.height - 40
        self.obstaculos.append(r)
   
    

    # -------loop principal----------
    def run(self):
        while self.corriendo:
            dt = self.reloj.tick(self.FPS) / 1000.0
            self._eventos()
            self._actualizar(dt)
            self._dibujar()
        pygame.quit()

    # -----partes del loop---------------
    def _eventos(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.corriendo = False

    def _actualizar(self, dt: float):
        # Entrada del jugador
        teclas = pygame.key.get_pressed()
        self.jugador.manejar_entrada(teclas, dt)
        self.jugador.actualizar(dt)

        # -------------------------
        # Timers para spawners
        # -------------------------
        self.tiempo_preguntas += dt
        self.tiempo_obstaculos += dt

        # Generar una nueva pregunta (solo si no hay baldosas en pantalla)
        if self.tiempo_preguntas >= 2.2 and not self.baldosas:
            self.tiempo_preguntas = 0.0
            self._spawn_pregunta()

        # Generar un nuevo obstáculo
        if self.tiempo_obstaculos >= 1.8:
            self.tiempo_obstaculos = 0.0
            self._spawn_obstaculo()

        # -------------------------
        # Movimiento descendente
        # -------------------------
        vel = getattr(self, "velocidad_juego", 240.0)  # usa 240px/s si no tenés Progresion

        # Baldosas de respuesta
        for b in self.baldosas:
            b.rect.move_ip(0, vel * dt)
        # limpiar si salen de pantalla
        self.baldosas = [b for b in self.baldosas if b.rect.top < self.ALTO + 20]

        # Obstáculos
        for r in self.obstaculos:
            r.move_ip(0, vel * dt)
        # limpiar si salen de pantalla
        self.obstaculos = [r for r in self.obstaculos if r.top < self.ALTO + 50]

        # -------------------------
        # Colisiones
        # -------------------------
        jr = self.jugador.get_rect()

        # a) Respuestas (prioridad sobre obstáculo)
        if self.baldosas:
            tocadas = [b for b in self.baldosas if jr.colliderect(b.rect)]
            if tocadas:
                # Izq/Der por cercanía al centro del carril
                carril = (
                    "izq"
                    if abs(tocadas[0].rect.centerx - self.X_IZQ)
                    <= abs(tocadas[0].rect.centerx - self.X_DER)
                    else "der"
                )
                if self.gestor.evaluar_eleccion(carril):
                    self.puntaje += 100
                else:
                    self.jugador.perder_vida()
                # limpiar opciones y enunciado
                self.baldosas.clear()
                self.enunciado_actual = ""

        # b) Obstáculos
        for r in list(self.obstaculos):
            if jr.colliderect(r):
                self.jugador.perder_vida()
                self.obstaculos.remove(r)

        # Fondo en movimiento
        self.fondo.actualizar(dt)

    def _dibujar(self):
        # Fondo
        self.fondo.dibujar(self.pantalla)

        # Baldosas de respuesta
        for b in self.baldosas:
            b.dibujar(self.pantalla)

        # Obstáculos
        for r in self.obstaculos:
            pygame.draw.rect(self.pantalla, (200, 80, 80), r, border_radius=8)
            pygame.draw.rect(self.pantalla, (120, 30, 30), r, width=2, border_radius=8)

        # Jugador + vidas
        self.jugador.dibujar(self.pantalla)
        dibujar_vidas(self.pantalla, self.jugador.get_vidas())

        # HUD: puntaje + enunciado
        if not hasattr(self, "fuente"):
            self.fuente = pygame.font.SysFont(None, 48)

        puntos = self.fuente.render(f"Puntos: {self.puntaje}", True, (255, 255, 255))
        self.pantalla.blit(puntos, (20, 20))

        if getattr(self, "enunciado_actual", ""):
            enun = self.fuente.render(self.enunciado_actual, True, (255, 255, 0))
            enun_rect = enun.get_rect(center=(self.ANCHO // 2, int(self.ALTO * 0.10)))
            self.pantalla.blit(enun, enun_rect)

        pygame.display.flip()
