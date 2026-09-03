import sys
from flync.model.flync_4_communication.flync_communication import FLYNCCommunicationConfig
from flync.model.flync_4_app.application import ServiceConsumerReference

class App(ServiceConsumerReference):
    type = 'consumer'
    service_name = 'non_existent_service'
    instance_id = 123
    major_version = 1

try:
    config = FLYNCCommunicationConfig()
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)

app = App()

print("SUCCESS")
sys.exit(0)