import sys

from flync.model.flync_4_security.macsec import IntegrityWithConfidentiality
from flync.model.flync_4_security.macsec import MACsecConfig

integrity_with_confidentiality = IntegrityWithConfidentiality(
)
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

print("SUCCESS")
sys.exit(0)
