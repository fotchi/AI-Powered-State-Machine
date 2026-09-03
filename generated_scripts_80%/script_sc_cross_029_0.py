import sys
from flync.model.flync_4_security.firewall import Firewall, FirewallRule
from flync.model.flync_4_ecu.port import ECUPort
from pydantic import ValidationError

scenario = {
    "type": "Negative",
    "description": "FirewallRule References Non-Existent ECUPort Identifier"
}

firewall_rule = FirewallRule(
    name="Invalid Rule",
    action="reject",
    pattern=FrameFilter(
        src_mac="00:11:22:33:44:55",
        dst_mac="66:77:88:99:AA:BB",
        ethertype="0x0806"
    )
)

firewall = Firewall(
    input_rules=[firewall_rule],
    output_rules=[]
)

ecu_port = ECUPort(name="Invalid Port")

try:
    firewall_rule.target_interface = ecu_port
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)