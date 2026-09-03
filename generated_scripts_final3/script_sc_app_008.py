import sys
from flync.model.flync_4_app.app_bindings import AppBindings

try:
    app_bindings = AppBindings(app_refs=[])
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)