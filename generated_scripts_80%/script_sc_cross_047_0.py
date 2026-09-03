import sys
from flync.model.flync_4_topology.ethernet_topology import ExternalConnection
from flync.model.flync_4_security.firewall import Firewall, FirewallRule

try:
    external_connection = ExternalConnection(
        type='ecu_port_to_ecu_port',
        id='invalid_id',
        ecu1_port_name='ecu1_port',
        ecu2_port_name='ecu2_port'
    )
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)

firewall_rule = FirewallRule(
    name="Invalid Rule",
    action='reject',
    pattern={
        'source': {
            'address': '192.168.0.1'
        }
    }
)
print("SUCCESS")
sys.exit(0)