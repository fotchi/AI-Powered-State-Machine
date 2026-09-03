import sys
from flync.model.flync_4_app.app_bindings import AppBindings
from pydantic import BaseModel

class AppBindings(BaseModel):
    app_refs: list[str] = []

app_bindings1 = AppBindings(app_refs=["App1", "App2"])
app_bindings2 = AppBindings(app_refs=["App1", "App2"])
app_bindings3 = AppBindings(app_refs=["App1", "App2"])

print("SUCCESS")
sys.exit(0)