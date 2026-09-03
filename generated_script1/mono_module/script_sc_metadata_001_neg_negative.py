import sys
from flync.model.flync_4_metadata.metadata import SystemMetadata, BaseVersion
from pydantic import ValidationError

try:
    system_metadata1 = SystemMetadata(
        type="System",
        author="N/A",
        compatible_flync_version=BaseVersion(major=1, minor=0, patch=0),
        release=BaseVersion(major=1, minor=0, patch=0),
        name="VehicleSystemA"
    )
    system_metadata2 = SystemMetadata(
        type="System",
        author="N/A",
        compatible_flync_version=BaseVersion(major=1, minor=0, patch=0),
        release=BaseVersion(major=1, minor=0, patch=0),
        name="VehicleSystemA"
    )
except ValidationError as e:
    sys.exit(0)
else:
    sys.exit(1)