import sys
from flync.model.flync_4_app.application import App
from flync.model.flync_4_ecu.ecu import ECU
from pydantic import ValidationError

app1 = App(name='TelemetryApp', service_consumer_refs=None, service_provider_refs=None)
app2 = App(name='TelemetryApp', service_consumer_refs=None, service_provider_refs=None)

try:
    ECU(app1=app1, app2=app2)
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)