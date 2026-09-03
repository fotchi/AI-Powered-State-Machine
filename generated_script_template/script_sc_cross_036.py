import sys
from pydantic import ValidationError

from flync.model.flync_4_metadata.metadata import ECUMetadata
from flync.model.flync_4_security.firewall import FirewallRule
from flync.model.flync_4_metadata.metadata import BaseVersion
from flync.model.flync_4_tsn.qos import FrameFilter

try:
    ecu_metadata = ECUMetadata(
        type="demo_type",
        author="demo_author",
        compatible_flync_version=BaseVersion(version="demo_version"),
    )
    firewall_rule = FirewallRule(
        name="demo_name",
        action='reject',
        pattern=FrameFilter(),
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
