import sys
from flync.model.flync_4_metadata.metadata import ECUMetadata
from flync.model.flync_4_metadata.metadata import EmbeddedMetadata
from flync.model.flync_4_tsn.timesync import PTPConfig
from flync.model.flync_4_tsn.timesync import PTPPort
from pydantic import ValidationError

ecu_metadata = ECUMetadata(
    type="ecu",
    author="John Doe",
    compatible_flync_version={"major": 1, "minor": 0}
)

embedded_metadata = EmbeddedMetadata(
    type="controller",
    author="Jane Doe",
    target_system="AARCH",
    hardware=None,
    app=None,
    bootloader=None
)
embedded_metadata.parent_ecu_identifier = "non_existent_parent"

ptp_config = PTPConfig(
    cmlds_linkport_enabled=False,
    ptp_ports=[PTPPort(domain_id=1, src_port_identity=2)]
)

try:
    obj = EmbeddedMetadata(**vars(embedded_metadata))
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)