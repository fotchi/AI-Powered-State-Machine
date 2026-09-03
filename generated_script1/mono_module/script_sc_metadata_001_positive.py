import sys

from flync.model.flync_4_metadata.metadata import BaseMetadata
from flync.model.flync_4_metadata.metadata import SystemMetadata
from flync.model.flync_4_metadata.metadata import BaseVersion

base_metadata = BaseMetadata(
    type="demo_type",
    author="demo_author",
    compatible_flync_version=BaseVersion(version="demo_version"),
)
system_metadata = SystemMetadata(
    type="demo_type",
    author="demo_author",
    compatible_flync_version=BaseVersion(version="demo_version"),
    release=BaseVersion(version="demo_version"),
)

print("SUCCESS")
sys.exit(0)
