import sys
from flync.model.flync_4_tsn.qos import SingleRateTwoColorMarker, TrafficClass

single_rate_two_color_marker = SingleRateTwoColorMarker(
    type='single_rate_two_color',
    cir=100,
    cbs=200,
    eir=0,
    ebs=50,
    coupling=False
)

traffic_class = TrafficClass(
    name='Traffic Class 1',
    priority=3,
    frame_priority_values=[4, 5],
    internal_priority_values=[6]
)

single_rate_two_color_marker.associate_with(traffic_class)
print("SUCCESS")
sys.exit(0)