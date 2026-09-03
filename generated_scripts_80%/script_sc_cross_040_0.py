import sys
from flync.model.flync_4_security.firewall import Firewall
from flync.model.flync_4_security.firewall import FirewallRule
from flync.model.flync_4_nm.state_management import StateManagementGroup

firewall = Firewall(
    default_action='accept',
    input_rules=[FirewallRule(name='rule1', action='accept', pattern={'type': 'IP', 'value': '192.168.1.1'})],
    output_rules=[],
    forward_rules=[]
)

state_management_group = StateManagementGroup(
    name='group1',
    nm_pdu='pdu1',
    timing_profile='profile1'
)

print("SUCCESS")
sys.exit(0)