from pathlib import Path
import pygame

from pathlib import Path
import pygame

_almacen = {}

def cargar_imagen(ruta, con_alpha=True):
    p = Path(ruta)
    clave = (p.resolve(), con_alpha)
    if clave in _almacen:
        return _almacen[clave]
    if not p.exists():
        raise FileNotFoundError(f"No existe la imagen: {p}")
    img = pygame.image.load(str(p))
    surf = img.convert_alpha() if con_alpha else img.convert()
    _almacen[clave] = surf
    return surf

def escalar_a_tamaño(superficie, ancho_destino, alto_destino):
    """Escala a un tamaño exacto (sin mantener proporción)."""
    return pygame.transform.smoothscale(superficie, (int(ancho_destino), int(alto_destino)))


def escalar_por_altura(superficie, altura_destino):
    #Escala manteniendo proporción para que la altura sea 'altura_destino
    ancho, alto = superficie.get_size()
    factor = altura_destino / float(alto)
    nuevo_tamaño = (int(ancho * factor), int(alto * factor))
    return pygame.transform.smoothscale(superficie, nuevo_tamaño)

def escalar_por_ancho(superficie, ancho_destino):
    #Escala manteniendo proporción para que el ancho sea 'ancho_destino'
    ancho, alto = superficie.get_size()
    factor = ancho_destino / float(ancho)
    nuevo_tamaño = (int(ancho * factor), int(alto * factor))
    return pygame.transform.smoothscale(superficie, nuevo_tamaño)

def ajustar_a(superficie, max_ancho, max_alto):
    #Ajusta la imagen para que quepa dentro de (max_ancho x max_alto) manteniendo proporción
    ancho, alto = superficie.get_size()
    factor = min(max_ancho / float(ancho), max_alto / float(alto))
    nuevo_tamaño = (int(ancho * factor), int(alto * factor))
    return pygame.transform.smoothscale(superficie, nuevo_tamaño)


