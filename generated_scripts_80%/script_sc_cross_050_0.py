import sys
from flync.model.flync_4_topology.ethernet_topology import ExternalConnection
from flync.model.flync_4_signal.signal import Signal, SignalInstance

external_connection = ExternalConnection(
    type='ecu_port_to_ecu_port',
    id='ECU_PORT_TO_ECU_PORT_ID',
    ecu1_port_name='ECU1_PORT_NAME',
    ecu2_port_name='ECU2_PORT_NAME'
)

signal = Signal(
    name='SIGNAL_NAME',
    description=None,
    bit_length=16,
    data_type=SignalDataType.UINT16,
    factor=1.0,
    offset=0.0
)

signal_instance = SignalInstance(
    signal=signal
)

print("SUCCESS")
sys.exit(0)