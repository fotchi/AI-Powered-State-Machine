import sys

from flync.model.flync_4_topology.ethernet_topology import EthernetTopology
from flync.model.flync_4_topology.ethernet_topology import ExternalConnection
from flync.model.flync_4_topology.ethernet_topology import FLYNCTopology
from flync.model.flync_4_someip.service_interface import SDConfig
from flync.model.flync_4_someip.service_interface import SDTimings
from flync.model.flync_4_someip.service_interface import SOMEIPConfig
from flync.model.flync_4_someip.service_interface import SOMEIPTimingProfile

ethernet_topology = EthernetTopology(
    connections=[],
)
external_connection = ExternalConnection(
    id="demo_id",
    ecu1_port_name="demo_ecu1_port_name",
    ecu2_port_name="demo_ecu2_port_name",
)
flync_topology = FLYNCTopology(
)
sd_config = SDConfig(
    ip_address=None,
    sd_timings=[],
)
sd_timings = SDTimings(
    profile_id="demo_profile_id",
)
someip_config = SOMEIPConfig(
    sd_config=SDConfig(ip_address=None, sd_timings=[]),
    services=[],
    someip_timings=SOMEIPTimingProfile(),
)

print("SUCCESS")
sys.exit(0)
