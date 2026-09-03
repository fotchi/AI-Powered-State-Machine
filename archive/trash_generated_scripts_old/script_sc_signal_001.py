import sys
from flync.model.flync_4_signal.frame import CANFrame
from flync.model.flync_4_signal.pdu import StandardPDU

scenario = {
    "type": "Positive",
    "description": "Valid CAN Frame with matching PDU size"
}

can_frame = CANFrame(
    name="CAN Frame 1",
    length=8,
    can_id=0x123,
    id_format="standard_11bit",
    type="can",
    is_remote_frame=False
)

pdu = StandardPDU(
    name="Standard PDU 1",
    length=8,
    pdu_usage=None,
    description=None,
    type="standard"
)

print("SUCCESS")
sys.exit(0)