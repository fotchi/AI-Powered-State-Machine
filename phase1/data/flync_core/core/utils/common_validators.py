"""
Compatibility shim -- NOT part of the real FLYNC repo, added locally.

Upstream commit 3f7004333541b2c49b6f960ffe3d3006e97b5019 ("chore: split
someip_datatypes and common_validators", 2026-08-24/25 on
Technica-Engineering/FLYNC) removed src/flync/core/utils/common_validators.py
and split its contents into what is now src/flync/core/validators/{address,
bit_ranges,connection_compatibility,generic,traffic_classes}.py -- but the
SAME commit forgot to update the import statements in every model file that
still does `import flync.core.utils.common_validators as common_validators`
(can_bus.py, controller.py, firewall.py, qos.py, state_management.py, and
about a dozen others). As of this file's writing, `main` on the upstream
repo is still broken this way -- confirmed directly against the GitHub API
(the file 404s at every commit after the split, including current HEAD).

This restores the old combined import path as a thin re-export of the real,
current, unmodified upstream functions -- every name below is copied from
an actual file that exists today, nothing here is guessed or reimplemented.
If/when upstream fixes their own imports, this file becomes dead weight
but harmless (nothing will import a missing module anymore).

Do not add anything here that isn't a straight re-export of a real function.
"""
from flync.core.validators.generic import (
    none_to_empty_list,
    single_to_list,
    validate_elements_in,
    validate_list_items_and_remove,
    validate_list_items_unique,
    validate_or_remove,
)
from flync.core.validators.traffic_classes import validate_traffic_classes
from flync.core.validators.address import (
    validate_any_multicast_address,
    validate_ip_multicast,
    validate_mac_multicast,
    validate_mac_unicast,
    validate_multicast_list,
    validate_multicast_list_only_ip,
    validate_vlan_id,
)
from flync.core.validators.connection_compatibility import (
    validate_cbs_idleslopes_fit_portspeed,
    validate_compulsory_mii_config_compatibility,
    validate_gptp,
    validate_gptp_domains,
    validate_htb,
    validate_ingress_streams_fields,
    validate_macsec,
    validate_optional_mii_config_compatibility,
    validate_vlan_ids_unique,
)

__all__ = [
    "none_to_empty_list",
    "single_to_list",
    "validate_elements_in",
    "validate_list_items_and_remove",
    "validate_list_items_unique",
    "validate_or_remove",
    "validate_traffic_classes",
    "validate_any_multicast_address",
    "validate_ip_multicast",
    "validate_mac_multicast",
    "validate_mac_unicast",
    "validate_multicast_list",
    "validate_multicast_list_only_ip",
    "validate_vlan_id",
    "validate_cbs_idleslopes_fit_portspeed",
    "validate_compulsory_mii_config_compatibility",
    "validate_gptp",
    "validate_gptp_domains",
    "validate_htb",
    "validate_ingress_streams_fields",
    "validate_macsec",
    "validate_optional_mii_config_compatibility",
    "validate_vlan_ids_unique",
]
