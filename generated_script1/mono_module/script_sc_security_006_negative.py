import sys
from flync.model.flync_4_security.firewall import FirewallRule
from pydantic import ValidationError

try:
    fw_rule = FirewallRule(name="test_rule", action="reject", pattern=None, interface_id="ethX")
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)