import sys
from pydantic import ValidationError

from flync.model.flync_4_security.firewall import FirewallRule
from flync.model.flync_4_signal.signal import Signal
from flync.model.flync_4_tsn.qos import FrameFilter
from flync.model.flync_4_signal.signal import SignalDataType

try:
    firewall_rule = FirewallRule(
        name="demo_name",
        action='reject',
        pattern=FrameFilter(),
    )
    signal = Signal(
        name="demo_name",
        bit_length=1,
        data_type=SignalDataType.UINT8,
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
