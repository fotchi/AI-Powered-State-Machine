import sys

from flync.model.flync_4_bus.lin_bus import LINBus
from flync.model.flync_4_bus.lin_bus import LINScheduleTable

lin_bus = LINBus(
    name="demo_name",
    lin_protocol_version=None,
    lin_language_version=None,
    baud_rate=1,
)
lin_schedule_table = LINScheduleTable(
    name="demo_name",
)

print("SUCCESS")
sys.exit(0)
