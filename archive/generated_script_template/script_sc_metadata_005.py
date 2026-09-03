import sys

from flync.model.flync_4_metadata.metadata import EmbeddedMetadata
from flync.model.flync_4_metadata.metadata import BaseVersion

embedded_metadata = EmbeddedMetadata(
    type="demo_type",
    author="demo_author",
    compatible_flync_version=BaseVersion(version="demo_version"),
    target_system="demo_target_system",
)

print("SUCCESS")
sys.exit(0)
