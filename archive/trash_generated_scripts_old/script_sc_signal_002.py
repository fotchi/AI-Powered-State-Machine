import sys
from flync.model.flync_4_signal.frame import CANFrame
from flync.model.flync_4_signal.pdu import StandardPDU

scenario = {
    "type": "Negative",
    "description": "CAN Frame DLC smaller than referenced PDU"
}

try:
    can_frame = CANFrame(
        name="test_can_frame",
        length=8,
        frame_usage='application',
        description=None,
        packed_pdus=[],
        can_id=0x123,
        id_format='standard_11bit',
        timing=None,
        type='can',
        is_remote_frame=False
    )
    
    standard_pdu = StandardPDU(
        name="test_standard_pdu",
        length=4,  # DLC smaller than referenced PDU
        pdu_usage='application',
        description=None,
        type='standard',
        signals=[],
        signal_groups=[]
    )

except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)