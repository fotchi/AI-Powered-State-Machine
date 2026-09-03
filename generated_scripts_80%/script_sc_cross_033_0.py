import sys
from flync.model.flync_4_tsn.timesync import PTPConfig, PTPPort, PTPTimeTransmitterConfig
from flync.model.flync_4_ecu.port import ECUPort
from pydantic import ValidationError

ptp_config = PTPConfig(
    ptp_ports=[
        PTPPort(
            domain_id=1,
            src_port_identity=2,
            sync_config=PTPTimeTransmitterConfig(log_tx_period=True),
            pdelay_config=None
        )
    ]
)

ecu_port = ECUPort(name='eth_tsn_0')

ptp_config_with_faulty_ecuport_reference = PTPConfig(
    ptp_ports=[
        PTPPort(
            domain_id=1,
            src_port_identity=2,
            sync_config=PTPTimeTransmitterConfig(log_tx_period=True),
            pdelay_config=None
        )
    ]
)

try:
    obj = PTPConfig(ptp_ports=[ptp_config_with_faulty_ecuport_reference])
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)