import sys
from flync.model.flync_4_security.firewall import Firewall
from flync.model.flync_4_security.firewall import FirewallRule
from flync.model.flync_4_someip.service_interface import SDConfig
from flync.model.flync_4_someip.service_interface import SOMEIPConfig

firewall = Firewall(
    default_action='accept',
    input_rules=[
        FirewallRule(name='input_rule', action='accept', pattern={'type': 'frame_filter'})
    ],
    output_rules=[],
    forward_rules=[]
)

sd_config = SDConfig(ip_address='239.255.0.1', port=30490, sd_timings=[])

someip_config = SOMEIPConfig(
    version='1.0',
    sd_config=sd_config,
    services=[],
    someip_timings={}
)

print("SUCCESS")
sys.exit(0)