import sys
from pydantic import ValidationError
from flync.model.flync_4_ecu.port import ECUPort

try:
    ecu_port1 = ECUPort(name='portA', mdi_config=BASET1())
    ecu_port2 = ECUPort(name='portB', mdi_config=BASET1())
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)