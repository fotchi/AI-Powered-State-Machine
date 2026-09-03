import sys
from flync.model.flync_4_app.app_bindings import AppBindings

appbindings = 'one'
app_refs = ['telemetry_app', 'control_app']
app_bindings = AppBindings(app_refs=app_refs)
print("SUCCESS")
sys.exit(0)