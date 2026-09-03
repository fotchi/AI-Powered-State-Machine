import sys
from flync.model.flync_4_security.macsec import IntegrityWithConfidentiality, MACsecConfig
from pydantic import ValidationError

scenario = {
    'type': 'Negative',
    'description': 'MACsecConfig referencing a non-existent Integrity mode'
}

try:
    macsec_config = MACsecConfig(
        vlan_bypass=[1],
        mka_enabled=True,
        hello_time=10,
        bounded_hello_time=20,
        life_time=30,
        sak_retire_time=40,
        hello_time_rampup=[50, 60],
        sak_rekey_time=None,
        macsec_mode='integrity',
        kay_on=True,
        key_role='key_server_always',
        delay_protect=True,
        participant_activation='onoperup',
        sci_included=False,
        cipher_preference=MACsecConfig.default_entries_list(),
        integrity_mode='non_existent_mode'
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)