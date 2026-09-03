import sys
from flync.model.flync_4_security.macsec import IntegrityWithoutConfidentiality
from flync.model.flync_4_security.macsec import MACsecConfig

integrity_config = IntegrityWithoutConfidentiality(
    type='integrity_without_confidentiality',
    offset_preference=0
)

macsec_config = MACsecConfig(
    vlan_bypass=[100],
    hello_time=10,
    bounded_hello_time=20,
    life_time=300,
    sak_retire_time=60,
    hello_time_rampup=[10, 20, 30],
    macsec_mode='integrity',
    kay_on=True,
    key_role='key_server_always',
    delay_protect=True,
    participant_activation='onoperup',
    cipher_preference=[integrity_config]
)

print("SUCCESS")
sys.exit(0)