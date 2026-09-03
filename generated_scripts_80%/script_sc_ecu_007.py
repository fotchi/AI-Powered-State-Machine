import sys
from pydantic import BaseModel
from flync.model.flync_4_ecu.controller import EthernetInterface, EthernetInterfaceConfig, SocketContainer
from flync.model.flync_4_ecu.config import External, OutputStrategy, NamingStrategy

class TestEthernetInterface(BaseModel):
    name: str = "Test Interface"
    interface_config: EthernetInterfaceConfig = EthernetInterfaceConfig(
        phy_address=0x01,
        speed=1000,
        duplex="full-duplex",
        mdix=True
    )
    sockets: Optional[List[SocketContainer]] = []

test_interface = TestEthernetInterface()
print("SUCCESS")
sys.exit(0)