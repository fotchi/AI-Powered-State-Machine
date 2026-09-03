import sys
from flync.model.flync_4_ecu.sockets import DeploymentUnion
from flync.model.flync_4_ecu.socket_container import SocketContainer
from pydantic import ValidationError

try:
    obj = SocketContainer(name="example_socket", sockets=[], deployment_union=DeploymentUnion(id="non_existent_id"))
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)