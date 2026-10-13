import sys
from flync.model.flync_4_bus.lin_bus import LINScheduleEntry, LINScheduleTable

# Création des entrées LIN
entry1 = LINScheduleEntry(frame_name="Frame_Lights", period=1.0)
entry2 = LINScheduleEntry(frame_name="Frame_Doors", period=2.0)

# Création de la table de planification LIN
schedule_table = LINScheduleTable(name="DefaultSchedule", entries=[entry1, entry2])

print("SUCCESS")
sys.exit(0)