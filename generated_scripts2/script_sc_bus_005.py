import sys
from flync.model.flync_4_signal.frame import Frame

frame = Frame(
    name="ExampleFrame",
    length=8,
    frame_usage="application",
    description="Example CAN frame for testing",
    packed_pdus=[]
)

print("SUCCESS")
sys.exit(0)