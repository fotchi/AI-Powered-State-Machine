import sys
from flync.model.flync_4_someip.service_interface import SOMEIPServiceInterface
from pydantic import ValidationError

scenario = {
    'type': 'Negative',
    'description': 'Duplicate Service Identifier in two SOMEIPServiceInterface objects'
}

someip_service_interface1 = SOMEIPServiceInterface(
    name='service1',
    id=0x2000,
    meta=SOMEIPServiceMetadata(author={'name': 'author1', 'email': 'email1'}, compatible_flync_version={'major': 4, 'minor': 2})
)

someip_service_interface2 = SOMEIPServiceInterface(
    name='service2',
    id=0x2000,
    meta=SOMEIPServiceMetadata(author={'name': 'author2', 'email': 'email2'}, compatible_flync_version={'major': 4, 'minor': 3})
)

try:
    someip_service_interface1
    someip_service_interface2
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)