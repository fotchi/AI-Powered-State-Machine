import sys
from flync.model.flync_4_metadata.metadata import ECUMetadata
from flync.model.flync_4_metadata.metadata import EmbeddedMetadata

ecu = ECUMetadata(type='ECU', author='N/A', compatible_flync_version={'major': 1, 'minor': 0})
embedded_metadata = EmbeddedMetadata(parent_ecu_id='ECU_B', type='Embedded', author='N/A', compatible_flync_version={'major': 1, 'minor': 0}, target_system='AARCH')
print("SUCCESS")
sys.exit(0)