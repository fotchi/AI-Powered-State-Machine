import sys
from flync.model.flync_4_tsn.qos import TrafficClass

traffic_class = TrafficClass(
    name="TrafficClass",
    priority=3,
    maxBandwidth="100Mbps",
    burstSize=10,
)

print("SUCCESS")
sys.exit(0)