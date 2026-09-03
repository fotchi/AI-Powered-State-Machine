import sys
from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_metadata.metadata import ECUMetadata

can_bus = CANBus(
    name='powertrain_can',
    baud_rate=1000000,
    fd_enabled=False,
    frames=[
        {'type': 'CANFrame', 'id': 291, 'data': [1, 2, 3]},
        {'type': 'CANFDFrame', 'id': 292, 'data': [4, 5, 6]}
    ]
)

ecu_metadata = ECUMetadata(
    type='ECU',
    author='N/A',
    compatible_flync_version='1.0.0'
)

print("SUCCESS")
sys.exit(0)