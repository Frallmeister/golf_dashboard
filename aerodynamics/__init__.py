import sys
from pathlib import Path

BASE_DIR = str(Path('.').parent.resolve())
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)