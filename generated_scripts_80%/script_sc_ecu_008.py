import sys
from flync.model.flync_4_ecu.can_interface import CANInterface
from pydantic import ValidationError

scenario = {
    'type': 'Negative',
    'description': 'CAN Interface with Classic CAN payload length exceeding 8 bytes'
}

try:
    can_interface = CANInterface(
        name='test_can_interface',
        bus_ref='test_bus_ref',
        sender_frames=[],
        receiver_frames=[],
        forwarder_frames=[
            {'id': 1, 'dlc': 12}  # Fault injected: size mismatch
        ]
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)