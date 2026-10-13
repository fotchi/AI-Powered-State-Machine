import sys
from flync.model.flync_4_signal.frame import LINFrame
from flync.model.flync_4_bus.lin_bus import LINScheduleEntry

# Création de l'objet LINFrame
frame_lights = LINFrame(
    name="Frame_Lights",
    length=8,
    lin_id=10
)

# Création de l'objet LINScheduleEntry
schedule_entry = LINScheduleEntry(
    frame_name="Frame_Lights",
    period=150.0
)

print("SUCCESS")
sys.exit(0)