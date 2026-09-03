import sys
from flync.model.flync_4_topology.ethernet_topology import ExternalConnection, FLYNCTopology
from flync.model.flync_4_someip.service_interface import SDConfig, SDTimings, SOMEIPConfig

topology = FLYNCTopology(
    ethernet_topology=ExternalConnection(
        type='ecu_port_to_ecu_port',
        id='connection1',
        ecu1_port_name='CAN_PORT',
        ecu2_port_name='CAN_PORT'
    )
)

sd_config = SDConfig(
    ip_address='192.168.0.1',
    port=30490,
    sd_timings=[
        SDTimings(
            profile_id='profile1',
            initial_delay_min=10,
            initial_delay_max=10,
            repetitions_base_delay=30,
            repetitions_max=3,
            request_response_delay_min=10,
            request_response_delay_max=10,
            offer_cyclic_delay=None,
            offer_ttl=None,
            find_ttl=None,
            subscribe_ttl=None
        )
    ]
)

someip_config = SOMEIPConfig(
    version='1.0',
    sd_config=sd_config,
    services=[],
    someip_timings={}
)

print("SUCCESS")
sys.exit(0)