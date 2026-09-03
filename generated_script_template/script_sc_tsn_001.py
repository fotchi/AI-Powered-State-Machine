import sys

from flync.model.flync_4_tsn.timesync import PTPConfig
from flync.model.flync_4_tsn.timesync import PTPTimeReceiverConfig
from flync.model.flync_4_tsn.timesync import PTPTimeTransmitterConfig

ptp_config = PTPConfig(
    ptp_ports=[],
)
ptp_time_receiver_config = PTPTimeReceiverConfig(
    sync_timeout=1,
    sync_followup_timeout=1,
)
ptp_time_transmitter_config = PTPTimeTransmitterConfig(
    log_tx_period=1,
)

print("SUCCESS")
sys.exit(0)
