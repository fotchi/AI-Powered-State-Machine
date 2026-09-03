import sys

from flync.model.flync_4_communication.flync_channels import FLYNCChannelConfig
from flync.model.flync_4_communication.flync_communication import FLYNCCommunicationConfig
from flync.model.flync_4_security.firewall import Firewall
from flync.model.flync_4_security.firewall import FirewallRule
from flync.model.flync_4_security.macsec import IntegrityWithConfidentiality
from flync.model.flync_4_security.macsec import MACsecConfig
from flync.model.flync_4_ecu.sockets import TCPOption
from flync.model.flync_4_tsn.qos import FrameFilter

flync_channel_config = FLYNCChannelConfig(
)
flync_communication_config = FLYNCCommunicationConfig(
)
firewall = Firewall(
)
firewall_rule = FirewallRule(
    name="demo_name",
    action='reject',
    pattern=FrameFilter(),
)
integrity_with_confidentiality = IntegrityWithConfidentiality(
)
ma_csec_config = MACsecConfig(
    vlan_bypass=[],
    hello_time=1,
    bounded_hello_time=1,
    life_time=1,
    sak_retire_time=1,
    hello_time_rampup=[],
    macsec_mode='disabled',
    kay_on=False,
    key_role='key_server_always',
    delay_protect=False,
    participant_activation='disabled',
)
tcp_option = TCPOption(
    tcp_profile_id=1,
)

print("SUCCESS")
sys.exit(0)
