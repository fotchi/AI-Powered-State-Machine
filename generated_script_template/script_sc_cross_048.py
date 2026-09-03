import sys
from pydantic import ValidationError

from flync.model.flync_4_topology.ethernet_topology import EthernetTopology
from flync.model.flync_4_topology.ethernet_topology import ExternalConnection
from flync.model.flync_4_security.firewall import Firewall
from flync.model.flync_4_security.firewall import FirewallRule
from flync.model.flync_4_tsn.qos import FrameFilter

try:
    ethernet_topology = EthernetTopology(
        connections=[],
    )
    external_connection = ExternalConnection(
        id="demo_id",
        ecu1_port_name="demo_ecu1_port_name",
        ecu2_port_name="demo_ecu2_port_name",
    )
    firewall = Firewall(
    )
    firewall_rule = FirewallRule(
        name="demo_name",
        action='reject',
        pattern=FrameFilter(),
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
