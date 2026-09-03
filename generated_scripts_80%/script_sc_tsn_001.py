import sys
from flync.model.flync_4_tsn.timesync import PTPConfig
from flync.model.flync_4_tsn.timesync import PTPTimeReceiverConfig
from flync.model.flync_4_tsn.timesync import PTPTimeTransmitterConfig

ptp_config = PTPConfig(
    ptp_ports=[
        PTPPort(domain_id=1, src_port_identity=2, sync_config={"syncInterval": 1}),
        PTPPort(domain_id=3, src_port_identity=4, sync_config={"announceInterval": 2})
    ]
)

print("SUCCESS")
sys.exit(0)