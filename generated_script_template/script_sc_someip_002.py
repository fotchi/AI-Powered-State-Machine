import sys
from pydantic import ValidationError

from flync.model.flync_4_someip.service_interface import SOMEIPServiceInterface
from flync.model.flync_4_metadata.metadata import BaseVersion
from flync.model.flync_4_metadata.metadata import SOMEIPServiceMetadata

try:
    someip_service_interface = SOMEIPServiceInterface(
        name="demo_name",
        id=1,
        meta=SOMEIPServiceMetadata(type="demo_type", author="demo_author", compatible_flync_version=BaseVersion(version="demo_version")),
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
