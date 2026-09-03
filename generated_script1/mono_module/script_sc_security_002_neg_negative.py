import sys
from pydantic import ValidationError
from flync.model.flync_4_security.macsec import IntegrityWithoutConfidentiality
from flync.model.flync_4_security.macsec import MACsecConfig

try:
    macsec_config1 = MACsecConfig(
        vlan_bypass=[10],
        hello_time=10,
        bounded_hello_time=20,
        life_time=30,
        sak_retire_time=40,
        hello_time_rampup=[50],
        macsec_mode='integrity',
        kay_on=True,
        key_role='key_server_always',
        delay_protect=True,
        participant_activation='onoperup',
        macsec_mode_config=IntegrityWithoutConfidentiality()
    )

    macsec_config2 = MACsecConfig(
        vlan_bypass=[20],
        hello_time=10,
        bounded_hello_time=20,
        life_time=30,
        sak_retire_time=40,
        hello_time_rampup=[50],
        macsec_mode='integrity',
        kay_on=True,
        key_role='key_server_always',
        delay_protect=True,
        participant_activation='onoperup',
        macsec_mode_config=IntegrityWithoutConfidentiality()
    )

    macsec_config1.key_id = 2
    macsec_config2.key_id = 2

except ValidationError as e:
    print("Validation failed:", e)
    sys.exit(0)

sys.exit(1)