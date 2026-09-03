import sys
from flync.model.flync_4_signal.frame import Frame

try:
    frame = Frame(
        name="TestFrame",
        length=8,
        frame_usage="application",
        description="Test CAN frame",
        packed_pdus=[],
        id=0x80000000
    )
except ValueError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValueError but no error was raised")
    sys.exit(1)