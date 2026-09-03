import sys

from flync.model.flync_4_tsn.qos import ATSInstance
from flync.model.flync_4_signal.frame import Frame
from flync.model.flync_4_tsn.qos import FrameFilter
from flync.model.flync_4_tsn.qos import SingleRateTwoColorMarker
from flync.model.flync_4_tsn.qos import Stream

ats_instance = ATSInstance(
    committed_information_rate=1,
    committed_burst_size=1,
    max_residence_time=1,
)
frame = Frame(
    name="demo_name",
    length=1,
)
frame_filter = FrameFilter(
)
single_rate_two_color_marker = SingleRateTwoColorMarker(
    cir=1,
    cbs=1,
    eir=0,
    ebs=1,
    coupling=False,
)
stream = Stream(
    name="demo_name",
    stream_identification=[],
)

print("SUCCESS")
sys.exit(0)
