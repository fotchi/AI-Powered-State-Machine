import sys
from pydantic import ValidationError

from flync.model.flync_4_app.app_bindings import AppBindings
from flync.model.flync_4_ecu.controller import Controller
from flync.model.flync_4_tsn.timesync import PTPPort
from flync.model.flync_4_app.application import ServiceProviderReference
from flync.model.flync_4_tsn.qos import SingleRateTwoColorMarker
from flync.model.flync_4_tsn.qos import Stream
from flync.model.flync_4_metadata.metadata import BaseVersion
from flync.model.flync_4_metadata.metadata import EmbeddedMetadata

try:
    app_bindings = AppBindings(
    )
    controller = Controller(
        name="demo_name",
        controller_metadata=EmbeddedMetadata(type="demo_type", author="demo_author", compatible_flync_version=BaseVersion(version="demo_version"), target_system="demo_target_system"),
    )
    ptp_port = PTPPort(
        domain_id=1,
        src_port_identity=1,
        sync_config=None,
    )
    service_provider_reference = ServiceProviderReference(
        instance_id=1,
        major_version=1,
    )
    single_rate_two_color_marker = SingleRateTwoColorMarker(
        cir=1,
        cbs=1,
        eir=0,
        ebs=1,
        coupling=False,
    )
    stream = Stream(
        name="demo_name",
        stream_identification=[],
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
