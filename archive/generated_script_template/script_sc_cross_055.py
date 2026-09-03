import sys

from flync.model.flync_4_topology.ethernet_topology import EthernetTopology
from flync.model.flync_4_topology.ethernet_topology import ExternalConnection
from flync.model.flync_4_tsn.timesync import PTPConfig
from flync.model.flync_4_tsn.timesync import PTPPort
from flync.model.flync_4_tsn.timesync import PTPTimeReceiverConfig
from flync.model.flync_4_tsn.timesync import PTPTimeTransmitterConfig

ethernet_topology = EthernetTopology(
    connections=[],
)
external_connection = ExternalConnection(
    id="demo_id",
    ecu1_port_name="demo_ecu1_port_name",
    ecu2_port_name="demo_ecu2_port_name",
)
ptp_config = PTPConfig(
    ptp_ports=[],
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
