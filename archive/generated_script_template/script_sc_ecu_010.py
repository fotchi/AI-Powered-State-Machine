import sys
from pydantic import ValidationError

from flync.model.flync_4_ecu.sockets import DeploymentUnion
from flync.model.flync_4_ecu.socket_container import SocketContainer

try:
    deployment_union = DeploymentUnion(
        root=None,
    )
    socket_container = SocketContainer(
        name="demo_name",
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
