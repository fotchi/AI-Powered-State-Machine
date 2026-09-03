import sys
from flync.model.flync_4_app.application import ServiceConsumerReference
from flync.model.flync_4_app.application import ServiceProviderReference

try:
    service_consumer_reference = ServiceConsumerReference(
        type='consumer',
        service_name='non_existent_service',
        instance_id=0,
        major_version=1
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

sys.exit(0)