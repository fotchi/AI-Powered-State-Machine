import sys
from flync.model.flync_4_signal.frame import Frame
from pydantic import ValidationError

try:
    frames = [Frame(name="Frame1", length=10), Frame(name="Frame2", length=20)]
    schedule_table = [
        {"frame_name": "Frame3", "length": 30},
        {"frame_name": "Frame1", "length": 10}
    ]
    obj = Frame(name="Frame3", length=30)
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)