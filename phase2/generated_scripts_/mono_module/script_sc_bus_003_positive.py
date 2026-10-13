import sys
from flync.model.flync_4_bus.lin_bus import LINBus

lin_bus = LINBus(
    name="BodyLIN",
    description="LIN Bus for body control",
    lin_protocol_version="2.0",
    lin_language_version="2.0",
    baud_rate=19200,
    channel_name="LIN1",
    time_base=5.0,
    jitter=0.0,
    schedule_tables=[],
    frames=[],
    state_memberships=[]
)

print("SUCCESS")
sys.exit(0)