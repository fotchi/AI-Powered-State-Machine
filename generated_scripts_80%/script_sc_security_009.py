import sys
from flync.model.flync_4_security.firewall import Firewall, FirewallRule
from flync.model.flync_4_security.common_validators import none_to_empty_list
from pydantic import ValidationError

firewall = Firewall(
    input_rules=[
        FirewallRule(
            name="rule1",
            action="accept",
            pattern={"type": "IP", "value": "10.0.0.1"},
            source_ip="10.0.0.1",
            destination_ip="10.0.0.2",
            source_port=1000,
            destination_port=2000,
            protocol="UDP"
        )
    ]
)

print("SUCCESS")
sys.exit(0)