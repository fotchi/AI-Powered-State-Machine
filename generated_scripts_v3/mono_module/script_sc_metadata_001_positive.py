import sys
from flync.model.flync_4_metadata.metadata import BaseMetadata, SystemMetadata, BaseVersion

# Création d'un objet SystemMetadata avec les champs obligatoires
system_metadata = SystemMetadata(
    type="system",
    author="N/A",
    compatible_flync_version=BaseVersion(version="1.0.0"),
    release=BaseVersion(version="1.0.0")
)

print("SUCCESS")
sys.exit(0)