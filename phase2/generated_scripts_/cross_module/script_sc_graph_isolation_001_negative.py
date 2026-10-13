import sys
from flync.model.flync_4_app.application import ServiceConsumerReference
from pydantic import ValidationError
try:
    obj = ServiceConsumerReference(service_id=0, instance_id=1, major_version=1)
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)