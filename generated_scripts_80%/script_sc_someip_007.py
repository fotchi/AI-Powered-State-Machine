import sys
from flync.model.flync_4_someip.service_interface import SDConfig, SDTimings
from pydantic import BaseModel

class SDConfig(BaseModel):
    ip_address: str = "192.168.1.100"
    port: int = 30490
    sd_timings: list[SDTimings] = [
        SDTimings(
            name="default_sd",
            timing_profile="sd_config.flync.yaml",
            service_name="my_service"
        )
    ]

try:
    config = SDConfig()
    print("SUCCESS")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)