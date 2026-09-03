import sys
from pydantic import ValidationError

from flync.model.flync_4_security.macsec import MACsecConfig

try:
    ma_csec_config = MACsecConfig(
        vlan_bypass=[],
        hello_time=1,
        bounded_hello_time=1,
        life_time=1,
        sak_retire_time=1,
        hello_time_rampup=[],
        macsec_mode='disabled',
        kay_on=False,
        key_role='key_server_always',
        delay_protect=False,
        participant_activation='disabled',
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
