import sys
from flync.model.flync_4_communication.flync_communication import FLYNCCommunicationConfig
from flync.model.flync_4_security.firewall import Firewall, FirewallRule
from pydantic import ValidationError

scenario = {
    'type': 'Positive',
    'description': 'Valid Firewall Rule Destination Port Matching TCPOption Socket Configuration'
}

tcp_option = TCPOption(port=12345)
flync_communication_config = FLYNCCommunicationConfig(tcp_profiles=[tcp_option])
firewall = Firewall(default_action='accept')
firewall_rule = FirewallRule(name='rule1', action='accept', pattern=FrameFilter())
firewall.input_rules.append(firewall_rule)

print("SUCCESS")
sys.exit(0)