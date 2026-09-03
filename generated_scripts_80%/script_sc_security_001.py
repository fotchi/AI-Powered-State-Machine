import sys
from flync.model.flync_4_security.macsec import IntegrityWithConfidentiality, MACsecConfig

integrity_with_confidentiality = IntegrityWithConfidentiality(type='integrity_with_confidentiality')
macsec_config = MACsecConfig(
    macsec_mode='integrity_confidentiality',
    kay_on=True,
    key_role='key_server_always',
    delay_protect=True,
    participant_activation='onoperup',
    sci_included=False,
    vlan_bypass=[1],
    hello_time=10,
    bounded_hello_time=20,
    life_time=30,
    sak_retire_time=40,
    sak_rekey_time=None,
    cipher_preference=[],
    mka_enabled=True,
    hello_time_rampup=[]
)
print("SUCCESS")
sys.exit(0)