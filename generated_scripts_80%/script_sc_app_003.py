import sys
from flync.model.flync_4_app.app_bindings import AppBindings

app_bindings = AppBindings(
    app_refs=["App1"],
    ecu_controller="ECU1"
)
print("SUCCESS")
sys.exit(0)