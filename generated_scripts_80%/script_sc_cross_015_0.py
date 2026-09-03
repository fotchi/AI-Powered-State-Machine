import sys
from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_signal.frame import Frame, PDUInstance
from flync.model.flync_4_signal.signal import Signal, SignalDataType, ValueEncoding

try:
    pdu = PDUInstance(
        name="pdu",
        length=16,
        packed_signals=[
            SignalInstance(
                signal=Signal(
                    name="signal",
                    data_type=SignalDataType.BYTEARRAY,
                    bit_length=8,
                    size=16
                )
            )
        ]
    )

    pdu_ref = PDUInstance(
        name="pdu_ref",
        length=16,
        packed_signals=[
            SignalInstance(
                signal=pdu.packed_signals[0].signal
            )
        ]
    )

    frame = Frame(
        name="frame",
        length=8,
        pdu_ref=pdu_ref
    )

    can_bus = CANBus(
        name="can_bus",
        baud_rate=1000000,
        frames=[frame]
    )

except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)