import sys
from flync.model.flync_4_app.application import ServiceConsumerReference
from pydantic import ValidationError

scenario = {
    "type": "Negative",
    "description": "Dangling ServiceConsumerReference"
}

service_consumer_reference = ServiceConsumerReference(
    type="consumer",
    service_name="non_existent_service",
    instance_id=123,
    major_version=1
)

try:
    service_consumer_reference.validate()
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)