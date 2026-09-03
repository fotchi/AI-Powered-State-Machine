import sys
from flync.model.flync_4_communication.flync_channels import FLYNCChannelConfig
from flync.model.flync_4_signal.signal import SignalInstance
from pydantic import ValidationError

scenario = {
    'type': 'Negative',
    'description': 'SignalInstance Placement in FLYNCChannelConfig Classic CAN PDU Exceeds 8-Byte Payload Limit'
}

class FaultySignal(Signal):
    data_type: SignalDataType = SignalDataType.UINT64
    bit_length: int = 80

class FaultySignalInstance(SignalInstance):
    signal: Signal = FaultySignal()

try:
    channel_config = FLYNCChannelConfig(
        pdus=[
            {
                'type': 'StandardPDU',
                'name': 'pdu1',
                'bit_offset': 16,
                'signals': [
                    FaultySignalInstance()
                ]
            }
        ],
        can_buses=[]
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)