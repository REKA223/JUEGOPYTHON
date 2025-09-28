"""Lógica de generación y validación de preguntas.

Define el modelo de una pregunta y un gestor que crea preguntas aritméticas
según un conjunto de operaciones y un rango de operandos. También provee
la evaluación de la elección del jugador (izq/der).
"""

import random
from dataclasses import dataclass

@dataclass
class Pregunta:
    enunciado: str
    valor_izq: int
    valor_der: int
    carril_correcto: str  # "izq" o "der"

class GestorPreguntas:
    def __init__(self, operaciones=("suma", "resta", "mul"), rango=(1, 12)):
        self.operaciones = tuple(operaciones) if operaciones else ("suma",)
        self.rango = rango
        self.pregunta_actual: Pregunta | None = None
        self._rnd = random.Random()

    def _operacion(self, op: str, a: int, b: int) -> tuple[str, int]:
        if op == "suma":
            res = a + b; txt = f"{a} + {b} = ?"
        elif op == "resta":
            if b > a: a, b = b, a
            res = a - b; txt = f"{a} - {b} = ?"
        else:  # "mul"
            res = a * b; txt = f"{a} × {b} = ?"
        return txt, res

    def _distractor(self, correcto: int) -> int:
        for _ in range(12):
            delta = self._rnd.choice([-4,-3,-2,-1,1,2,3,4,5])
            alt = correcto + delta
            if alt != correcto and alt >= 0:
                return alt
        return correcto + 1


    def siguiente_pregunta(self, operaciones=None, rango_operandos=None):
        ops = tuple(operaciones) if operaciones else self.operaciones
        lo, hi = rango_operandos if rango_operandos else self.rango
    


        a = self._rnd.randint(lo, hi)
        b = self._rnd.randint(lo, hi)
        op = self._rnd.choice(ops)

        enunciado, correcto = self._operacion(op, a, b)
        distractor = self._distractor(correcto)

        if self._rnd.random() < 0.5:
            p = Pregunta(enunciado, correcto, distractor, "izq")
        else:
            p = Pregunta(enunciado, distractor, correcto, "der")

        self.pregunta_actual = p
        return p

    def evaluar_eleccion(self, carril: str) -> bool:
        return bool(self.pregunta_actual and carril == self.pregunta_actual.carril_correcto)


