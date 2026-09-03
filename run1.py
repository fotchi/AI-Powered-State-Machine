import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from flync_pipeline.agent_maitre import main

if __name__ == "__main__":
    sys.exit(main())