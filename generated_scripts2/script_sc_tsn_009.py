import sys
from flync.model.flync_4_tsn.qos import SingleRateTwoColorMarker

# Instantiate a SingleRateTwoColorMarker with committed_information_rate=2Mbps and peak_information_rate=5Mbps
marker = SingleRateTwoColorMarker(
    cir=2000000,
    cbs=1000000,
    eir=0,
    ebs=500000,
    coupling=False
)

print("SUCCESS")
sys.exit(0)