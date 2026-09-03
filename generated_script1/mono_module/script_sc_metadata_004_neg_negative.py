import sys
from flync.model.flync_4_metadata.metadata import SoftwareBaseMetadata
from pydantic import ValidationError

try:
    metadata = SoftwareBaseMetadata(sw_version='2.0.0-rc')
except ValidationError:
    sys.exit(0)

sys.exit(1)