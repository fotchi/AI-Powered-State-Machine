import sys
from flync.model.flync_4_someip.service_interface import SOMEIPConfig
from flync.model.flync_4_signal.signal import Signal, SignalDataType
from pydantic import ValidationError

someip_config = SOMEIPConfig(
    version='1.0',
    sd_config=None,
    services=[],
    someip_timings=None
)

signal_data_type = SignalDataType.BYTEARRAY
signal = Signal(
    name="test_signal",
    description=None,
    bit_length=8,
    data_type=signal_data_type,
    factor=1.0,
    offset=0.0,
    lower_limit=None,
    upper_limit=None,
    unit=None,
    initial_value=b'\x00' * 2048, # 2048 bytes
    value_encoding=None
)

signal_instance = SignalInstance(
    signal=signal,
    bit_position=None,
    update_indication_bit_position=None,
    endianness='LE'
)

try:
    obj = SOMEIPConfig(
        version='1.0',
        sd_config=None,
        services=[],
        someip_timings=None
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)