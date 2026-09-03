import sys

from flync.model.flync_4_ecu.controller import EthernetInterface
from flync.model.flync_4_ecu.controller import EthernetInterfaceConfig

ethernet_interface = EthernetInterface(
    name="demo_name",
    interface_config=EthernetInterfaceConfig(),
)

print("SUCCESS")
sys.exit(0)
