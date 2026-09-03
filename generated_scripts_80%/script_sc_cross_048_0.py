import sys
from flync.model.flync_4_security.macsec import IntegrityWithConfidentiality
from flync.model.flync_4_security.macsec import MACsecConfig
from flync.model.flync_4_tsn.timesync import PTPConfig
from flync.model.flync_4_tsn.timesync import PTPPort
from flync.model.flync_4_tsn.timesync import PTPTimeTransmitterConfig

macsec_config = MACsecConfig(
    vlan_bypass=[1],
    mka_enabled=True,
    hello_time=10,
    bounded_hello_time=20,
    life_time=30,
    sak_retire_time=40,
    hello_time_rampup=[50, 60],
    sak_rekey_time=None,
    macsec_mode='integrity_confidentiality',
    kay_on=True,
    key_role='key_server_always',
    delay_protect=True,
    participant_activation='onoperup',
    sci_included=False,
    cipher_preference=[]
)

ptp_config = PTPConfig(
    cmlds_linkport_enabled=False,
    ptp_ports=[
        PTPPort(
            domain_id=1,
            src_port_identity=2,
            sync_config=PTPTimeTransmitterConfig(
                type='time_transmitter',
                log_tx_period=-3,
                two_step=True,
                tlv=[]
            )
        )
    ]
)

print("SUCCESS")
sys.exit(0)