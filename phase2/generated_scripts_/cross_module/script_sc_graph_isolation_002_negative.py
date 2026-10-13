import sys
from pydantic import ValidationError
from flync.model.flync_4_communication.flync_channels import FLYNCChannelConfig
from flync.model.flync_4_app.application import ServiceConsumerReference
try:
    channel = FLYNCChannelConfig()
    consumer = ServiceConsumerReference(service_id=1, instance_id=1, major_version=1, communication_channel_ref=channel)
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)