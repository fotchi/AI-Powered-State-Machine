import sys
from flync.model.flync_4_bus.lin_bus import LINScheduleEntry, LINScheduleTable

frame_lights_entry = LINScheduleEntry(frame_name="Frame_Lights", period=1.0)
frame_doors_entry = LINScheduleEntry(frame_name="Frame_Doors", period=2.0)

schedule_table = LINScheduleTable(name="DefaultSchedule", entries=[frame_lights_entry, frame_doors_entry])

print("SUCCESS")
sys.exit(0)