import sys
from flync.model.flync_4_tsn.qos import ATSInstance
from flync.model.flync_4_app.app_bindings import AppBindings
from flync.model.flync_4_app.application import ServiceProviderReference
from flync.model.flync_4_tsn.qos import SingleRateTwoColorMarker, Stream

app_bindings = AppBindings(app_refs=["my_app"])
service_provider_reference = ServiceProviderReference(
    type="provider",
    service_name="my_service",
    instance_id=1,
    major_version=1
)
ats_instance = ATSInstance(
    committed_information_rate=1000,
    committed_burst_size=2000,
    max_residence_time=3000
)
single_rate_two_color_marker = SingleRateTwoColorMarker(
    cir=50000,
    cbs=60000,
    eir=0,
    ebs=70000,
    coupling=False
)

stream = Stream(
    name="my_stream",
    stream_identification=[],
    policer=single_rate_two_color_marker,
    ats=ats_instance
)

try:
    obj = AppBindings(app_refs=["my_app"])
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)