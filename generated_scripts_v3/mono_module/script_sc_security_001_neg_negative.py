import sys
from pydantic import ValidationError
from flync.model.flync_4_security.macsec import IntegrityWithConfidentiality
from flync.model.flync_4_security.macsec import MACsecConfig

try:
    macsec_config = MACsecConfig(
        vlan_bypass=[100],
        hello_time=10,
        bounded_hello_time=20,
        life_time=30,
        sak_retire_time=40,
        hello_time_rampup=[50],
        macsec_mode='integrity_with_confidentiality',
        kay_on=True,
        key_role='key_server_always',
        delay_protect=True,
        participant_activation='onoperup',
        key=[1, 2, 3, 4, 5, 6, 7, 8]  # Key length too short
    )
except ValidationError as e:
    print("Validation failed:", e)
    sys.exit(0)
else:
    sys.exit(1)