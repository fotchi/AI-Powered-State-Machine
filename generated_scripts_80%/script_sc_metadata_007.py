import sys
from flync.model.flync_4_metadata.metadata import SystemMetadata
from pydantic import BaseModel, BaseVersion

system_metadata = SystemMetadata(
    type="System",
    author="N/A",
    compatible_flync_version=BaseVersion("1.0"),
    extensions=None,
    oem=None,
    platform=None,
    variant=None,
    release=BaseVersion("1.0rc1")
)

print("SUCCESS")
sys.exit(0)