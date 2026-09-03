import sys
from flync.model.flync_4_ecu.controller import VirtualSwitch, VirtualSwitchPort

# Création d'un VirtualSwitchPort avec les attributs requis
port = VirtualSwitchPort(name="port1", node_connected="node1")

# Création d'un VirtualSwitch avec le VirtualSwitchPort
switch = VirtualSwitch(name="switch1", ports=[port], vlans=[])

print("SUCCESS")
sys.exit(0)