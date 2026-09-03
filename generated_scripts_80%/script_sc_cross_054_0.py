import sys
from flync.model.flync_4_topology.ethernet_topology import ExternalConnection
from flync.model.flync_4_tsn.timesync import PTPConfig
from flync.model.flync_4_tsn.timesync import PTPPdelayConfig
from flync.model.flync_4_tsn.timesync import PTPPort
from flync.model.flync_4_tsn.timesync import PTPTimeReceiverConfig
from flync.model.flync_4_tsn.timesync import PTPTimeTransmitterConfig

system_topology = ExternalConnection(
    type='ecu_port_to_ecu_port',
    id='connection-1',
    ecu1_port_name='Port A',
    ecu2_port_name='Port B'
)

ptp_config = PTPConfig(
    cmlds_linkport_enabled=False,
    ptp_ports=[
        PTPPort(domain_id=0, src_port_identity=1, sync_config=PTPTimeTransmitterConfig(type='time_transmitter', log_tx_period=-3)),
        PTPPort(domain_id=0, src_port_identity=2, sync_config=PTPTimeReceiverConfig(type='time_receiver', sync_timeout=10, sync_followup_timeout=20))
    ]
)

ptp_pdelay_config = PTPPdelayConfig(log_tx_period=1)

print("SUCCESS")
sys.exit(0)