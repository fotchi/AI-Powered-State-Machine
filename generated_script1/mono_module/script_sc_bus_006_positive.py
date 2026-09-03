import sys
from flync.model.flync_4_signal.frame import LINFrame
from flync.model.flync_4_bus.lin_bus import LINScheduleEntry

# Création d'un objet LINFrame
frame_lights = LINFrame(
    name="Frame_Lights",
    length=8,
    lin_id=10
)

# Création d'un objet LINScheduleEntry avec les paramètres de timing valides
schedule_entry = LINScheduleEntry(
    frame_name="Frame_Lights",
    period=1.5
)

print("SUCCESS")
sys.exit(0)