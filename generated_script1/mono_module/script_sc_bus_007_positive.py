import sys
from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_topology.bus_topology import CANBusTopology

# Création d'un CANBus avec un baud_rate valide
can_bus = CANBus(
    name="CANBus1",
    baud_rate=250000,
    description="CAN Bus for automotive communication",
    version="1.0",
    fd_enabled=False,
    frames=[],
    state_memberships=[]
)

# Création d'un CANBusTopology avec le CANBus valide
can_bus_topology = CANBusTopology(
    bus_name="CANBus1",
    bus_type="can",
    attachments=[]
)

print("SUCCESS")
sys.exit(0)