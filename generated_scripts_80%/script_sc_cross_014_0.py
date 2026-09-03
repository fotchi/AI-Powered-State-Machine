import sys
from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_security.firewall import Firewall, FirewallRule

can_bus = CANBus(
    name='CAN Bus',
    baud_rate=500000,
    fd_enabled=False,
    frames=[
        {'type': 'CANFrame', 'id': 291, 'dlc': 8},
        {'type': 'CANFDFrame', 'id': 1110, 'dlc': 16}
    ]
)

firewall = Firewall(
    default_action='reject',
    input_rules=[FirewallRule(name='Input Rule', action='accept', pattern={'type': 'FrameFilter', 'filter_type': 'ECU_ID'})],
    output_rules=[FirewallRule(name='Output Rule', action='drop', pattern={'type': 'FrameFilter', 'filter_type': 'ECU_ID'})]
)

print("SUCCESS")
sys.exit(0)