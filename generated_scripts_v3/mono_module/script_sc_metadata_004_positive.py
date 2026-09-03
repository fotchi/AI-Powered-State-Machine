import sys
from flync.model.flync_4_metadata.metadata import SoftwareBaseMetadata

metadata = SoftwareBaseMetadata(version_schema='pep440', version='2.0.0rc1')
print("SUCCESS")
sys.exit(0)