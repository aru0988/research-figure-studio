"""Repository entry point; the installed skill also contains a self-contained CLI."""
from pathlib import Path
import runpy
import sys

scripts = Path(__file__).resolve().parents[1] / "skills/research-figure-studio/scripts"
sys.path.insert(0, str(scripts))
runpy.run_path(str(scripts / "generate_demo.py"), run_name="__main__")
