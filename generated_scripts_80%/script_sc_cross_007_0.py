import sys
from flync.model.flync_4_app.app_bindings import AppBindings
from flync.model.flync_4_someip.service_interface import SOMEIPConfig
from flync.model.flync_4_app.application import ServiceConsumerReference
from pydantic import ValidationError

some_ip_config = SOMEIPConfig(
    version="1.0",
    sd_config=SDConfig(ip_address="", sd_timings={}, sd_type=""),
    services=[],
    someip_timings={}
)

app_bindings = AppBindings(app_refs=[])

service_consumer_reference = ServiceConsumerReference(
    type='consumer',
    service_name='',
    instance_id=0,
    major_version=0
)

try:
    obj = SOMEIPConfig(
        version="1.0",
        sd_config=SDConfig(ip_address="", sd_timings={}, sd_type=""),
        services=[],
        someip_timings={}
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)