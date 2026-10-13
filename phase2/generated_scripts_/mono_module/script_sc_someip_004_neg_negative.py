import sys
from pydantic import ValidationError
from flync.model.flync_4_someip.service_interface import SOMEIPRequestResponseMethod, SOMEIPParameter, SOMEIPTP

try:
    method = SOMEIPRequestResponseMethod(
        name="get_vehicle_info",
        description="Retrieve vehicle information",
        type="request_response",
        id=0x01,
        input_parameters=[
            SOMEIPParameter(
                name="vehicle_id",
                description="ID of the vehicle",
                type="UNKNOWN_TYPE"  # Fault injecté : missing or dangling reference
            )
        ],
        output_parameters=[
            SOMEIPParameter(
                name="vehicle_info",
                description="Information about the vehicle",
                type="string"
            )
        ]
    )
except ValidationError as e:
    print("SUCCESS")
    sys.exit(0)
else:
    sys.exit(1)