#Constantes globales del juego.
from pathlib import Path

# --- Ventanas ---
GAME_ANCHO = 1500
GAME_ALTO  = 1000
GAME_FPS   = 60

MENU_ANCHO = 1000     # tamaño del menú 
MENU_ALTO  = 800

# --- Carriles (proporciones del ancho de la ventana de juego) ---
LANE_X_LEFT   = 0.20
LANE_X_CENTER = 0.50
LANE_X_RIGHT  = 0.80
SUELO_Y_RATIO = 0.82   # altura donde se para el jugador

# --- Personaje ---
TAM_PERSONAJE            = (128, 128)
ANIM_FRAME_SECONDS       = 0.25    
INVULNERABLE_SECONDS     = 0.90
COOLDOWN_CAMBIO_SECONDS  = 0.45
VEL_HORIZONTAL_PX_S      = 350.0 

# --- Preguntas ---
OPERACIONES         = ("suma", "resta", "mul")
RANGO_OPERANDOS     = (1, 12)
PUNTAJE_CORRECTA    = 100
INTERVALO_PREGUNTAS_S = 1.8   # segundos entre preguntas (si no hay activas)

# --- Baldosas (respuestas) ---
BALDOSA_ANCHO   = 260
BALDOSA_ALTO    = 70
BALDOSA_Y_TOP_P = 0.05   # posición inicial como % del alto de la ventana

# --- Obstáculos ---
OBST_W = 120
OBST_H = 50
INTERVALO_OBSTACULOS_S = 1.6
OBST_GAP_VERTICAL_PX   = 160     # separación mínima con baldosas al spawnear

# --- Lógica de respuesta ---
ANSWER_GRACE_SECONDS = 1.0      # ventana de inmunidad tras elegir baldosa

# --- Rutas de assets ---
BASE = Path(__file__).resolve().parents[1]  # raíz del proyecto (carpeta que contiene /Sprite)
CARPETA_SPRITES    = BASE / "Sprite"
CARPETA_PERSONAJE  = CARPETA_SPRITES / "Personaje"
FONDO_FILE         = CARPETA_SPRITES / "fondo.png"


# --- Dificultad Dinamica ---
# Cada N puntos sube un "nivel".
DIFF_STEP_PUNTOS      = 500

# Velocidad de caída (px/s): base, incremento por nivel, tope
CAIDA_BASE_PX_S       = 260
CAIDA_STEP_PX_S       = 24
CAIDA_MAX_PX_S        = 520

# Intervalos entre spawns (seg): base, decremento por nivel, mínimo
PREGUNTA_BASE_S           = 2.2  # Estas serian las nuevas preguntas
PREGUNTA_STEP_S           = 0.12
PREGUNTA_MIN_S            = 1.0

OBST_BASE_S           = 1.8   # Estos serian los nuevos obstaculos
OBST_STEP_S           = 0.08
OBST_MIN_S            = 0.8

# Sonidos para el juego
VOLUMEN_SFX    = 0.7
VOLUMEN_MUSICA = 0.45

SFX_DIR  = BASE / "Sfx"
BGM_MENU = SFX_DIR / "menu.mp3"
BGM_GAME = SFX_DIR / "game.mp3"

# SFX 
SFX_CLICK = SFX_DIR / "click.ogg"
SFX_OK    = SFX_DIR / "confirmation.ogg"
SFX_BAD   = SFX_DIR / "error.ogg"
SFX_HIT   = SFX_DIR / "hit.ogg"