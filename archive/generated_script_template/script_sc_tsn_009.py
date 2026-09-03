import sys

from flync.model.flync_4_tsn.qos import SingleRateTwoColorMarker

single_rate_two_color_marker = SingleRateTwoColorMarker(
    cir=1,
    cbs=1,
    eir=0,
    ebs=1,
    coupling=False,
)

print("SUCCESS")
sys.exit(0)
