#Main.py
# Main.py
from pathlib import Path
import sys
from lib.Core import Juego

BASE = Path(__file__).parent.resolve()
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

if __name__ == "__main__":
    Juego(BASE).run()
