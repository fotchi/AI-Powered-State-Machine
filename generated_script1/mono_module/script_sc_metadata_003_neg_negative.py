import sys
from flync.model.flync_4_metadata.metadata import HardwareBaseMetadata
from pydantic import ValidationError

try:
    HardwareBaseMetadata(hw_version='1.2')
except ValidationError as e:
    sys.exit(0)
sys.exit(1)