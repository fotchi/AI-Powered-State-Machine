import sys
from flync.model.flync_4_bus.lin_bus import LINBus

lin_bus = LINBus(
    name="LIN Slave Node",
    lin_protocol_version="1.3",
    lin_language_version="1.3",
    baud_rate=19200,
    channel_name="CAN Channel 1",
    time_base=5.0,
    jitter=0.0,
    schedule_tables=[],
    frames=[],
    state_memberships=[]
)

print("SUCCESS")
sys.exit(0)