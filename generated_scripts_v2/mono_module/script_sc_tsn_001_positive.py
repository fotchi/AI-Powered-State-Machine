import sys
from flync.model.flync_4_tsn.timesync import PTPConfig

ptp_config = PTPConfig(
    cmlds_linkport_enabled=False,
    ptp_ports=[]
)

print("SUCCESS")
sys.exit(0)