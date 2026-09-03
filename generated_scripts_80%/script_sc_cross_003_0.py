import sys
from flync.model.flync_4_app.app_bindings import AppBindings
from flync.model.flync_4_metadata.metadata import ECUMetadata, EmbeddedMetadata

try:
    ecu_metadata = ECUMetadata(
        type='ECU',
        author='N/A',
        compatible_flync_version={'major': 4},
        extensions=None,
        hardware=None,
        software=None
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)

try:
    embedded_metadata = EmbeddedMetadata(
        type='ECU',
        author='N/A',
        compatible_flync_version={'major': 4},
        extensions=None,
        hardware=None,
        app=None,
        bootloader=None,
        target_system='AARCH'
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)

try:
    app_bindings = AppBindings(
        app_refs=['app1', 'app2'],
        ecu_ref=embedded_metadata
    )
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected exception but no error was raised")
    sys.exit(1)

print("SUCCESS")
sys.exit(0)