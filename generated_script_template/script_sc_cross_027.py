import sys

from flync.model.flync_4_communication.flync_channels import FLYNCChannelConfig
from flync.model.flync_4_tsn.timesync import PTPConfig
from flync.model.flync_4_tsn.timesync import PTPPdelayConfig
from flync.model.flync_4_tsn.timesync import PTPPort
from flync.model.flync_4_tsn.timesync import PTPTimeReceiverConfig
from flync.model.flync_4_tsn.timesync import PTPTimeTransmitterConfig

flync_channel_config = FLYNCChannelConfig(
)
ptp_config = PTPConfig(
    ptp_ports=[],
)
ptp_pdelay_config = PTPPdelayConfig(
    log_tx_period=1,
)
ptp_port = PTPPort(
    domain_id=1,
    src_port_identity=1,
    sync_config=None,
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
