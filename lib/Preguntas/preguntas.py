# lib/preguntas.py (o dentro de Core si preferís)
import random
from dataclasses import dataclass

@dataclass
class Pregunta:
    texto: str
    valor_izq: int
    valor_der: int
    carril_correcto: str  # "izq" | "der"

class GestorPreguntas:
    def __init__(self):
        self._ultima = None

    def _operacion(self, op, a, b):
        if op == "suma": return a + b
        if op == "resta": return a - b
        if op == "multiplicacion": return a * b
        return a + b

    def _distractor(self, correcto, rango):
        # genera un número distinto al correcto, pero cercano/creíble
        a, b = rango
        for _ in range(10):
            alt = correcto + random.choice([-3,-2,-1,1,2,3,4])
            if alt != correcto and a*b-10 <= alt <= a*b+10:  # ventana laxa
                return alt
        # fallback: algo al azar que no sea correcto
        alt = correcto
        while alt == correcto:
            alt = random.randint(a, b) + random.randint(a, b)
        return alt

    def siguiente_pregunta(self, operaciones, rango_operandos):
        a = random.randint(*rango_operandos)
        b = random.randint(*rango_operandos)
        op = random.choice(operaciones)
        correcto = self._operacion(op, a, b)

        texto = f"{a} {'+' if op=='suma' else '-' if op=='resta' else '×'} {b} = ?"
        distractor = self._distractor(correcto, rango_operandos)

        if random.random() < 0.5:
            p = Pregunta(texto, correcto, distractor, "izq")
        else:
            p = Pregunta(texto, distractor, correcto, "der")

        self._ultima = p
        return p

    def evaluar_eleccion(self, carril_elegido):
        return self._ultima and (carril_elegido == self._ultima.carril_correcto)
