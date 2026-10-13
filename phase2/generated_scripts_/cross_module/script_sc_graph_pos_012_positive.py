import sys
from flync.model.flync_4_ecu.sockets import DeploymentUnion
from flync.model.flync_4_someip.deployment import SOMEIPSDDeployment
sd = SOMEIPSDDeployment()
du = DeploymentUnion(root=sd)
print("SUCCESS")
sys.exit(0)