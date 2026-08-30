import sys
from pydantic import ValidationError
from flync.model.flync_4_metadata.metadata import HardwareBaseMetadata

try:
    HardwareBaseMetadata(version='1.2')
except ValidationError as e:
    sys.exit(0)

sys.exit(1)