import sys
from flync.model.flync_4_app.app_bindings import AppBindings

app_bindings = AppBindings(
    app_refs=[
        "App1",
        "App2"
    ],
    ecu_controller="ECU-12345",
    metadata={
        "description": "Test AppBindings",
        "version": "1.0"
    }
)

print("SUCCESS")
sys.exit(0)