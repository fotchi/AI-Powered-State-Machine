import sys
from flync.model.flync_4_communication.flync_channels import FLYNCChannelConfig

scenario = {
    'type': 'Positive',
    'description': 'Create a FLYNCChannelConfig containing a bus named "CAN1" of type CAN with a list of PDUs ["PDU1", "PDU2"] that conform to the specification.',
    'fault_injected': None,
    'expected_result': 'Validator returns success; the FLYNCChannelConfig object is instantiated without errors.'
}

channel_config = FLYNCChannelConfig(
    can_buses=[{'name': 'CAN1', 'baud_rate': 1000000}]
)

print("SUCCESS")
sys.exit(0)