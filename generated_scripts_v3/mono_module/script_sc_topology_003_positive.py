import sys
from flync.model.flync_4_topology.bus_topology import CANBusTopology

# Création d'un CANBusTopology avec les champs obligatoires et les attachments
can_bus_topology = CANBusTopology(
    bus_name="CAN_1",
    bus_type="can",
    attachments=[
        {"controller_name": "controller_A", "interface_name": "interface_A", "role": "can_node", "ecu_name": "ECU_A"},
        {"controller_name": "controller_B", "interface_name": "interface_B", "role": "can_node", "ecu_name": "ECU_B"},
        {"controller_name": "controller_C", "interface_name": "interface_C", "role": "can_node", "ecu_name": "ECU_C"}
    ]
)

print("SUCCESS")
sys.exit(0)