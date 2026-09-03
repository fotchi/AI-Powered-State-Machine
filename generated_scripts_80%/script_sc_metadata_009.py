import sys
from flync.model.flync_4_metadata.metadata import BaseMetadata
from pydantic import BaseModel as _BaseModel, Field

class BaseVersion(BaseModel):
    major: int = Field(..., ge=0)
    minor: int = Field(..., ge=0)
    patch: int = Field(..., ge=0)

base_metadata = BaseMetadata(
    type="metadata",
    author="N/A",
    compatible_flync_version=BaseVersion(major=1, minor=0, patch=0),
    extensions=None
)
print("SUCCESS")
sys.exit(0)