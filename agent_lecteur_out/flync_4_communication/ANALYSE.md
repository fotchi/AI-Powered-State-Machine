# `flync_4_communication` — analyse indépendante

`KEY` = `None` | API publique = `['FLYNCChannelConfig', 'FLYNCCommunicationConfig']`

### `FLYNCChannelConfig` (hérite de: FLYNCBaseModel)
> Channel-level configuration grouping all buses and shared PDU definitions.
- `pdus: Annotated[Optional[List[Annotated[Union[StandardPDU, MultiplexedPDU], Field(discriminator='type')]]], External(output_structure=OutputStrategy.FOLDER, naming_strategy=NamingStrategy.FIXED_PATH, path='pdus')]` — optionnel (défaut: Field(default_factory=list, description='Shared PDU definitions, one file per PDU.'))
- `can_buses: Annotated[Optional[List[CANBus]], External(output_structure=OutputStrategy.FOLDER, naming_strategy=NamingStrategy.FIXED_PATH, path='can')]` — optionnel (défaut: Field(default=None, description='CAN / CAN FD bus definitions, one file per bus.'))
- `lin_buses: Annotated[Optional[List[LINBus]], External(output_structure=OutputStrategy.FOLDER, naming_strategy=NamingStrategy.FIXED_PATH, path='lin')]` — optionnel (défaut: Field(default=None, description='LIN bus definitions, one file per bus.'))
- `ethernet_pdu_containers: Annotated[Optional[List[ContainerPDU]], External(output_structure=OutputStrategy.FOLDER, naming_strategy=NamingStrategy.FIXED_PATH, path='ethernet_pdu_containers')]` — optionnel (défaut: Field(default=None, description='Ethernet Container PDU definitions.'))
- validator `validate_pdus_name_unique` (model_validator, cible: after)
- validator `validate_canbus_name_unique` (model_validator, cible: after)
- validator `validate_linbus_name_unique` (model_validator, cible: after)
- validator `validate_pdu_refs` (model_validator, cible: after)

### `FLYNCCommunicationConfig` (hérite de: FLYNCBaseModel)
> The top-level configuration object that aggregates all reusable
- `tcp_profiles: Annotated[Optional[List[TCPOption]], External(output_structure=OutputStrategy.SINGLE_FILE), BeforeValidator(common_validators.validate_or_remove('TCP profiles', List[TCPOption])), BeforeValidator(common_validators.none_to_empty_list)]` — optionnel (défaut: Field(default=[]))
- `someip_config: Annotated[Optional[SOMEIPConfig], External(output_structure=OutputStrategy.FOLDER, naming_strategy=NamingStrategy.FIXED_PATH, path='someip'), BeforeValidator(common_validators.validate_or_remove('SOME/IP config', SOMEIPConfig))]` — optionnel (défaut: Field(default=None, description='contains the SOME/IP config for the entire system.'))
- `channels: Annotated[Optional[FLYNCChannelConfig], External(output_structure=OutputStrategy.FOLDER, naming_strategy=NamingStrategy.FIXED_PATH, path='channels')]` — optionnel (défaut: Field(default=None, description='CAN buses, LIN buses and Ethernet Container PDUs, loaded from communication/channels/.'))
- `state_management: Annotated[Optional[StateManagementConfig], External(output_structure=OutputStrategy.FOLDER, naming_strategy=NamingStrategy.FIXED_PATH, path='state_management')]` — optionnel (défaut: Field(default_factory=StateManagementConfig, description='System-wide state management groups, loaded from communication/state_management/.'))

### Dépendances croisées
- `flync.model.flync_4_bus.can_bus` -> CANBus
- `flync.model.flync_4_bus.lin_bus` -> LINBus
- `flync.model.flync_4_signal.frame` -> Frame
- `flync.model.flync_4_signal.pdu` -> PDU, ContainerPDU, MultiplexedPDU, StandardPDU
- `flync.model.flync_4_ecu` -> TCPOption
- `flync.model.flync_4_nm` -> StateManagementConfig
- `flync.model.flync_4_someip` -> SOMEIPConfig