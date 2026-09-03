import sys
from flync.model.flync_4_signal.frame import Frame
from pydantic import ValidationError

try:
    frame = Frame(
        name="CAN Bus Frame",
        length=8,
        frame_usage="application",
        description="CAN Bus Frame with ID Exceeding Standard/Extended Limits",
        packed_pdus=[],
        id=0x80000000
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)