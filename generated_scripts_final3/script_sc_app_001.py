import sys
from flync.model.flync_4_app.application import ServiceConsumerReference
from flync.model.flync_4_app.application import ServiceProviderReference
from pydantic import ValidationError

app = {
    "id": 12345,
    "name": "My App",
    "ecu_controller_id": 67890,
    "service_consumer_reference": ServiceConsumerReference(
        type="consumer",
        service_name="my_service",
        instance_id=1,
        major_version=2
    ),
    "service_provider_reference": ServiceProviderReference(
        type="provider",
        service_name="my_service",
        instance_id=3,
        major_version=4
    )
}

try:
    app["service_consumer_reference"].validate()
    app["service_provider_reference"].validate()
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("SUCCESS")
    sys.exit(0)