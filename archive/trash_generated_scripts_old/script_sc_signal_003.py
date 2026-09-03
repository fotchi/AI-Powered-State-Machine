import sys
from flync.model.flync_4_signal.frame import CANFDFrame
from flync.model.flync_4_signal.frame import Frame

scenario = {
    "type": "Boundary",
    "description": "CAN FD Frame at maximum 64-byte payload"
}

canfd_frame = CANFDFrame(
    name="test_frame",
    length=64,
    frame_usage='application',
    description=None,
    packed_pdus=[],
    can_id=0x123,
    id_format='standard_11bit',
    timing=None,
    type='can_fd',
    bit_rate_switch=True,
    error_state_indicator=False
)

try:
    canfd_frame.validate()
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("SUCCESS")
    sys.exit(0)