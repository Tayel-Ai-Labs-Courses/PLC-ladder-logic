"""Let every example import the `plc` package when run as examples/<name>.py."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
