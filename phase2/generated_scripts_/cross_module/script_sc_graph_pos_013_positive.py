import sys
from flync.model.flync_4_tsn.timesync import PTPConfig
from flync.model.flync_4_ecu.switch import SwitchPort
ptp = PTPConfig()
port = SwitchPort(name="port1", silicon_port_no=0, default_vlan_id=1, ptp_config=ptp)
print("SUCCESS")
sys.exit(0)