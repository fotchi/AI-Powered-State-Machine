import sys
from flync.model.flync_4_app.app_bindings import AppBindings
from pydantic import ValidationError

try:
    app_bindings = AppBindings(app_refs=["UnusedApp"])
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)