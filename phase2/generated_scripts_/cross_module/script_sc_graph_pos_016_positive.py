import sys
from flync.model.flync_4_safety.e2e import E2EConfig
from flync.model.flync_4_someip.service_interface import SOMEIPField
e2e = E2EConfig(profile="default_profile", data_id=42)
field = SOMEIPField(name="example_field", notifier_id=1, notifier_e2e=e2e)
print("SUCCESS")
sys.exit(0)