import sys
from flync.model.flync_4_security.firewall import FirewallRule
from flync.model.flync_4_signal.signal import Signal, ValueEncoding, SignalDataType

try:
    firewall_rule = FirewallRule(
        name="test",
        action="reject",
        pattern=FrameFilter(
            field="field1",
            operator="eq",
            value=b"123"
        ),
        signal=Signal(
            name="test_signal",
            description=None,
            bit_length=8,
            data_type=SignalDataType.BYTEARRAY,
            factor=2.0,
            offset=3.0
        )
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)