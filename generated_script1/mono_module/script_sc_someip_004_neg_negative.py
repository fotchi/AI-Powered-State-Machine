import sys
from pydantic import ValidationError
from flync.model.flync_4_someip.service_interface import SOMEIPRequestResponseMethod

try:
    method = SOMEIPRequestResponseMethod(
        name="get_vehicle_info",
        id=0x01,
        type="request_response",
        input_parameters=[
            {
                "name": "vehicle_id",
                "type": "UNKNOWN_TYPE",
                "description": "Vehicle identifier"
            }
        ],
        output_parameters=[
            {
                "name": "vehicle_info",
                "type": "string",
                "description": "Information about the vehicle"
            }
        ]
    )
except ValidationError as e:
    print("SUCCESS")
    sys.exit(0)
else:
    print("FAILURE")
    sys.exit(1)