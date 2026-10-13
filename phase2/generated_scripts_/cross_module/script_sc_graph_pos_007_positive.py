import sys
from flync.model.flync_4_communication.flync_communication import FLYNCCommunicationConfig
from flync.model.flync_4_nm.state_management import StateManagementConfig, StateManagementGroup
state_group = StateManagementGroup(name="EngineState", nm_pdu="EnginePDU", timing_profile="EngineTiming")
state_mgmt = StateManagementConfig(groups=[state_group])
comm_config = FLYNCCommunicationConfig(state_management=state_mgmt)
print("SUCCESS")
sys.exit(0)