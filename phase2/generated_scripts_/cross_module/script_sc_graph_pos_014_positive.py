import sys
from flync.model.flync_4_security.macsec import MACsecConfig
from flync.model.flync_4_ecu.switch import SwitchPort
macsec = MACsecConfig(vlan_bypass=[100], ethertype_bypass=[], src_mac_address_bypass=[], dest_mac_address_bypass=[], ckn="A1B2C3D4E5F6", hello_time=10, bounded_hello_time=20, life_time=30, sak_retire_time=40, hello_time_rampup=[], macsec_mode='integrity', kay_on=True, key_role='key_server_always', delay_protect=False, participant_activation='always')
port = SwitchPort(name="port1", silicon_port_no=1, default_vlan_id=100, macsec_config=macsec)
print("SUCCESS")
sys.exit(0)