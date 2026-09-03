import sys
from flync.model.flync_4_ecu.controller import Controller
from flync.model.flync_4_ecu.port import ECUPort
from pydantic import BaseModel, Field, List, Any, EmbeddedMetadata, OutputStrategy, NamingStrategy, ImpliedStrategy

class TestECUConfig(BaseModel):
    ecu_config: Controller = Controller(
        name="Controller1",
        controller_metadata=EmbeddedMetadata(
            output_structure=OutputStrategy.SINGLE_FILE,
            naming_strategy=NamingStrategy.FIELD_NAME
        ),
        ethernet_interfaces=[EthernetInterface(name="eth0")],
        can_interfaces=[CANInterface(name="can0")]
    )
    ecu_port: ECUPort = ECUPort(
        name="ECU Port",
        mdi_config=BASET1S,
        mii_config=MII
    )

print("SUCCESS")
sys.exit(0)