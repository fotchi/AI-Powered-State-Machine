import sys
from flync.model.flync_4_security.macsec import MACsecConfig

# Création d'un objet MACsecConfig avec un key_id unique
macsec_config = MACsecConfig(
    vlan_bypass=[10],
    hello_time=10,
    bounded_hello_time=20,
    life_time=30,
    sak_retire_time=40,
    hello_time_rampup=[5, 10, 15],
    macsec_mode='integrity',
    kay_on=True,
    key_role='key_server_always',
    delay_protect=True,
    participant_activation='onoperup',
    sci_included=False,
    cipher_preference=MACsecConfig.default_entries_list()
)

print("SUCCESS")
sys.exit(0)