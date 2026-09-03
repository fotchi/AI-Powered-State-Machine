import sys
from flync.model.flync_4_security.macsec import IntegrityWithoutConfidentiality, MACsecConfig

macsec_config = MACsecConfig(
    vlan_bypass=[1],
    macsec_mode='integrity',
    kay_on=True,
    key_role='key_server_always',
    delay_protect=True,
    participant_activation='disabled',
    sci_included=False,
    cipher_preference=[]
)

print("SUCCESS")
sys.exit(0)