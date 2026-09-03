import sys
from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_communication.flync_channels import FLYNCChannelConfig
from flync.model.flync_4_bus.lin_bus import LINBus

# Création d'une instance de CANBus
can_bus = CANBus(
    name="CANBus1",
    baud_rate=500000,
    fd_enabled=False,
    fd_baud_rate=None,
    frames=[],
    state_memberships=[]
)

# Création d'une instance de LINBus
lin_bus = LINBus(
    name="LINBus1",
    lin_protocol_version="2.0",
    lin_language_version="2.0",
    baud_rate=19200,
    channel_name=None,
    time_base=5.0,
    jitter=0.0,
    schedule_tables=[],
    frames=[],
    state_memberships=[]
)

# Création d'une instance de FLYNCChannelConfig avec des références aux instances de CANBus et LINBus
flync_channel_config = FLYNCChannelConfig(
    can_buses=[can_bus],
    lin_buses=[lin_bus]
)

print("SUCCESS")
sys.exit(0)