# lib/Core.py
import pygame

# ------------------------- JUGADOR -------------------------
class Jugador:
    """
    Animación de 2 cuadros SIEMPRE activa (corre en el lugar).
    Las flechas ←/→ mueven la X, pero la animación no depende de eso.
    """
    def __init__(self, frames, x, suelo_y, velocidad=320.0, velocidad_anim=0.14, x_min=30, x_max=930):
        assert len(frames) >= 2, "Se esperan al menos 2 frames para animar"
        self.frames = frames
        self.x = x
        self.suelo_y = suelo_y
        self.velocidad = velocidad
        self.velocidad_anim = velocidad_anim
        self.x_min = x_min
        self.x_max = x_max

        self.indice_anim = 0
        self.tiempo_anim = 0.0
        self.rect = self.frames[0].get_rect(midbottom=(self.x, self.suelo_y))
 #--- Comportamientos--
    def manejar_entrada(self, teclas, dt):
        dx = 0.0
        if teclas[pygame.K_LEFT]:
            dx -= self.velocidad * dt
        if teclas[pygame.K_RIGHT]:
            dx += self.velocidad * dt
        if dx:
            self.x = max(self.x_min, min(self.x_max, self.x + dx))

    def actualizar(self, dt):
        self.tiempo_anim += dt
        if self.tiempo_anim >= self.velocidad_anim:
            self.tiempo_anim = 0.0
            self.indice_anim ^= 1
        self.rect = self.frames[self.indice_anim].get_rect(midbottom=(self.x, self.suelo_y))

    def dibujar(self, pantalla):
        pantalla.blit(self.frames[self.indice_anim], self.rect)


# -------PREGUNTA------------------
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
    """
    Elige el nivel según puntaje y expone parámetros:
    - nivel, velocidad_juego, intervalo_preguntas, intervalo_obstaculos, rango_operandos
    """
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
            
