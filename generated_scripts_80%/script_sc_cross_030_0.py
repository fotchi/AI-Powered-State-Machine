import sys
from flync.model.flync_4_ecu.port import ECUPort
from flync.model.flync_4_signal.signal import Signal, SignalDataType
from flync.model.flync_4_signal.signal_instance import SignalInstance

ecu = ECUPort(name="ECU1", mdi_config=BASET1())
signal = Signal(name="Signal1", bit_length=16, data_type=SignalDataType.UINT16)
signal_instance = SignalInstance(signal=signal, bit_position=0)

pdu = signal_instance.signal
ecuport = ecu

print("SUCCESS")
sys.exit(0)