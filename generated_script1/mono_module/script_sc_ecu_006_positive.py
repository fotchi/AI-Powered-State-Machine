import sys
from flync.model.flync_4_ecu.lin_interface import LINMasterInterface

lin_master_interface = LINMasterInterface(
    name="LINMaster1",
    bus_ref="LINBus1",
    lin_protocol="2.0",
    p2_min=0.1,
    st_min=0.2
)

print("SUCCESS")
sys.exit(0)