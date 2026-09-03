import sys
from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_topology.bus_topology import CANBusTopology

# Création d'un objet CANBus avec un baud_rate valide
can_bus = CANBus(
    name="CANBus1",
    baud_rate=250000,
    description="CAN Bus for automotive communication",
    version="1.0",
    fd_enabled=False,
    fd_baud_rate=None,
    frames=[],
    state_memberships=[]
)

# Création d'un objet CANBusTopology avec un bus_type valide
can_bus_topology = CANBusTopology(
    bus_name="CANBus1",
    bus_type="can",
    attachments=[]
)

print("SUCCESS")
sys.exit(0)