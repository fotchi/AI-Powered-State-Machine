import sys
from flync.model.flync_4_tsn.timesync import PTPPort, PTPTimeTransmitterConfig

ptp_port = PTPPort(
    domain_id=0,
    src_port_identity=1,
    sync_config=PTPTimeTransmitterConfig(type="time_transmitter", log_tx_period=-3),
    pdelay_config=None
)

print("SUCCESS")
sys.exit(0)