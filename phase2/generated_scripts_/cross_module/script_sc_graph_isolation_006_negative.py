import sys
from flync.model.flync_4_security.firewall import FirewallRule
from flync.model.flync_4_app.application import ServiceProviderReference
from pydantic import ValidationError
try:
    sp_ref = ServiceProviderReference(service_id=1, instance_id=10, major_version=1)
    obj = FirewallRule(name="block_invalid", action="reject", pattern=sp_ref)
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)