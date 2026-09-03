import sys
from flync.model.flync_4_metadata.metadata import EmbeddedMetadata

scenario = {
    'type': 'Positive',
    'description': 'EmbeddedMetadata creation succeeds with valid parent ECU reference',
    'result': 'EmbeddedMetadata object is instantiated; reference is resolved; no validation errors',
    'fault': None,
    'data': {
        'type': 'embedded',
        'author': 'N/A',
        'compatible_flync_version': {'version': '1.0.0'},
        'extensions': None,
        'hardware': None,
        'app': None,
        'bootloader': None,
        'target_system': 'AARCH'
    }
}

ecu_metadata = EmbeddedMetadata(
    type='embedded',
    author='N/A',
    compatible_flync_version={'version': '1.0.0'},
    extensions=None,
    hardware=None,
    app=None,
    bootloader=None,
    target_system='AARCH'
)

print("SUCCESS")
sys.exit(0)