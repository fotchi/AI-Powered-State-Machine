import sys
from pydantic import ValidationError

from flync.model.flync_4_someip.service_interface import SOMEIPConfig
from flync.model.flync_4_signal.signal import Signal
from flync.model.flync_4_signal.signal import SignalInstance
from flync.model.flync_4_someip.service_interface import SDConfig
from flync.model.flync_4_someip.service_interface import SOMEIPTimingProfile
from flync.model.flync_4_signal.signal import SignalDataType

try:
    someip_config = SOMEIPConfig(
        sd_config=SDConfig(ip_address=None, sd_timings=[]),
        services=[],
        someip_timings=SOMEIPTimingProfile(),
    )
    signal = Signal(
        name="demo_name",
        bit_length=1,
        data_type=SignalDataType.UINT8,
    )
    signal_instance = SignalInstance(
        signal=Signal(name="demo_name", bit_length=1, data_type=SignalDataType.UINT8),
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
