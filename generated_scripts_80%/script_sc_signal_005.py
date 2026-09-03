import sys
from flync.model.flync_4_signal import Signal, ValueEncoding, SignalDataType
from flync.model.flync_4_signal.value_encoding import BitfieldGroup

signal = Signal(
    name="MySignal",
    description=None,
    bit_length=16,
    data_type=SignalDataType.UINT16,
    value_encoding=ValueEncoding.bitfield_text_table,
    bitfields=[
        BitfieldGroup(
            name='Problem',
            mask=0x00FF,
            states=[{'value': 0, 'text': 'NoProblem'}, {'value': 1, 'text': 'Minor'}, {'value': 2, 'text': 'Major'}]
        ),
        BitfieldGroup(
            name='Mode',
            mask=0xFF00,
            states=[{'value': 0x0000, 'text': 'Off'}, {'value': 0x0100, 'text': 'On'}]
        )
    ]
)

print("SUCCESS")
sys.exit(0)