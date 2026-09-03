import sys
from flync.model.flync_4_signal.frame import Frame

frame = Frame(
    name="CAN Bus Frame",
    length=8,
    frame_usage="application",
    description="CAN Bus Frame with standard ID and payload",
    packed_pdus=[]
)

print("SUCCESS")
sys.exit(0)