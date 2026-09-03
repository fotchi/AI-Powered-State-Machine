import sys
from pydantic import ValidationError
from flync.model.flync_4_ecu.socket_container import SocketContainer

try:
    socket_container = SocketContainer(name="example", vlan_id=5000)
except ValidationError as e:
    sys.exit(0)

sys.exit(1)