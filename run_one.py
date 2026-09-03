"""Usage: python run_one.py generated_scripts\script_sc_app_001.py"""
import subprocess, sys
from pathlib import Path

script = Path(sys.argv[1])
cache_src = Path.home() / ".flync_kb_cache" / "src"

result = subprocess.run(
    [sys.executable, str(script)],
    capture_output=True, text=True,
    env={"PYTHONPATH": str(cache_src), "PATH": __import__("os").environ.get("PATH", "")},
)
print(result.stdout)
print(result.stderr, file=sys.stderr)
print(f"exit code: {result.returncode}")