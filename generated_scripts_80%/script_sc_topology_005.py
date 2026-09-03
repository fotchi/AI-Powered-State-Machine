import sys
from pydantic import ValidationError
from flync.model.flync_4_topology.ethernet_topology import ExternalConnection

scenario = {
    'type': 'Negative',
    'faulty_value': 'non_existent_ecu'
}

try:
    obj = ExternalConnection(
        type='ecu_port_to_ecu_port',
        id='id123',
        ecu1_port_name='ecu1_port_name',
        ecu2_port_name='ecu2_port_name',
        external_connection_reference=scenario['faulty_value']
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

print("SUCCESS")
sys.exit(0)