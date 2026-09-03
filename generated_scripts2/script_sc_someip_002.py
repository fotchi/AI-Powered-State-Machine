import sys
from flync.model.flync_4_someip.service_interface import SOMEIPServiceInterface

try:
    service1 = SOMEIPServiceInterface(
        name="Service1",
        id=0x2000,
        major_version=0,
        minor_version=0,
        meta=SOMEIPServiceMetadata()
    )
    service2 = SOMEIPServiceInterface(
        name="Service2",
        id=0x2000,
        major_version=0,
        minor_version=0,
        meta=SOMEIPServiceMetadata()
    )
except Exception as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)