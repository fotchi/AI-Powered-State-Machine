import sys
from pydantic import ValidationError
from flync import SystemTopology, ECU

scenario = {
    "type": "Negative",
    "description": "Duplicate IPv6 Address in SystemTopology"
}

system_topology = SystemTopology(
    name="System Topology",
    description="Test system topology",
    ecus=[
        ECU(name="ECU 1", ip_address="2001:0db8:85a3:0000:0000:8a2e:0370:7334"),
        ECU(name="ECU 2", ip_address="2001:0db8:85a3:0000:0000:8a2e:0370:7334")
    ]
)

try:
    system_topology.validate()
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)