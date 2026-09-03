import sys
from flync.model.flync_4_app.application import ServiceProviderReference
from pydantic import ValidationError

try:
    obj = ServiceProviderReference(
        type='provider',
        service_name='VideoService',
        instance_id=1,
        major_version=1
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)