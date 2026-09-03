import sys

from flync.model.flync_4_signal.frame import CANFrame
from flync.model.flync_4_signal.frame import Frame
from flync.model.flync_4_signal.pdu import StandardPDU

can_frame = CANFrame(
    name="demo_name",
    length=1,
    can_id=1,
    id_format='standard_11bit',
)
frame = Frame(
    name="demo_name",
    length=1,
)
standard_pdu = StandardPDU(
    name="demo_name",
    length=1,
)

print("SUCCESS")
sys.exit(0)
