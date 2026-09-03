import sys
from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_signal.frame import CANFDFrame

# Création d'une instance de CANFDFrame
can_fd_frame = CANFDFrame(
    name="CANFDFrame1",
    length=64,
    can_id=0x123,
    id_format="standard_11bit",
    packed_pdus=[],
    timing=None
)

# Création d'une instance de CANBus et configuration de son champ frames
can_bus = CANBus(
    name="CANBus1",
    baud_rate=500000,
    fd_enabled=True,
    fd_baud_rate=2000000,
    frames=[can_fd_frame]
)

print("SUCCESS")
sys.exit(0)