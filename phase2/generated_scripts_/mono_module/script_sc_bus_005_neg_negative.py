import sys
from flync.model.flync_4_signal.frame import LINFrame
from flync.model.flync_4_bus.lin_bus import LINScheduleEntry
from pydantic import ValidationError
try:
    entry = LINScheduleEntry(frame_name='Frame_Doors', period=0)
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)