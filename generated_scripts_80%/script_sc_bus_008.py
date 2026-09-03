import sys
from pydantic import ValidationError

class SlaveNode:
    def __init__(self, pid):
        self.pid = pid

try:
    slave_node1 = SlaveNode(pid=0x1234)
    slave_node2 = SlaveNode(pid=0x1234)  # duplicate PID
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)