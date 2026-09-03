import sys
from flync.model.flync_4_tsn.qos import ATSInstance, SingleRateTwoColorMarker, Stream
from flync.model.flync_4_communication.flync_channels import FLYNCChannelConfig

ats_instance = ATSInstance(
    committed_information_rate=1000,
    committed_burst_size=500,
    max_residence_time=2000
)

single_rate_two_color_marker = SingleRateTwoColorMarker(
    cir=10000,
    cbs=5000,
    eir=0,
    ebs=1000,
    coupling=False
)

stream = Stream(
    name="TSN Stream",
    stream_identification=[FrameFilter("Ethernet Channel Frames")],
    policer=single_rate_two_color_marker
)

flync_channel_config = FLYNCChannelConfig(
    pdus=[
        StandardPDU(
            type="Ethernet"
        )
    ],
    can_buses=None,
    lin_buses=None,
    ethernet_pdu_containers=None
)

print("SUCCESS")
sys.exit(0)