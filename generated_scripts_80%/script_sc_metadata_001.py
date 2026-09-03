import sys
from flync.model.flync_4_metadata.metadata import SystemMetadata
from pydantic import ValidationError

system_metadata = SystemMetadata(
    type="system",
    author="N/A",
    compatible_flync_version="1.0.0",
    extensions=None,
    oem=None,
    platform=None,
    variant=None,
    release="2.1.4"
)

print("SUCCESS")
sys.exit(0)