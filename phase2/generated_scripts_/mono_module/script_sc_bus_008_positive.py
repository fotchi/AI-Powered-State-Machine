import sys
from flync.model.flync_4_bus.lin_bus import LINBus

lin_bus = LINBus(
    name="LINBus1",
    description="LIN Bus for automotive communication",
    lin_protocol_version="2.0",
    lin_language_version="2.0",
    baud_rate=9600,
    channel_name="LIN1",
    time_base=5.0,
    jitter=0.0,
    schedule_tables=[],
    frames=[],
    state_memberships=[]
)

print("SUCCESS")
sys.exit(0)