import sys
from flync.model.flync_4_app.app_bindings import AppBindings

app_bindings = AppBindings(app_refs=["telemetry_app", "control_app"])
print("SUCCESS")
sys.exit(0)