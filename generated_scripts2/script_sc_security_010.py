import sys
from flync.model.flync_4_security.macsec import MACsecConfig

try:
    obj = MACsecConfig(
        vlan_bypass=[1],
        hello_time=10,
        bounded_hello_time=20,
        life_time=30,
        sak_retire_time=40,
        hello_time_rampup=[5],
        macsec_mode='disabled',
        kay_on=True,
        key_role='key_server_always',
        delay_protect=True,
        participant_activation='onoperup',
        mka_enabled=False,
        mka_handshake='malformed_or_unauthenticated'
    )
except Exception as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)