import sys
from flync.model.flync_4_topology.ethernet_topology import EthernetTopology, ExternalConnection

try:
    ecu1 = ExternalConnection(ipv4_address="192.168.1.1")
    ecu2 = ExternalConnection(ipv4_address="192.168.1.1")
    topology = EthernetTopology(connections=[ecu1, ecu2])
except Exception as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)