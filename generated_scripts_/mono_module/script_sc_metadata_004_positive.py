import sys
from flync.model.flync_4_metadata.metadata import SoftwareBaseMetadata

software_metadata = SoftwareBaseMetadata(version='2.0.0rc1', version_schema='pep440')
print("SUCCESS")
sys.exit(0)