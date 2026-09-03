import sys
from flync.model.flync_4_someip.service_interface import SOMEIPRequestResponseMethod
from pydantic import BaseModel, Field, Annotated, Optional, List, BeforeValidator

class SOMEIPRequestResponseMethod(BaseModel):
    name: str | None = True
    description: Optional[str] | None = False
    type: Literal['request_response', 'fire_and_forget'] | None = True
    id: Annotated[int, Field(gt=0, le=65535, strict=True)] | None = True
    reliable: bool | None = False
    someip_tp: Optional[SOMEIPTP] | None = False
    input_parameters: Annotated[Optional[List['SOMEIPParameter']], BeforeValidator(common_validators.none_to_empty_list)] | None = False
    someip_timing: Optional[str] | None = False
    output_parameters: Annotated[Optional[List['SOMEIPParameter']], BeforeValidator(common_validators.none_to_empty_list)] | None = False

someip_request_response_method = SOMEIPRequestResponseMethod(
    name='GetEngineSpeed',
    type='request_response',
    id=1,
    input_parameters=[
        {'name': 'requestId', 'type': 'uint8'}
    ],
    output_parameters=[
        {'name': 'engineSpeed', 'type': 'uint16'}
    ]
)

print("SUCCESS")
sys.exit(0)