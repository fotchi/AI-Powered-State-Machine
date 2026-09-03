import sys
from flync.model.flync_4_ecu.controller import Controller
from flync.model.flync_4_ecu.port import ECUPort
from flync.model.flync_4_someip.service_interface import SOMEIPConfig
from pydantic import ValidationError

some_ip_config = SOMEIPConfig(
    version='1.0',
    sd_config=None,
    services=[],
    someip_timings=None
)

ecu_controller = Controller(
    name="InvalidECU",
    controller_metadata={"invalid": "metadata"},
    ethernet_interfaces=[]
)

try:
    ecu_port = ECUPort(name="InvalidPort", mdi_config=BASET1, mii_config=None)
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)

print("SUCCESS")