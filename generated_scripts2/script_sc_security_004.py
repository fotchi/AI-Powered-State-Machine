import sys
from flync.model.flync_4_security.macsec import MACsecConfig
from pydantic import ValidationError

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
        secure_association_key='00:11:22:33:44:55'
    )

    macsec_config2 = MACsecConfig(
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
        secure_association_key='00:11:22:33:44:55'
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