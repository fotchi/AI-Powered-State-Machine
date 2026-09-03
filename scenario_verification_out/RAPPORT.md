# Vérification automatique des scénarios KPIT

Générée par `scenario_verifier.py` — indexation réelle de `src/flync/model` (12 modules) + `src/flync/sdk/{workspace,utils}` (classes/fonctions de haut niveau uniquement), correspondance de nom restreinte aux modules déclarés dans `submodel` (voir `entities_dropped_out_of_scope` pour les faux positifs écartés), et priorisation des classes-pont réelles (`module_relations.py`) pour les scénarios cross-module.

| ID | Submodel(s) déclaré(s) | Classification | Entités (model) | Entités (sdk) | Couplage réel confirmé |
|---|---|---|---|---|---|
| `SC-APP-001` | flync_4_app | ✅ MODEL_ONLY | `ServiceConsumerReference`, `ServiceProviderReference` | — | — |
| `SC-APP-002` | flync_4_app | ✅ MODEL_ONLY | `ServiceConsumerReference`, `ServiceProviderReference` | — | — |
| `SC-APP-003` | flync_4_app | ✅ MODEL_ONLY | `AppBindings` | — | — |
| `SC-APP-004` | flync_4_app | ❓ UNRESOLVED | — | — | — |
| `SC-APP-005` | flync_4_app | ✅ MODEL_ONLY | `ServiceProviderReference` | — | — |
| `SC-APP-006` | flync_4_app | ⚠️ REQUIRES_SDK | `ServiceProviderReference` | `Range` | — |
| `SC-APP-007` | flync_4_app | ✅ MODEL_ONLY | `AppBindings` | — | — |
| `SC-APP-008` | flync_4_app | ✅ MODEL_ONLY | `AppBindings` | — | — |
| `SC-APP-009` | flync_4_app | ✅ MODEL_ONLY | `ServiceConsumerReference`, `ServiceProviderReference` | — | — |
| `SC-BUS-001` | flync_4_bus | ❓ UNRESOLVED | — | — | — |
| `SC-BUS-002` | flync_4_bus | ❓ UNRESOLVED | — | — | — |
| `SC-BUS-003` | flync_4_bus | ❓ UNRESOLVED | — | — | — |
| `SC-BUS-004` | flync_4_bus | ❓ UNRESOLVED | — | — | — |
| `SC-BUS-005` | flync_4_bus | ❓ UNRESOLVED | — | — | — |
| `SC-BUS-006` | flync_4_bus | ❓ UNRESOLVED | — | — | — |
| `SC-BUS-007` | flync_4_bus | ❓ UNRESOLVED | — | — | — |
| `SC-BUS-008` | flync_4_bus | ❓ UNRESOLVED | — | — | — |
| `SC-BUS-009` | flync_4_bus | ❓ UNRESOLVED | — | — | — |
| `SC-COMMUNICATION-001` | flync_4_communication | ✅ MODEL_ONLY | `FLYNCChannelConfig` | — | — |
| `SC-COMMUNICATION-002` | flync_4_communication | ❓ UNRESOLVED | — | — | — |
| `SC-COMMUNICATION-003` | flync_4_communication | ❓ UNRESOLVED | — | — | — |
| `SC-COMMUNICATION-004` | flync_4_communication | ✅ MODEL_ONLY | `FLYNCChannelConfig` | — | — |
| `SC-COMMUNICATION-005` | flync_4_communication | ❓ UNRESOLVED | — | — | — |
| `SC-COMMUNICATION-006` | flync_4_communication | ❓ UNRESOLVED | — | — | — |
| `SC-COMMUNICATION-008` | flync_4_communication | ❓ UNRESOLVED | — | — | — |
| `SC-COMMUNICATION-009` | flync_4_communication | ❓ UNRESOLVED | — | — | — |
| `SC-COMMUNICATION-010` | flync_4_communication | ❓ UNRESOLVED | — | — | — |
| `SC-ECU-001` | flync_4_ecu | ✅ MODEL_ONLY | `Controller`, `ECUPort` | — | — |
| `SC-ECU-002` | flync_4_ecu | ✅ MODEL_ONLY | `ECUPort` | — | — |
| `SC-ECU-003` | flync_4_ecu | ✅ MODEL_ONLY | `Switch`, `VirtualSwitch`, `VirtualSwitchPort` | — | — |
| `SC-ECU-004` | flync_4_ecu | ✅ MODEL_ONLY | `Switch` | — | — |
| `SC-ECU-005` | flync_4_ecu | ✅ MODEL_ONLY | `IPv4AddressEndpoint`, `Socket` | — | — |
| `SC-ECU-006` | flync_4_ecu | ✅ MODEL_ONLY | `Controller` | — | — |
| `SC-ECU-007` | flync_4_ecu | ✅ MODEL_ONLY | `EthernetInterface` | — | — |
| `SC-ECU-008` | flync_4_ecu | ✅ MODEL_ONLY | `CANInterface` | — | — |
| `SC-ECU-009` | flync_4_ecu | ✅ MODEL_ONLY | `LINMasterInterface` | — | — |
| `SC-ECU-010` | flync_4_ecu | ✅ MODEL_ONLY | `Switch`, `VirtualSwitch` | — | — |
| `SC-METADATA-001` | flync_4_metadata | ✅ MODEL_ONLY | `SystemMetadata` | — | — |
| `SC-METADATA-002` | flync_4_metadata | ✅ MODEL_ONLY | `ECUMetadata` | — | — |
| `SC-METADATA-003` | flync_4_metadata | ✅ MODEL_ONLY | `BaseVersion` | — | — |
| `SC-METADATA-004` | flync_4_metadata | ✅ MODEL_ONLY | `HardwareBaseMetadata` | — | — |
| `SC-METADATA-005` | flync_4_metadata | ✅ MODEL_ONLY | `ECUMetadata`, `EmbeddedMetadata` | — | — |
| `SC-METADATA-007` | flync_4_metadata | ✅ MODEL_ONLY | `SystemMetadata` | — | — |
| `SC-METADATA-008` | flync_4_metadata | ✅ MODEL_ONLY | `ECUMetadata` | — | — |
| `SC-METADATA-009` | flync_4_metadata | ✅ MODEL_ONLY | `BaseMetadata` | — | — |
| `SC-NM-001` | flync_4_nm | ✅ MODEL_ONLY | `StateManagementGroup`, `StateMembershipRef` | — | — |
| `SC-NM-002` | flync_4_nm | ✅ MODEL_ONLY | `StateManagementGroup` | — | — |
| `SC-NM-003` | flync_4_nm | ✅ MODEL_ONLY | `GroupTiming` | — | — |
| `SC-NM-004` | flync_4_nm | ✅ MODEL_ONLY | `GroupTiming` | — | — |
| `SC-NM-005` | flync_4_nm | ✅ MODEL_ONLY | `StateMembershipRef` | — | — |
| `SC-NM-007` | flync_4_nm | ✅ MODEL_ONLY | `SleepTiming` | — | — |
| `SC-NM-008` | flync_4_nm | ✅ MODEL_ONLY | `SleepTiming` | — | — |
| `SC-NM-009` | flync_4_nm | ✅ MODEL_ONLY | `AnnouncementPhaseTiming` | — | — |
| `SC-NM-010` | flync_4_nm | ✅ MODEL_ONLY | `AnnouncementPhaseTiming` | — | — |
| `SC-SECURITY-001` | flync_4_security | ✅ MODEL_ONLY | `IntegrityWithConfidentiality`, `MACsecConfig` | — | — |
| `SC-SECURITY-002` | flync_4_security | ✅ MODEL_ONLY | `FirewallRule` | — | — |
| `SC-SECURITY-003` | flync_4_security | ✅ MODEL_ONLY | `IntegrityWithoutConfidentiality`, `MACsecConfig` | — | — |
| `SC-SECURITY-004` | flync_4_security | ✅ MODEL_ONLY | `FirewallRule` | — | — |
| `SC-SECURITY-005` | flync_4_security | ✅ MODEL_ONLY | `Firewall`, `FirewallRule` | — | — |
| `SC-SECURITY-006` | flync_4_security | ✅ MODEL_ONLY | `IntegrityWithConfidentiality`, `MACsecConfig` | — | — |
| `SC-SECURITY-007` | flync_4_security | ✅ MODEL_ONLY | `FirewallRule` | — | — |
| `SC-SECURITY-009` | flync_4_security | ✅ MODEL_ONLY | `Firewall`, `FirewallRule` | — | — |
| `SC-SIGNAL-001` | flync_4_signal | ✅ MODEL_ONLY | `Signal` | — | — |
| `SC-SIGNAL-002` | flync_4_signal | ✅ MODEL_ONLY | `Signal` | — | — |
| `SC-SIGNAL-003` | flync_4_signal | ✅ MODEL_ONLY | `Signal` | — | — |
| `SC-SIGNAL-004` | flync_4_signal | ✅ MODEL_ONLY | `Signal` | — | — |
| `SC-SIGNAL-005` | flync_4_signal | ✅ MODEL_ONLY | `BitfieldGroup`, `Signal` | — | — |
| `SC-SIGNAL-006` | flync_4_signal | ✅ MODEL_ONLY | `Signal` | — | — |
| `SC-SIGNAL-007` | flync_4_signal | ✅ MODEL_ONLY | `Signal` | — | — |
| `SC-SIGNAL-008` | flync_4_signal | ✅ MODEL_ONLY | `Signal`, `SignalInstance` | — | — |
| `SC-SIGNAL-009` | flync_4_signal | ✅ MODEL_ONLY | `Signal` | — | — |
| `SC-SIGNAL-010` | flync_4_signal | ✅ MODEL_ONLY | `Signal` | — | — |
| `SC-SOMEIP-001` | flync_4_someip | ✅ MODEL_ONLY | `SOMEIPServiceInterface` | — | — |
| `SC-SOMEIP-002` | flync_4_someip | ✅ MODEL_ONLY | `SOMEIPServiceInterface` | — | — |
| `SC-SOMEIP-003` | flync_4_someip | ✅ MODEL_ONLY | `SOMEIPRequestResponseMethod` | — | — |
| `SC-SOMEIP-004` | flync_4_someip | ✅ MODEL_ONLY | `SOMEIPEvent`, `SOMEIPEventgroup` | — | — |
| `SC-SOMEIP-005` | flync_4_someip | ✅ MODEL_ONLY | `SOMEIPField` | — | — |
| `SC-SOMEIP-006` | flync_4_someip | ✅ MODEL_ONLY | `Layer4Endpoint`, `SOMEIPServiceDeployment` | — | — |
| `SC-SOMEIP-007` | flync_4_someip | ✅ MODEL_ONLY | `SDConfig` | — | — |
| `SC-SOMEIP-008` | flync_4_someip | ❓ UNRESOLVED | — | — | — |
| `SC-SOMEIP-009` | flync_4_someip | ✅ MODEL_ONLY | `Layer4Endpoint`, `SOMEIPServiceInterface`, `SOMEIPServiceProvider` | — | — |
| `SC-SOMEIP-010` | flync_4_someip | ✅ MODEL_ONLY | `SOMEIPServiceConsumer`, `SOMEIPServiceInterface` | — | — |
| `SC-TOPOLOGY-001` | flync_4_topology | ✅ MODEL_ONLY | `ExternalConnection` | — | — |
| `SC-TOPOLOGY-002` | flync_4_topology | ✅ MODEL_ONLY | `ExternalConnection` | — | — |
| `SC-TOPOLOGY-004` | flync_4_topology | ❓ UNRESOLVED | — | — | — |
| `SC-TOPOLOGY-005` | flync_4_topology | ✅ MODEL_ONLY | `ExternalConnection` | — | — |
| `SC-TOPOLOGY-006` | flync_4_topology | ❓ UNRESOLVED | — | — | — |
| `SC-TOPOLOGY-009` | flync_4_topology | ❓ UNRESOLVED | — | — | — |
| `SC-TOPOLOGY-010` | flync_4_topology | ❓ UNRESOLVED | — | — | — |
| `SC-TSN-001` | flync_4_tsn | ✅ MODEL_ONLY | `PTPConfig`, `PTPTimeReceiverConfig`, `PTPTimeTransmitterConfig` | — | — |
| `SC-TSN-002` | flync_4_tsn | ✅ MODEL_ONLY | `PTPPort` | — | — |
| `SC-TSN-003` | flync_4_tsn | ✅ MODEL_ONLY | `CBSShaper` | — | — |
| `SC-TSN-004` | flync_4_tsn | ✅ MODEL_ONLY | `ATSInstance` | — | — |
| `SC-TSN-005` | flync_4_tsn | ✅ MODEL_ONLY | `TrafficClass` | — | — |
| `SC-TSN-006` | flync_4_tsn | ✅ MODEL_ONLY | `HTBInstance` | — | — |
| `SC-TSN-007` | flync_4_tsn | ✅ MODEL_ONLY | `FrameFilter` | — | — |
| `SC-TSN-008` | flync_4_tsn | ✅ MODEL_ONLY | `Stream` | — | — |
| `SC-TSN-009` | flync_4_tsn | ✅ MODEL_ONLY | `SingleRateTwoColorMarker`, `TrafficClass` | — | — |
| `SC-TSN-010` | flync_4_tsn | ✅ MODEL_ONLY | `DoubleRateThreeColorMarker`, `TrafficClass` | — | — |
| `SC-CROSS-000-0` | flync_4_app, flync_4_bus | ✅ MODEL_ONLY | `AppBindings`, `CANBus`, `ServiceProviderReference` | — | ⚠️ non confirmé |
| `SC-CROSS-001-0` | flync_4_app, flync_4_communication | ✅ MODEL_ONLY | `FLYNCCommunicationConfig`, `ServiceConsumerReference` | — | ⚠️ non confirmé |
| `SC-CROSS-002-0` | flync_4_app, flync_4_ecu | ✅ MODEL_ONLY | `AppBindings`, `Controller`, `ServiceProviderReference` | — | ✅ |
| `SC-CROSS-003-0` | flync_4_app, flync_4_metadata | ✅ MODEL_ONLY | `AppBindings`, `ECUMetadata`, `EmbeddedMetadata` | — | ⚠️ non confirmé |
| `SC-CROSS-004-0` | flync_4_app, flync_4_nm | ✅ MODEL_ONLY | `AppBindings`, `GroupTiming`, `ServiceProviderReference`, `StateManagementConfig`, `StateManagementGroup` | — | ⚠️ non confirmé |
| `SC-CROSS-005-0` | flync_4_app, flync_4_security | ✅ MODEL_ONLY | `AppBindings`, `Firewall`, `FirewallRule`, `ServiceProviderReference` | — | ⚠️ non confirmé |
| `SC-CROSS-006-0` | flync_4_app, flync_4_signal | ✅ MODEL_ONLY | `AppBindings`, `ServiceProviderReference`, `Signal`, `SignalDataType` | — | ⚠️ non confirmé |
| `SC-CROSS-007-0` | flync_4_app, flync_4_someip | ✅ MODEL_ONLY | `AppBindings`, `SOMEIPConfig`, `ServiceConsumerReference` | — | ⚠️ non confirmé |
| `SC-CROSS-008-0` | flync_4_app, flync_4_topology | ✅ MODEL_ONLY | `AppBindings`, `ExternalConnection`, `ServiceConsumerReference`, `ServiceProviderReference` | — | ⚠️ non confirmé |
| `SC-CROSS-009-0` | flync_4_app, flync_4_tsn | ✅ MODEL_ONLY | `ATSInstance`, `AppBindings`, `ServiceProviderReference`, `SingleRateTwoColorMarker`, `Stream` | — | ⚠️ non confirmé |
| `SC-CROSS-010-0` | flync_4_bus, flync_4_communication | ✅ MODEL_ONLY | `CANBus`, `FLYNCChannelConfig`, `FLYNCCommunicationConfig` | — | ✅ |
| `SC-CROSS-011-0` | flync_4_bus, flync_4_ecu | ✅ MODEL_ONLY | `CANBus`, `ECUPort` | — | ⚠️ non confirmé |
| `SC-CROSS-012-0` | flync_4_bus, flync_4_metadata | ✅ MODEL_ONLY | `CANBus`, `ECUMetadata` | — | ⚠️ non confirmé |
| `SC-CROSS-013-0` | flync_4_bus, flync_4_nm | ✅ MODEL_ONLY | `CANBus`, `StateManagementGroup` | — | ✅ |
| `SC-CROSS-014-0` | flync_4_bus, flync_4_security | ✅ MODEL_ONLY | `CANBus`, `Firewall`, `FirewallRule` | — | ⚠️ non confirmé |
| `SC-CROSS-015-0` | flync_4_bus, flync_4_signal | ✅ MODEL_ONLY | `CANBus`, `Frame`, `Signal`, `SignalDataType`, `SignalInstance` | — | ✅ |
| `SC-CROSS-016-0` | flync_4_bus, flync_4_someip | ✅ MODEL_ONLY | `Layer4Endpoint`, `SDConfig`, `SOMEIPConfig`, `SOMEIPServiceDeployment` | — | ⚠️ non confirmé |
| `SC-CROSS-017-0` | flync_4_bus, flync_4_topology | ✅ MODEL_ONLY | `CANBus`, `ExternalConnection` | — | ✅ |
| `SC-CROSS-018-0` | flync_4_bus, flync_4_tsn | ✅ MODEL_ONLY | `CANBus`, `FrameFilter`, `SingleRateTwoColorMarker`, `Stream` | — | ⚠️ non confirmé |
| `SC-CROSS-019-0` | flync_4_communication, flync_4_ecu | ✅ MODEL_ONLY | `TCPOption`, `FLYNCCommunicationConfig` | — | ✅ |
| `SC-CROSS-020-0` | flync_4_communication, flync_4_metadata | ✅ MODEL_ONLY | `ECUMetadata`, `FLYNCChannelConfig`, `FLYNCCommunicationConfig`, `SystemMetadata` | — | ⚠️ non confirmé |
| `SC-CROSS-021-0` | flync_4_communication, flync_4_nm | ✅ MODEL_ONLY | `StateManagementConfig`, `FLYNCChannelConfig`, `StateManagementGroup` | — | ✅ |
| `SC-CROSS-022-0` | flync_4_communication, flync_4_security | ✅ MODEL_ONLY | `FLYNCCommunicationConfig`, `Firewall`, `FirewallRule` | — | ⚠️ non confirmé |
| `SC-CROSS-023-0` | flync_4_communication, flync_4_signal | ✅ MODEL_ONLY | `FLYNCChannelConfig`, `Signal`, `SignalDataType`, `SignalInstance` | — | ✅ |
| `SC-CROSS-024-0` | flync_4_communication, flync_4_someip | ✅ MODEL_ONLY | `SOMEIPConfig`, `FLYNCChannelConfig`, `FLYNCCommunicationConfig`, `SDConfig`, `SDTimings` | — | ✅ |
| `SC-CROSS-025-0` | flync_4_communication, flync_4_topology | ✅ MODEL_ONLY | `ExternalConnection`, `FLYNCChannelConfig` | — | ⚠️ non confirmé |
| `SC-CROSS-026-0` | flync_4_communication, flync_4_tsn | ✅ MODEL_ONLY | `ATSInstance`, `FLYNCChannelConfig`, `SingleRateTwoColorMarker`, `Stream` | — | ⚠️ non confirmé |
| `SC-CROSS-027-0` | flync_4_ecu, flync_4_metadata | ✅ MODEL_ONLY | `ECUMetadata`, `EmbeddedMetadata`, `Controller` | — | ✅ |
| `SC-CROSS-028-0` | flync_4_ecu, flync_4_nm | ✅ MODEL_ONLY | `GroupTiming`, `StateManagementConfig`, `StateManagementGroup` | — | ✅ |
| `SC-CROSS-029-0` | flync_4_ecu, flync_4_security | ✅ MODEL_ONLY | `Firewall`, `ECUPort`, `FirewallRule` | — | ✅ |
| `SC-CROSS-030-0` | flync_4_ecu, flync_4_signal | ✅ MODEL_ONLY | `ECUPort`, `Signal`, `SignalDataType`, `SignalInstance` | — | ✅ |
| `SC-CROSS-031-0` | flync_4_ecu, flync_4_someip | ✅ MODEL_ONLY | `Controller`, `ECUPort`, `SOMEIPConfig` | — | ✅ |
| `SC-CROSS-032-0` | flync_4_ecu, flync_4_topology | ✅ MODEL_ONLY | `ECUPort`, `ExternalConnection` | — | ✅ |
| `SC-CROSS-033-0` | flync_4_ecu, flync_4_tsn | ✅ MODEL_ONLY | `PTPConfig`, `ECUPort`, `PTPPort` | — | ✅ |
| `SC-CROSS-034-0` | flync_4_metadata, flync_4_nm | ✅ MODEL_ONLY | `ECUMetadata`, `GroupTiming`, `StateManagementConfig`, `StateManagementGroup` | — | ⚠️ non confirmé |
| `SC-CROSS-036-0` | flync_4_metadata, flync_4_signal | ✅ MODEL_ONLY | `ECUMetadata`, `Signal`, `SignalDataType`, `SignalInstance`, `SystemMetadata` | — | ⚠️ non confirmé |
| `SC-CROSS-037-0` | flync_4_metadata, flync_4_someip | ✅ MODEL_ONLY | `ECUMetadata`, `Layer4Endpoint`, `SOMEIPConfig` | — | ✅ |
| `SC-CROSS-038-0` | flync_4_metadata, flync_4_topology | ✅ MODEL_ONLY | `ECUMetadata`, `ExternalConnection` | — | ⚠️ non confirmé |
| `SC-CROSS-039-0` | flync_4_metadata, flync_4_tsn | ✅ MODEL_ONLY | `ECUMetadata`, `EmbeddedMetadata`, `PTPConfig`, `PTPPort` | — | ⚠️ non confirmé |
| `SC-CROSS-040-0` | flync_4_nm, flync_4_security | ✅ MODEL_ONLY | `Firewall`, `FirewallRule`, `StateManagementGroup` | — | ⚠️ non confirmé |
| `SC-CROSS-041-0` | flync_4_nm, flync_4_signal | ✅ MODEL_ONLY | `Signal`, `SignalDataType`, `SignalInstance`, `StateManagementGroup` | — | ⚠️ non confirmé |
| `SC-CROSS-042-0` | flync_4_nm, flync_4_someip | ✅ MODEL_ONLY | `GroupTiming`, `SDConfig`, `SDTimings`, `SOMEIPConfig`, `SleepTiming`, `StateManagementConfig`, `StateManagementGroup` | — | ⚠️ non confirmé |
| `SC-CROSS-043-0` | flync_4_nm, flync_4_topology | ✅ MODEL_ONLY | `ExternalConnection`, `FLYNCTopology`, `StateManagementConfig`, `StateManagementGroup` | — | ⚠️ non confirmé |
| `SC-CROSS-044-0` | flync_4_nm, flync_4_tsn | ✅ MODEL_ONLY | `GroupTiming`, `SingleRateTwoColorMarker`, `StateManagementGroup`, `Stream` | — | ⚠️ non confirmé |
| `SC-CROSS-045-0` | flync_4_security, flync_4_signal | ✅ MODEL_ONLY | `FirewallRule`, `Signal`, `SignalDataType` | — | ⚠️ non confirmé |
| `SC-CROSS-046-0` | flync_4_security, flync_4_someip | ✅ MODEL_ONLY | `Firewall`, `FirewallRule`, `SDConfig`, `SOMEIPConfig` | — | ⚠️ non confirmé |
| `SC-CROSS-047-0` | flync_4_security, flync_4_topology | ✅ MODEL_ONLY | `ExternalConnection`, `Firewall`, `FirewallRule` | — | ⚠️ non confirmé |
| `SC-CROSS-048-0` | flync_4_security, flync_4_tsn | ✅ MODEL_ONLY | `IntegrityWithConfidentiality`, `MACsecConfig`, `PTPConfig`, `PTPPort`, `PTPTimeTransmitterConfig` | — | ✅ |
| `SC-CROSS-049-0` | flync_4_signal, flync_4_someip | ✅ MODEL_ONLY | `SOMEIPConfig`, `Signal`, `SignalDataType`, `SignalInstance` | — | ⚠️ non confirmé |
| `SC-CROSS-050-0` | flync_4_signal, flync_4_topology | ✅ MODEL_ONLY | `ExternalConnection`, `Signal`, `SignalDataType`, `SignalInstance` | — | ⚠️ non confirmé |
| `SC-CROSS-051-0` | flync_4_signal, flync_4_tsn | ✅ MODEL_ONLY | `Frame`, `FrameFilter`, `Signal`, `SignalDataType`, `SignalInstance`, `Stream` | — | ⚠️ non confirmé |
| `SC-CROSS-052-0` | flync_4_someip, flync_4_topology | ✅ MODEL_ONLY | `ExternalConnection`, `FLYNCTopology`, `SDConfig`, `SDTimings`, `SOMEIPConfig` | — | ⚠️ non confirmé |
| `SC-CROSS-053-0` | flync_4_someip, flync_4_tsn | ✅ MODEL_ONLY | `FrameFilter`, `SDConfig`, `SDTimings`, `SingleRateTwoColorMarker`, `Stream` | — | ⚠️ non confirmé |
| `SC-CROSS-054-0` | flync_4_topology, flync_4_tsn | ✅ MODEL_ONLY | `ExternalConnection`, `PTPConfig`, `PTPPdelayConfig`, `PTPPort`, `PTPTimeReceiverConfig`, `PTPTimeTransmitterConfig` | — | ⚠️ non confirmé |

**Résumé : 130 model-only, 1 requièrent le SDK, 22 non résolus.**

## Entités écartées hors périmètre (faux positifs de nom, hors module déclaré)

- `SC-BUS-004` : `Frame`
- `SC-BUS-005` : `Frame`
- `SC-COMMUNICATION-002` : `TCPOption`
- `SC-COMMUNICATION-003` : `UDPOption`
- `SC-COMMUNICATION-005` : `TCPOption`
- `SC-COMMUNICATION-006` : `Layer4Endpoint`, `UDPOption`
- `SC-COMMUNICATION-008` : `TCPOption`
- `SC-COMMUNICATION-009` : `UDPOption`
- `SC-COMMUNICATION-010` : `MultiplexedPDU`
- `SC-SECURITY-004` : `Frame`
- `SC-SIGNAL-005` : `Bitfield`
- `SC-CROSS-000-0` : `Controller`
- `SC-CROSS-003-0` : `Controller`
- `SC-CROSS-004-0` : `Controller`
- `SC-CROSS-005-0` : `Controller`, `Drop`
- `SC-CROSS-008-0` : `Controller`
- `SC-CROSS-009-0` : `Controller`
- `SC-CROSS-010-0` : `Frame`
- `SC-CROSS-013-0` : `Frame`
- `SC-CROSS-018-0` : `Frame`
- `SC-CROSS-022-0` : `Socket`, `TCPOption`
- `SC-CROSS-024-0` : `TCPOption`
- `SC-CROSS-037-0` : `Socket`
- `SC-CROSS-039-0` : `Controller`
- `SC-CROSS-040-0` : `Controller`

## Classes-pont priorisées (scénarios cross-module)

- `SC-CROSS-002-0` : `AppBindings`
- `SC-CROSS-010-0` : `CANBus`
- `SC-CROSS-017-0` : `CANBus`
- `SC-CROSS-019-0` : `TCPOption`
- `SC-CROSS-021-0` : `StateManagementConfig`
- `SC-CROSS-024-0` : `SOMEIPConfig`
- `SC-CROSS-027-0` : `ECUMetadata`, `EmbeddedMetadata`
- `SC-CROSS-029-0` : `Firewall`
- `SC-CROSS-032-0` : `ECUPort`
- `SC-CROSS-033-0` : `PTPConfig`

## Validators réels des classes trouvées, par scénario

⚠️ Une classe trouvée ne veut pas dire que LA règle métier décrite existe — seulement que la classe existe. Compare la liste de validators ci-dessous au `expected_result` du scénario pour juger si la règle a une chance d'y être.

**`SC-APP-001`** — *Validation succeeds; both ServiceProviderReference and ServiceConsumerReference resolve to existing services and the App is bound to the specified ECU controller without errors.*
- `ServiceConsumerReference` → (aucun validator)
- `ServiceProviderReference` → (aucun validator)

**`SC-APP-002`** — *Validation fails with error code DanglingServiceConsumerReference indicating the referenced service cannot be resolved.*
- `ServiceConsumerReference` → (aucun validator)
- `ServiceProviderReference` → (aucun validator)

**`SC-APP-003`** — *Validation succeeds; AppBindings correctly links the App to the ECU controller and the App identifier is confirmed unique system‑wide.*
- `AppBindings` → (aucun validator)

**`SC-APP-005`** — *Validation succeeds; ServiceProviderReference resolves to an existing service definition.*
- `ServiceProviderReference` → (aucun validator)

**`SC-APP-006`** — *Validation fails with error code PortNumberOutOfRange indicating the port number must be within 0‑65535.*
- `ServiceProviderReference` → (aucun validator)

**`SC-APP-007`** — *Validation succeeds; the App is deployed to all specified controllers and the App identifier remains unique system‑wide.*
- `AppBindings` → (aucun validator)

**`SC-APP-008`** — *Validation fails with error code MissingAppBindings indicating the App has no binding to any ECU controller.*
- `AppBindings` → (aucun validator)

**`SC-APP-009`** — *Validation succeeds; ServiceConsumerReference resolves to the existing service without errors.*
- `ServiceConsumerReference` → (aucun validator)
- `ServiceProviderReference` → (aucun validator)

**`SC-COMMUNICATION-001`** — *Validator returns success; no errors are reported and the FLYNCChannelConfig instance is created with the provided bus and PDU definitions.*
- `FLYNCChannelConfig` → validate_pdus_name_unique, validate_canbus_name_unique, validate_linbus_name_unique, validate_pdu_refs

**`SC-COMMUNICATION-004`** — *Validation fails with error BUS_BITRATE_OUT_OF_RANGE indicating that the specified bitrate (5 Mbit/s) is above the permitted maximum.*
- `FLYNCChannelConfig` → validate_pdus_name_unique, validate_canbus_name_unique, validate_linbus_name_unique, validate_pdu_refs

**`SC-ECU-001`** — *Validator returns success; no errors are reported for ECU, ECUPort, or Controller definitions.*
- `Controller` → reject_legacy_controller_layout, require_at_least_one_interface, validate_unique_interface_names, check_ports_virtual_switch_are_interfaces_or_compute_nodes
- `ECUPort` → verify_mdi_and_mii_config_have_same_speed

**`SC-ECU-002`** — *Validator fails with error indicating duplicate ECUPort identifier 'portA'.*
- `ECUPort` → verify_mdi_and_mii_config_have_same_speed

**`SC-ECU-003`** — *Validator returns success; VirtualSwitch and VirtualSwitchPort are accepted.*
- `Switch` → validate_unique_port_number, validate_unique_port_names, validate_ipv_mapping, validate_ats_instances, validate_ports_in_tcam_exist, validate_tcam_ids_unique, validate_tcam_name_unique
- `VirtualSwitch` → experimental_warning
- `VirtualSwitchPort` → (aucun validator)

**`SC-ECU-004`** — *Validator fails, reporting 'VLAN ID 5000 out of range (must be 1‑4094)' for the Switch configuration.*
- `Switch` → validate_unique_port_number, validate_unique_port_names, validate_ipv_mapping, validate_ats_instances, validate_ports_in_tcam_exist, validate_tcam_ids_unique, validate_tcam_name_unique

**`SC-ECU-005`** — *Validator returns success; Socket and IPv4AddressEndpoint pass validation.*
- `IPv4AddressEndpoint` → check_if_sockets_have_the_same_ip
- `Socket` → drop_invalid_deployment, validate_unique_forwarder_per_pdu

**`SC-ECU-006`** — *Validator fails, reporting 'Missing mandatory controllers directory for ECU' error.*
- `Controller` → reject_legacy_controller_layout, require_at_least_one_interface, validate_unique_interface_names, check_ports_virtual_switch_are_interfaces_or_compute_nodes

**`SC-ECU-007`** — *Validator returns success; EthernetInterface and its MII configuration are accepted.*
- `EthernetInterface` → (aucun validator)

**`SC-ECU-008`** — *Validator fails, reporting 'Classic CAN DLC 12 exceeds maximum of 8 bytes' error.*
- `CANInterface` → validate_forwarder_frame_uniqueness

**`SC-ECU-009`** — *Validator returns success; LINMasterInterface passes validation.*
- `LINMasterInterface` → (aucun validator)

**`SC-ECU-010`** — *Validator fails, reporting 'Multicast group VLAN 100 not defined in any Switch configuration' error.*
- `Switch` → validate_unique_port_number, validate_unique_port_names, validate_ipv_mapping, validate_ats_instances, validate_ports_in_tcam_exist, validate_tcam_ids_unique, validate_tcam_name_unique
- `VirtualSwitch` → experimental_warning

**`SC-METADATA-001`** — *Validation succeeds; no errors are reported.*
- `SystemMetadata` → (aucun validator)

**`SC-METADATA-002`** — *Validation fails with DuplicateIdentifierError indicating identifier 'ECU_A' is already used.*
- `ECUMetadata` → (aucun validator)

**`SC-METADATA-003`** — *Validation succeeds; version string is parsed as a valid Semantic Version.*
- `BaseVersion` → validate_and_parse_version

**`SC-METADATA-004`** — *Validation fails with VersionParseError indicating the version 'v1' is invalid.*
- `HardwareBaseMetadata` → (aucun validator)

**`SC-METADATA-005`** — *Validation succeeds; parent_ecu_id resolves to an existing ECUMetadata.*
- `ECUMetadata` → (aucun validator)
- `EmbeddedMetadata` → (aucun validator)

**`SC-METADATA-007`** — *Validation succeeds; version string is recognized as a valid PEP 440 version.*
- `SystemMetadata` → (aucun validator)

**`SC-METADATA-008`** — *Validation fails with MissingFieldError indicating that 'system_id' is required.*
- `ECUMetadata` → (aucun validator)

**`SC-METADATA-009`** — *Validation succeeds; version string parses as a valid Semantic Version.*
- `BaseMetadata` → (aucun validator)

**`SC-NM-001`** — *Validation succeeds; the StateManagementGroup is accepted and its derived membership list matches the StateMembershipRef entries declared on the entities.*
- `StateManagementGroup` → (aucun validator)
- `StateMembershipRef` → observer_owns_no_bit, no_duplicate_bits

**`SC-NM-002`** — *Validation fails with error "DuplicateGroupNameError" indicating that the group name "VEHICLE" is used more than once.*
- `StateManagementGroup` → (aucun validator)

**`SC-NM-003`** — *Validation succeeds; all timing values are within allowed ranges and the GroupTiming object is accepted.*
- `GroupTiming` → check_consistency

**`SC-NM-004`** — *Validation fails with error "InvalidCycleTimeError" because cycle_time_ms is negative.*
- `GroupTiming` → check_consistency

**`SC-NM-005`** — *Validation succeeds; the StateMembershipRef is accepted and the relevance bits are resolved correctly.*
- `StateMembershipRef` → observer_owns_no_bit, no_duplicate_bits

**`SC-NM-007`** — *Validation succeeds; both timeout_ms and wait_before_sleep_ms are within the allowed non‑negative range.*
- `SleepTiming` → (aucun validator)

**`SC-NM-008`** — *Validation fails with error "InvalidTimeoutError" because timeout_ms is negative.*
- `SleepTiming` → (aucun validator)

**`SC-NM-009`** — *Validation succeeds; all announcement timing fields are within their permitted ranges.*
- `AnnouncementPhaseTiming` → check_burst_pair

**`SC-NM-010`** — *Validation fails with error "InvalidBurstCountError" because burst_count cannot be negative.*
- `AnnouncementPhaseTiming` → check_burst_pair

**`SC-SECURITY-001`** — *Validation succeeds; the MACsecConfig instance is created and its confidentiality flag is set to true.*
- `IntegrityWithConfidentiality` → (aucun validator)
- `MACsecConfig` → validate_mka_macsecmode_disabled, validate_life_time_greater_than_hello_time

**`SC-SECURITY-002`** — *Validation fails with error message: "Destination port 70000 is outside the valid range 0‑65535."*
- `FirewallRule` → validate_pattern

**`SC-SECURITY-003`** — *Validation succeeds; the MACsecConfig instance is created and its confidentiality flag is set to false.*
- `IntegrityWithoutConfidentiality` → (aucun validator)
- `MACsecConfig` → validate_mka_macsecmode_disabled, validate_life_time_greater_than_hello_time

**`SC-SECURITY-004`** — *Validation fails with error message: "Duplicate firewall rule detected – identical match criteria already exist."*
- `FirewallRule` → validate_pattern

**`SC-SECURITY-005`** — *Validation succeeds; the Firewall is created containing the three distinct rules.*
- `Firewall` → check_duplicate_rules
- `FirewallRule` → validate_pattern

**`SC-SECURITY-006`** — *Validation fails with error message: "Integrity mode reference is dangling – referenced object does not exist."*
- `IntegrityWithConfidentiality` → (aucun validator)
- `MACsecConfig` → validate_mka_macsecmode_disabled, validate_life_time_greater_than_hello_time

**`SC-SECURITY-007`** — *Validation succeeds; the rule is accepted as a valid FirewallRule.*
- `FirewallRule` → validate_pattern

**`SC-SECURITY-009`** — *Validation succeeds; the Firewall is created containing the single valid rule.*
- `Firewall` → check_duplicate_rules
- `FirewallRule` → validate_pattern

**`SC-SIGNAL-001`** — *Validator accepts the Signal; no errors are reported.*
- `Signal` → _factor_nonzero, _validate_bit_length_for_data_type, _validate_limits, _validate_initial_value, _validate_value_encoding

**`SC-SIGNAL-002`** — *Validator rejects the Signal with an error indicating that bit_length (20) exceeds the natural bit width of UINT16 (16).*
- `Signal` → _factor_nonzero, _validate_bit_length_for_data_type, _validate_limits, _validate_initial_value, _validate_value_encoding

**`SC-SIGNAL-003`** — *Validator accepts the Signal; the text_table entries are stored without overlap or missing fields.*
- `Signal` → _factor_nonzero, _validate_bit_length_for_data_type, _validate_limits, _validate_initial_value, _validate_value_encoding

**`SC-SIGNAL-004`** — *Validator reports a duplicate identifier error for Signal name 'VehicleSpeed'.*
- `Signal` → _factor_nonzero, _validate_bit_length_for_data_type, _validate_limits, _validate_initial_value, _validate_value_encoding

**`SC-SIGNAL-005`** — *Validator accepts the Signal; each BitfieldGroup mask is disjoint and each group's states are non‑overlapping, allowing correct decoding.*
- `BitfieldGroup` → _validate_states
- `Signal` → _factor_nonzero, _validate_bit_length_for_data_type, _validate_limits, _validate_initial_value, _validate_value_encoding

**`SC-SIGNAL-006`** — *Validator rejects the Signal with an error indicating that flag masks are not disjoint (FlagA and FlagB overlap).*
- `Signal` → _factor_nonzero, _validate_bit_length_for_data_type, _validate_limits, _validate_initial_value, _validate_value_encoding

**`SC-SIGNAL-007`** — *Validator accepts the Signal; linear conversion (raw*0.5‑40) is applied to raw values not covered by the text_table, and limits are respected.*
- `Signal` → _factor_nonzero, _validate_bit_length_for_data_type, _validate_limits, _validate_initial_value, _validate_value_encoding

**`SC-SIGNAL-008`** — *Validator rejects the SignalInstance with an error indicating placement exceeds the owning Signal's bit length (bits 5‑12 out of range for an 8‑bit signal).*
- `Signal` → _factor_nonzero, _validate_bit_length_for_data_type, _validate_limits, _validate_initial_value, _validate_value_encoding
- `SignalInstance` → (aucun validator)

**`SC-SIGNAL-009`** — *Validator accepts the Signal; raw value 65535 is interpreted as 'Signal_Not_Available', all other raw values are converted using the linear formula and fall within the expected physical range.*
- `Signal` → _factor_nonzero, _validate_bit_length_for_data_type, _validate_limits, _validate_initial_value, _validate_value_encoding

**`SC-SIGNAL-010`** — *Validator rejects the Signal with an error indicating that the value_encoding entry is missing the required field 'label'.*
- `Signal` → _factor_nonzero, _validate_bit_length_for_data_type, _validate_limits, _validate_initial_value, _validate_value_encoding

**`SC-SOMEIP-001`** — *Validation succeeds; the interface is accepted and can be referenced by providers and consumers.*
- `SOMEIPServiceInterface` → resolve_eventgroup_event_refs, validate_for_notifiers_without_eventgroup, validate_service_owns_elements_of_eventgroups, validate_all_identifiers_to_be_unique

**`SC-SOMEIP-002`** — *Validation fails with error "Service Identifier 0x2000 is already used by another SOMEIPServiceInterface" and the second interface is rejected.*
- `SOMEIPServiceInterface` → resolve_eventgroup_event_refs, validate_for_notifiers_without_eventgroup, validate_service_owns_elements_of_eventgroups, validate_all_identifiers_to_be_unique

**`SC-SOMEIP-003`** — *Validation succeeds; the method is added to the service interface without errors.*
- `SOMEIPRequestResponseMethod` → (aucun validator)

**`SC-SOMEIP-004`** — *Validation fails with error "Eventgroup EngineEvents references undefined event EngineOverheat".*
- `SOMEIPEvent` → (aucun validator)
- `SOMEIPEventgroup` → (aucun validator)

**`SC-SOMEIP-005`** — *Validation succeeds; the field is accepted and its getter/setter are linked.*
- `SOMEIPField` → validate_at_least_one_identifier_to_be_defined

**`SC-SOMEIP-006`** — *Validation fails with error "SOMEIPServiceDeployment for service 0x3000 references undefined Layer4Endpoint ECU1_EP".*
- `Layer4Endpoint` → (aucun validator)
- `SOMEIPServiceDeployment` → (aucun validator)

**`SC-SOMEIP-007`** — *Validation succeeds; the SDConfig is accepted and can be used for service discovery.*
- `SDConfig` → (aucun validator)

**`SC-SOMEIP-009`** — *Validation succeeds; the provider is linked to the interface and endpoint.*
- `Layer4Endpoint` → (aucun validator)
- `SOMEIPServiceInterface` → resolve_eventgroup_event_refs, validate_for_notifiers_without_eventgroup, validate_service_owns_elements_of_eventgroups, validate_all_identifiers_to_be_unique
- `SOMEIPServiceProvider` → (aucun validator)

**`SC-SOMEIP-010`** — *Validation fails with error "SOMEIPServiceConsumer references undefined service interface NonExistentService".*
- `SOMEIPServiceConsumer` → (aucun validator)
- `SOMEIPServiceInterface` → resolve_eventgroup_event_refs, validate_for_notifiers_without_eventgroup, validate_service_owns_elements_of_eventgroups, validate_all_identifiers_to_be_unique

**`SC-TOPOLOGY-001`** — *Validation succeeds, reporting that the SystemTopology is correctly configured with a valid ExternalConnection.*
- `ExternalConnection` → (aucun validator)

**`SC-TOPOLOGY-002`** — *Validation fails, reporting that the ExternalConnection type is invalid and must be 'ecu_port_to_ecu_port'.*
- `ExternalConnection` → (aucun validator)

**`SC-TOPOLOGY-005`** — *Validation fails, reporting that the ECU reference is missing and must be a valid ECU identifier.*
- `ExternalConnection` → (aucun validator)

**`SC-TSN-001`** — *PTPConfig passes schema validation and can be instantiated without errors.*
- `PTPConfig` → (aucun validator)
- `PTPTimeReceiverConfig` → (aucun validator)
- `PTPTimeTransmitterConfig` → (aucun validator)

**`SC-TSN-002`** — *Validation raises an error stating that 'port_number' must be between 0 and 65535; value 70000 is out of range.*
- `PTPPort` → (aucun validator)

**`SC-TSN-003`** — *CBSShaper passes validation; idleCredit and sendCredit are accepted and the object can be used for traffic shaping.*
- `CBSShaper` → (aucun validator)

**`SC-TSN-004`** — *Validation fails with a duplicate identifier error: ATSInstance id 'ats1' is already defined.*
- `ATSInstance` → (aucun validator)

**`SC-TSN-005`** — *TrafficClass passes validation; priority is within 0‑7 and bandwidth reservation does not exceed the link capacity.*
- `TrafficClass` → validate_priority_values, validate_at_least_one_prio_list

**`SC-TSN-006`** — *Validation fails with an error indicating that 'maxBurst' exceeds the maximum allowed size of 1,000,000 bytes (value 2,000,000).*
- `HTBInstance` → validate_htb_config

**`SC-TSN-007`** — *FrameFilter passes validation; filter criteria are syntactically correct and can be applied.*
- `FrameFilter` → validate_vlanids, validate_pcps, validate_port_mac, validate_port_assignment

**`SC-TSN-008`** — *Validation fails with an error stating that the Stream rate (10 Gbps) exceeds the maximum permitted rate of 1 Gbps.*
- `Stream` → (aucun validator)

**`SC-TSN-009`** — *SingleRateTwoColorMarker passes validation; thresholds are accepted and the marker can be used for traffic policing.*
- `SingleRateTwoColorMarker` → (aucun validator)
- `TrafficClass` → validate_priority_values, validate_at_least_one_prio_list

**`SC-TSN-010`** — *Validation fails with an error indicating that the DoubleRateThreeColorMarker is missing a required reference to a TrafficClass.*
- `DoubleRateThreeColorMarker` → (aucun validator)
- `TrafficClass` → validate_priority_values, validate_at_least_one_prio_list

**`SC-CROSS-000-0`** — *The configuration validator successfully resolves the mapping, verifying that the App is bound to a controller that is a valid participating node on the CANBus and can transmit the referenced inline frames without any dangling references.*
- `AppBindings` → (aucun validator)
- `CANBus` → validate_baud_rate, validate_fd_configuration, validate_can_fd_frames_require_fd_enabled, validate_unique_can_ids
- `ServiceProviderReference` → (aucun validator)

**`SC-CROSS-001-0`** — *Validation fails with a dangling reference error, indicating that the ServiceConsumerReference in the App points to a service identifier that does not exist in the FLYNCCommunicationConfig.*
- `FLYNCCommunicationConfig` → (aucun validator)
- `ServiceConsumerReference` → (aucun validator)

**`SC-CROSS-002-0`** — *The configuration validation succeeds, confirming that the App is successfully bound to the specified ECU Controller and its ServiceProviderReference is correctly resolved.*
- `AppBindings` → (aucun validator)
- `Controller` → reject_legacy_controller_layout, require_at_least_one_interface, validate_unique_interface_names, check_ports_virtual_switch_are_interfaces_or_compute_nodes
- `ServiceProviderReference` → (aucun validator)

**`SC-CROSS-003-0`** — *Configuration validation fails, reporting a dangling reference error because the controller hosting the bound App references an undefined parent ECU identifier.*
- `AppBindings` → (aucun validator)
- `ECUMetadata` → (aucun validator)
- `EmbeddedMetadata` → (aucun validator)

**`SC-CROSS-004-0`** — *The configuration validator successfully processes the AppBindings and derives the controller's membership in the StateManagementGroup, verifying that the hosted App's communication is backed by the active NM group timing profile without errors.*
- `AppBindings` → (aucun validator)
- `GroupTiming` → check_consistency
- `ServiceProviderReference` → (aucun validator)
- `StateManagementConfig` → validate_unique_names
- `StateManagementGroup` → (aucun validator)

**`SC-CROSS-005-0`** — *Configuration validation fails, reporting a port conflict where the ServiceProviderReference port is blocked by a Drop action in the FirewallRule of the bound ECU controller.*
- `AppBindings` → (aucun validator)
- `Firewall` → check_duplicate_rules
- `FirewallRule` → validate_pattern
- `ServiceProviderReference` → (aucun validator)

**`SC-CROSS-006-0`** — *The configuration is successfully validated, confirming that the App is correctly bound to the controller via AppBindings and its associated ServiceProviderReference successfully maps to the transport service carrying the valid UINT16 Signal.*
- `AppBindings` → (aucun validator)
- `ServiceProviderReference` → (aucun validator)
- `Signal` → _factor_nonzero, _validate_bit_length_for_data_type, _validate_limits, _validate_initial_value, _validate_value_encoding
- `SignalDataType` → (aucun validator)

**`SC-CROSS-007-0`** — *Configuration validation fails with a dangling reference error, reporting that the service interface referenced by the App's ServiceConsumerReference does not exist in the SOME/IP configuration.*
- `AppBindings` → (aucun validator)
- `SOMEIPConfig` → validate_all_e2e_identifiers_to_be_unique, validate_timing_exist
- `ServiceConsumerReference` → (aucun validator)

**`SC-CROSS-008-0`** — *The configuration validates successfully, confirming that the service consumer App and service provider App are bound to controllers on ECUs that are physically connected via a declared ExternalConnection in the SystemTopology.*
- `AppBindings` → (aucun validator)
- `ExternalConnection` → (aucun validator)
- `ServiceConsumerReference` → (aucun validator)
- `ServiceProviderReference` → (aucun validator)

**`SC-CROSS-009-0`** — *Configuration validation fails, reporting a deployment mismatch between the App's controller binding in AppBindings and the controller interface hosting the TSN Stream.*
- `ATSInstance` → (aucun validator)
- `AppBindings` → (aucun validator)
- `ServiceProviderReference` → (aucun validator)
- `SingleRateTwoColorMarker` → (aucun validator)
- `Stream` → (aucun validator)

**`SC-CROSS-010-0`** — *The configuration validation succeeds, confirming that the FLYNCChannelConfig correctly resolves the pdu_ref in the CANBus inline frame to the corresponding PDU definition under the pdus directory.*
- `CANBus` → validate_baud_rate, validate_fd_configuration, validate_can_fd_frames_require_fd_enabled, validate_unique_can_ids
- `FLYNCChannelConfig` → validate_pdus_name_unique, validate_canbus_name_unique, validate_linbus_name_unique, validate_pdu_refs
- `FLYNCCommunicationConfig` → (aucun validator)

**`SC-CROSS-011-0`** — *Validation fails with a reference error indicating that the ECU listed as a participating node in the CANBus configuration lacks a corresponding ECUPort in ports.flync.yaml.*
- `CANBus` → validate_baud_rate, validate_fd_configuration, validate_can_fd_frames_require_fd_enabled, validate_unique_can_ids
- `ECUPort` → verify_mdi_and_mii_config_have_same_speed

**`SC-CROSS-012-0`** — *The configuration validation succeeds, verifying that the participating node on the CANBus correctly resolves to the defined ECUMetadata identifier with no dangling references.*
- `CANBus` → validate_baud_rate, validate_fd_configuration, validate_can_fd_frames_require_fd_enabled, validate_unique_can_ids
- `ECUMetadata` → (aucun validator)

**`SC-CROSS-013-0`** — *Validation fails, reporting that the CANBus is declared as a member of the StateManagementGroup but does not route the group's designated NM PDU.*
- `CANBus` → validate_baud_rate, validate_fd_configuration, validate_can_fd_frames_require_fd_enabled, validate_unique_can_ids
- `StateManagementGroup` → (aucun validator)

**`SC-CROSS-014-0`** — *The configuration validation succeeds with zero errors, confirming that the FirewallRule's ECU identifier successfully resolves to the active participating node defined within the CANBus configuration.*
- `CANBus` → validate_baud_rate, validate_fd_configuration, validate_can_fd_frames_require_fd_enabled, validate_unique_can_ids
- `Firewall` → check_duplicate_rules
- `FirewallRule` → validate_pattern

**`SC-CROSS-015-0`** — *Configuration validation fails, reporting that the total bit-width of the SignalInstance in the PDU referenced by the CANBus Frame exceeds the 8-byte limit for Classic CAN.*
- `CANBus` → validate_baud_rate, validate_fd_configuration, validate_can_fd_frames_require_fd_enabled, validate_unique_can_ids
- `Frame` → _validate_pdu_placements
- `Signal` → _factor_nonzero, _validate_bit_length_for_data_type, _validate_limits, _validate_initial_value, _validate_value_encoding
- `SignalDataType` → (aucun validator)
- `SignalInstance` → (aucun validator)

**`SC-CROSS-016-0`** — *The configuration validator successfully parses both submodels, verifying that the SOME/IP service deployment correctly resolves its target Layer4Endpoint to the valid IP address of the participating node defined on the Ethernet communication bus.*
- `Layer4Endpoint` → (aucun validator)
- `SDConfig` → (aucun validator)
- `SOMEIPConfig` → validate_all_e2e_identifiers_to_be_unique, validate_timing_exist
- `SOMEIPServiceDeployment` → (aucun validator)

**`SC-CROSS-017-0`** — *Validation fails with a configuration error indicating that the ExternalConnection between the CANBus participating nodes is not of type 'ecu_port_to_ecu_port'.*
- `CANBus` → validate_baud_rate, validate_fd_configuration, validate_can_fd_frames_require_fd_enabled, validate_unique_can_ids
- `ExternalConnection` → (aucun validator)

**`SC-CROSS-018-0`** — *The configuration validation passes successfully, confirming that the FrameFilter in flync_4_tsn correctly resolves the reference to the inline frame defined within the CANBus configuration of flync_4_bus.*
- `CANBus` → validate_baud_rate, validate_fd_configuration, validate_can_fd_frames_require_fd_enabled, validate_unique_can_ids
- `FrameFilter` → validate_vlanids, validate_pcps, validate_port_mac, validate_port_assignment
- `SingleRateTwoColorMarker` → (aucun validator)
- `Stream` → (aucun validator)

**`SC-CROSS-019-0`** — *Configuration validation fails, reporting a dangling reference error because the TCP profile imported by the ECU's TCPOption cannot be resolved in the FLYNCCommunicationConfig.*
- `TCPOption` → (aucun validator)
- `FLYNCCommunicationConfig` → (aucun validator)

**`SC-CROSS-020-0`** — *The FLYNC configuration parser successfully validates both the FLYNCCommunicationConfig and the SystemMetadata/ECUMetadata, verifying that the communication channels are correctly aligned with a valid system context and unique ECU identifiers without any duplicate-identifier or version-parsing errors.*
- `ECUMetadata` → (aucun validator)
- `FLYNCChannelConfig` → validate_pdus_name_unique, validate_canbus_name_unique, validate_linbus_name_unique, validate_pdu_refs
- `FLYNCCommunicationConfig` → (aucun validator)
- `SystemMetadata` → (aucun validator)

**`SC-CROSS-021-0`** — *Validation fails with a configuration error indicating that the PDU referenced by the StateManagementGroup must have its usage set to 'network_management' in the FLYNCChannelConfig.*
- `StateManagementConfig` → validate_unique_names
- `FLYNCChannelConfig` → validate_pdus_name_unique, validate_canbus_name_unique, validate_linbus_name_unique, validate_pdu_refs
- `StateManagementGroup` → (aucun validator)

**`SC-CROSS-022-0`** — *The configuration validator successfully verifies the FirewallRule, confirming that the destination port is within the valid 0-65535 range and correctly aligns with the active socket port defined in the FLYNCCommunicationConfig.*
- `FLYNCCommunicationConfig` → (aucun validator)
- `Firewall` → check_duplicate_rules
- `FirewallRule` → validate_pattern

**`SC-CROSS-023-0`** — *The configuration validator fails, reporting that the PDU size (80 bits) exceeds the 8-byte (64-bit) maximum payload limit for Classic CAN defined in the FLYNCChannelConfig.*
- `FLYNCChannelConfig` → validate_pdus_name_unique, validate_canbus_name_unique, validate_linbus_name_unique, validate_pdu_refs
- `Signal` → _factor_nonzero, _validate_bit_length_for_data_type, _validate_limits, _validate_initial_value, _validate_value_encoding
- `SignalDataType` → (aucun validator)
- `SignalInstance` → (aucun validator)

**`SC-CROSS-024-0`** — *The configuration generator successfully validates the model, verifying that the SOMEIPConfig service deployment correctly binds the SDTimings parameters and the TCPOption socket parameters without any unresolved references or validation errors.*
- `SOMEIPConfig` → validate_all_e2e_identifiers_to_be_unique, validate_timing_exist
- `FLYNCChannelConfig` → validate_pdus_name_unique, validate_canbus_name_unique, validate_linbus_name_unique, validate_pdu_refs
- `FLYNCCommunicationConfig` → (aucun validator)
- `SDConfig` → (aucun validator)
- `SDTimings` → (aucun validator)

**`SC-CROSS-025-0`** — *Configuration validation fails with a protocol mismatch error, indicating that the connected ports in the SystemTopology ExternalConnection must share compatible bus technologies in FLYNCChannelConfig.*
- `ExternalConnection` → (aucun validator)
- `FLYNCChannelConfig` → validate_pdus_name_unique, validate_canbus_name_unique, validate_linbus_name_unique, validate_pdu_refs

**`SC-CROSS-026-0`** — *The configuration validator successfully validates the network model, confirming that the Stream and ATSInstance from flync_4_tsn are correctly mapped to the Ethernet channel and frame definitions defined in FLYNCChannelConfig from flync_4_communication without any validation errors.*
- `ATSInstance` → (aucun validator)
- `FLYNCChannelConfig` → validate_pdus_name_unique, validate_canbus_name_unique, validate_linbus_name_unique, validate_pdu_refs
- `SingleRateTwoColorMarker` → (aucun validator)
- `Stream` → (aucun validator)

**`SC-CROSS-027-0`** — *Validation fails with a dangling reference error, indicating that the parent ECU identifier 'HPC_ECU_99' in the controller's EmbeddedMetadata does not resolve to any declared ECUMetadata identifier in the system configuration.*
- `ECUMetadata` → (aucun validator)
- `EmbeddedMetadata` → (aucun validator)
- `Controller` → reject_legacy_controller_layout, require_at_least_one_interface, validate_unique_interface_names, check_ports_virtual_switch_are_interfaces_or_compute_nodes

**`SC-CROSS-028-0`** — *Configuration validation succeeds, successfully deriving the ECU as a member of the StateManagementGroup and verifying that the timing profile parameters are correctly applied to the derived member.*
- `GroupTiming` → check_consistency
- `StateManagementConfig` → validate_unique_names
- `StateManagementGroup` → (aucun validator)

**`SC-CROSS-029-0`** — *Validation fails with a dangling reference error, explicitly stating that the ECUPort identifier referenced by the FirewallRule is undefined in the ECU Ports Config.*
- `Firewall` → check_duplicate_rules
- `ECUPort` → verify_mdi_and_mii_config_have_same_speed
- `FirewallRule` → validate_pattern

**`SC-CROSS-030-0`** — *The configuration validator successfully parses both submodels, confirming that the 16-bit SignalInstance fits within the PDU payload and is correctly mapped to the ECUPort without any validation errors.*
- `ECUPort` → verify_mdi_and_mii_config_have_same_speed
- `Signal` → _factor_nonzero, _validate_bit_length_for_data_type, _validate_limits, _validate_initial_value, _validate_value_encoding
- `SignalDataType` → (aucun validator)
- `SignalInstance` → (aucun validator)

**`SC-CROSS-031-0`** — *Configuration validation fails, reporting that the target ECU for the SOME/IP service deployment is invalid because it lacks the mandatory ECUPort configuration.*
- `Controller` → reject_legacy_controller_layout, require_at_least_one_interface, validate_unique_interface_names, check_ports_virtual_switch_are_interfaces_or_compute_nodes
- `ECUPort` → verify_mdi_and_mii_config_have_same_speed
- `SOMEIPConfig` → validate_all_e2e_identifiers_to_be_unique, validate_timing_exist

**`SC-CROSS-032-0`** — *The network configuration model successfully validates the system topology, resolving the ExternalConnection references to the declared ECUPort instances on both ECUs without any validation errors.*
- `ECUPort` → verify_mdi_and_mii_config_have_same_speed
- `ExternalConnection` → (aucun validator)

**`SC-CROSS-033-0`** — *Validation fails with a dangling reference error, stating that the PTPPort references an undefined ECUPort 'eth_tsn_0'.*
- `PTPConfig` → (aucun validator)
- `ECUPort` → verify_mdi_and_mii_config_have_same_speed
- `PTPPort` → (aucun validator)

**`SC-CROSS-034-0`** — *The configuration validates successfully, and the derived member set of the StateManagementGroup is resolved to contain the ECU identifier defined in ECUMetadata without any dangling references or validation errors.*
- `ECUMetadata` → (aucun validator)
- `GroupTiming` → check_consistency
- `StateManagementConfig` → validate_unique_names
- `StateManagementGroup` → (aucun validator)

**`SC-CROSS-036-0`** — *The configuration validation tool successfully parses both submodels, verifying that the SystemMetadata semantic version is valid, the ECU identifier is unique, and the Signal's SignalDataType is correctly resolved to 'UINT16' with no validation errors.*
- `ECUMetadata` → (aucun validator)
- `Signal` → _factor_nonzero, _validate_bit_length_for_data_type, _validate_limits, _validate_initial_value, _validate_value_encoding
- `SignalDataType` → (aucun validator)
- `SignalInstance` → (aucun validator)
- `SystemMetadata` → (aucun validator)

**`SC-CROSS-037-0`** — *Validation fails with a dangling reference error, indicating that the SOME/IP service deployment targets an ECU identifier not declared in any ECUMetadata configuration.*
- `ECUMetadata` → (aucun validator)
- `Layer4Endpoint` → (aucun validator)
- `SOMEIPConfig` → validate_all_e2e_identifiers_to_be_unique, validate_timing_exist

**`SC-CROSS-038-0`** — *The configuration passes validation successfully, verifying that the ECU identifiers referenced in the SystemTopology's ExternalConnection map to existing ECUMetadata declarations and the connection type is correctly set to 'ecu_port_to_ecu_port'.*
- `ECUMetadata` → (aucun validator)
- `ExternalConnection` → (aucun validator)

**`SC-CROSS-039-0`** — *Validation fails with a reference error, indicating that the PTPConfig cannot be resolved because the controller's EmbeddedMetadata contains a dangling reference to a non-existent parent ECU identifier.*
- `ECUMetadata` → (aucun validator)
- `EmbeddedMetadata` → (aucun validator)
- `PTPConfig` → (aucun validator)
- `PTPPort` → (aucun validator)

**`SC-CROSS-040-0`** — *The configuration validation succeeds, verifying that the network management PDU's destination port and IP address are correctly permitted by the FirewallRule within the Firewall configuration, allowing NM state management communication to proceed.*
- `Firewall` → check_duplicate_rules
- `FirewallRule` → validate_pattern
- `StateManagementGroup` → (aucun validator)

**`SC-CROSS-041-0`** — *Configuration validation fails, reporting that the StateManagementGroup's referenced NM PDU contains a SignalInstance with an invalid SignalDataType (FLOAT32) for network management usage.*
- `Signal` → _factor_nonzero, _validate_bit_length_for_data_type, _validate_limits, _validate_initial_value, _validate_value_encoding
- `SignalDataType` → (aucun validator)
- `SignalInstance` → (aucun validator)
- `StateManagementGroup` → (aucun validator)

**`SC-CROSS-042-0`** — *The configuration validation succeeds, verifying that the SOME/IP-SD cyclic transmission interval in SDTimings is compatible with the SleepTiming and GroupTiming cycle_time_ms, allowing both the flync_4_nm and flync_4_someip submodels to be successfully validated and generated.*
- `GroupTiming` → check_consistency
- `SDConfig` → (aucun validator)
- `SDTimings` → (aucun validator)
- `SOMEIPConfig` → validate_all_e2e_identifiers_to_be_unique, validate_timing_exist
- `SleepTiming` → (aucun validator)
- `StateManagementConfig` → validate_unique_names
- `StateManagementGroup` → (aucun validator)

**`SC-CROSS-043-0`** — *Validation fails with a cross-module error indicating that the derived member ECU of the StateManagementGroup lacks a valid ExternalConnection in the SystemTopology configuration.*
- `ExternalConnection` → (aucun validator)
- `FLYNCTopology` → warn_deprecated
- `StateManagementConfig` → validate_unique_names
- `StateManagementGroup` → (aucun validator)

**`SC-CROSS-044-0`** — *The system configuration successfully passes validation, confirming that the TSN Stream's SingleRateTwoColorMarker bandwidth allocation is compatible with the periodic transmission rate defined by the StateManagementGroup's GroupTiming cycle_time_ms.*
- `GroupTiming` → check_consistency
- `SingleRateTwoColorMarker` → (aucun validator)
- `StateManagementGroup` → (aucun validator)
- `Stream` → (aucun validator)

**`SC-CROSS-045-0`** — *Configuration validation fails, reporting that the FirewallRule cannot apply scalar comparison operators to a Signal of non-scalar SignalDataType BYTEARRAY.*
- `FirewallRule` → validate_pattern
- `Signal` → _factor_nonzero, _validate_bit_length_for_data_type, _validate_limits, _validate_initial_value, _validate_value_encoding
- `SignalDataType` → (aucun validator)

**`SC-CROSS-046-0`** — *The configuration validator successfully verifies that the FirewallRule port and address parameters correctly encompass the UDP ports defined in SOMEIPConfig and SDConfig, ensuring SOME/IP and Service Discovery traffic is not blocked.*
- `Firewall` → check_duplicate_rules
- `FirewallRule` → validate_pattern
- `SDConfig` → (aucun validator)
- `SOMEIPConfig` → validate_all_e2e_identifiers_to_be_unique, validate_timing_exist

**`SC-CROSS-047-0`** — *Validation fails with a dangling reference error, indicating that the ECU identifier specified in the FirewallRule does not exist in the SystemTopology configuration.*
- `ExternalConnection` → (aucun validator)
- `Firewall` → check_duplicate_rules
- `FirewallRule` → validate_pattern

**`SC-CROSS-048-0`** — *The configuration validator successfully validates the model, confirming that the network interface is correctly bound to both the MACsecConfig (with IntegrityWithConfidentiality) and the PTPConfig (with PTPPort and PTPTimeTransmitterConfig) without validation errors.*
- `IntegrityWithConfidentiality` → (aucun validator)
- `MACsecConfig` → validate_mka_macsecmode_disabled, validate_life_time_greater_than_hello_time
- `PTPConfig` → (aucun validator)
- `PTPPort` → (aucun validator)
- `PTPTimeTransmitterConfig` → (aucun validator)

**`SC-CROSS-049-0`** — *Validation fails with an error stating that the payload size of the Signal exceeds the configured SOMEIPConfig UDP segment size threshold and SOME/IP TP is not enabled to handle segmentation.*
- `SOMEIPConfig` → validate_all_e2e_identifiers_to_be_unique, validate_timing_exist
- `Signal` → _factor_nonzero, _validate_bit_length_for_data_type, _validate_limits, _validate_initial_value, _validate_value_encoding
- `SignalDataType` → (aucun validator)
- `SignalInstance` → (aucun validator)

**`SC-CROSS-050-0`** — *The configuration validator successfully parses the model, confirming that the SignalInstance's logical path is fully supported by the physical ExternalConnection of type 'ecu_port_to_ecu_port' defined in the SystemTopology.*
- `ExternalConnection` → (aucun validator)
- `Signal` → _factor_nonzero, _validate_bit_length_for_data_type, _validate_limits, _validate_initial_value, _validate_value_encoding
- `SignalDataType` → (aucun validator)
- `SignalInstance` → (aucun validator)

**`SC-CROSS-051-0`** — *Configuration validation fails, reporting that the minimum frame size required by the SignalInstance (128 bytes) exceeds the maximum frame length of the matching TSN FrameFilter (64 bytes).*
- `Frame` → _validate_pdu_placements
- `FrameFilter` → validate_vlanids, validate_pcps, validate_port_mac, validate_port_assignment
- `Signal` → _factor_nonzero, _validate_bit_length_for_data_type, _validate_limits, _validate_initial_value, _validate_value_encoding
- `SignalDataType` → (aucun validator)
- `SignalInstance` → (aucun validator)
- `Stream` → (aucun validator)

**`SC-CROSS-052-0`** — *The configuration validation succeeds. The generator successfully maps the SOME/IP-SD timing profiles from SDTimings to the endpoints of the ECUs linked by the ExternalConnection of type 'ecu_port_to_ecu_port' in the SystemTopology.*
- `ExternalConnection` → (aucun validator)
- `FLYNCTopology` → warn_deprecated
- `SDConfig` → (aucun validator)
- `SDTimings` → (aucun validator)
- `SOMEIPConfig` → validate_all_e2e_identifiers_to_be_unique, validate_timing_exist

**`SC-CROSS-053-0`** — *Configuration validation fails with an error indicating that the TSN Stream's SingleRateTwoColorMarker bandwidth is insufficient for the configured SOME/IP-SD SDTimings rate.*
- `FrameFilter` → validate_vlanids, validate_pcps, validate_port_mac, validate_port_assignment
- `SDConfig` → (aucun validator)
- `SDTimings` → (aucun validator)
- `SingleRateTwoColorMarker` → (aucun validator)
- `Stream` → (aucun validator)

**`SC-CROSS-054-0`** — *The validation engine successfully parses both submodels, verifying that the PTPPort configurations for Port A and Port B correctly map to the endpoints of the ExternalConnection defined in SystemTopology, and confirms that a valid time synchronization path is established between the transmitter and receiver.*
- `ExternalConnection` → (aucun validator)
- `PTPConfig` → (aucun validator)
- `PTPPdelayConfig` → (aucun validator)
- `PTPPort` → (aucun validator)
- `PTPTimeReceiverConfig` → (aucun validator)
- `PTPTimeTransmitterConfig` → (aucun validator)
