import sys
from pydantic import ValidationError
from flync.model.flync_4_topology.ethernet_topology import ExternalConnection, FLYNCTopology
from flync.model.flync_4_nm.state_management import StateManagementConfig, StateManagementGroup

state_management_config = StateManagementConfig(groups=[StateManagementGroup(name="group1", nm_pdu="pdu1", timing_profile="profile1")])
topology = FLYNCTopology()
ecu1 = ExternalConnection(type='ecu_port_to_ecu_port', id='id1', ecu1_port_name='port1', ecu2_port_name='port2')
try:
    topology.ethernet_topology.system_topology.append(ecu1)
except AttributeError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected AttributeError but no error was raised")
    sys.exit(1)