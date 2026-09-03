import sys
from flync.model.flync_4_app.app_bindings import AppBindings
from flync.model.flync_4_security.firewall import Firewall, FirewallRule
from flync.model.flync_4_app.application import ServiceProviderReference

firewall_rule = FirewallRule(name='rule1', action='drop', pattern={'source': '192.168.0.1/24'})
firewall = Firewall(default_action='reject', input_rules=[firewall_rule])
app_bindings = AppBindings(app_refs=['app1'])
service_provider_reference = ServiceProviderReference(type='provider', instance_id=123, major_version=2)

try:
    obj = firewall
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)