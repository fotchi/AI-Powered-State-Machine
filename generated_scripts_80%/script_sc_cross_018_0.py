import sys
from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_tsn.qos import FrameFilter, SingleRateTwoColorMarker, Stream

canbus = CANBus(
    name="CANBus",
    baud_rate=1000000,
    fd_enabled=False,
    frames=[
        {"type": "CANFrame", "id": 1, "data": [1, 2, 3]},
        {"type": "CANFDFrame", "id": 2, "data": [4, 5, 6]}
    ]
)

stream = Stream(
    name="Stream",
    stream_identification=[
        FrameFilter(
            ethertype=[0x0800],
            src_mac=["00:11:22:33:44:55"],
            dst_mac=["00:66:77:88:99:AA"]
        )
    ],
    policer=SingleRateTwoColorMarker(
        type="single_rate_two_color",
        cir=100000,
        cbs=200000,
        eir=0,
        ebs=300000,
        coupling=False
    )
)

print("SUCCESS")
sys.exit(0)