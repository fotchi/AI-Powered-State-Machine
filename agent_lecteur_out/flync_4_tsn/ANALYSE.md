# `flync_4_tsn` — analyse indépendante

`KEY` = `TSN` | API publique = `['ATSInstance', 'ATSShaper', 'CBSShaper', 'SingleRateTwoColorMarker', 'SingleRateThreeColorMarker', 'DoubleRateThreeColorMarker', 'FrameFilter', 'Stream', 'TrafficClass', 'HTBFilter', 'ChildClass', 'HTBInstance', 'PTPTimeTransmitterConfig', 'PTPTimeReceiverConfig', 'PTPPdelayConfig', 'PTPPort', 'PTPConfig']`

### `ATSInstance` (hérite de: FLYNCBaseModel)
> Defines an ATS (Asynchronous Traffic Shaping) instance configuration for an ingress stream. ATS shaping is applied on egress when an
- `committed_information_rate: int` — obligatoire
- `committed_burst_size: int` — obligatoire
- `max_residence_time: int` — obligatoire

### `ATSShaper` (hérite de: FLYNCBaseModel)
> Specifies a shaper using the ATS (Asynchronous Traffic Shaping) mechanism.
- `type: Literal['ats']` — optionnel (défaut: Field(default='ats'))

### `CBSShaper` (hérite de: FLYNCBaseModel)
> Credit-Based Shaper (CBS) configuration model.
- `type: Literal['cbs']` — optionnel (défaut: Field(default='cbs'))
- `idleslope: int` — obligatoire

### `SingleRateTwoColorMarker` (hérite de: FLYNCBaseModel)
> Policer model implementing a single-rate, two-color marker.
- `type: Literal['single_rate_two_color']` — optionnel (défaut: Field(default='single_rate_two_color'))
- `cir: int` — obligatoire
- `cbs: int` — obligatoire
- `eir: Literal[0]` — obligatoire
- `ebs: int` — obligatoire
- `coupling: Literal[False]` — obligatoire

### `SingleRateThreeColorMarker` (hérite de: FLYNCBaseModel)
> Policer model implementing a single-rate, three-color marker.
- `type: Literal['single_rate_three_color']` — optionnel (défaut: Field(default='single_rate_three_color'))
- `cir: int` — obligatoire
- `cbs: int` — obligatoire
- `eir: Literal[0]` — obligatoire
- `ebs: int` — obligatoire
- `coupling: Literal[True]` — obligatoire

### `DoubleRateThreeColorMarker` (hérite de: FLYNCBaseModel)
> Policer model implementing a double-rate, three-color marker.
- `type: Literal['double_rate_three_color']` — optionnel (défaut: Field(default='double_rate_three_color'))
- `cir: int` — obligatoire
- `cbs: int` — obligatoire
- `eir: int` — obligatoire
- `ebs: int` — obligatoire
- `coupling: bool` — optionnel (défaut: Field(default=True))

### `FrameFilter` (hérite de: FLYNCBaseModel)
> Defines filtering rules for frames based on MAC/IP addresses, VLAN, and transport protocol ports.
- `ethertype: Optional[Annotated[Ethertype | List[Ethertype], PlainSerializer(serialize_ethertype), BeforeValidator(validate_ethertype_input)]]` — optionnel (défaut: Field(default=None))
- `src_mac: Optional[str | MACAddressEntry | List[str | MACAddressEntry]]` — optionnel (défaut: Field(default=None))
- `dst_mac: Optional[str | MACAddressEntry | List[str | MACAddressEntry]]` — optionnel (défaut: Field(default=None))
- `vlan_tagged: Optional[bool]` — optionnel (défaut: Field(default=None))
- `vlanid: Optional[int | ValueRange | List[int | ValueRange]]` — optionnel (défaut: Field(default=None))
- `pcp: Optional[int | List[int]]` — optionnel (défaut: Field(default=None))
- `src_ipv4: Optional[IPv4AddressEntry | IPv4Address | List[IPv4AddressEntry | IPv4Address]]` — optionnel (défaut: Field(default=None))
- `dst_ipv4: Optional[IPv4AddressEntry | IPv4Address | List[IPv4AddressEntry | IPv4Address]]` — optionnel (défaut: Field(default=None))
- `src_ipv6: Optional[IPv6AddressEntry | IPv6Address | List[IPv6AddressEntry | IPv6Address]]` — optionnel (défaut: Field(default=None))
- `dst_ipv6: Optional[IPv6AddressEntry | IPv6Address | List[IPv6AddressEntry | IPv6Address]]` — optionnel (défaut: Field(default=None))
- `protocol: Optional[Literal['tcp'] | Literal['udp']]` — optionnel (défaut: Field(default=None))
- `src_port: Optional[int | ValueRange | List[int | ValueRange]]` — optionnel (défaut: Field(default=None))
- `dst_port: Optional[int | ValueRange | List[int | ValueRange]]` — optionnel (défaut: Field(default=None))
- validator `validate_vlanids` (field_validator, cible: ['vlanid'])
- validator `validate_pcps` (field_validator, cible: ['pcp'])
- validator `validate_port_mac` (field_validator, cible: ['src_mac', 'dst_mac'])
- validator `validate_port_assignment` (field_validator, cible: ['src_port', 'dst_port'])

### `Stream` (hérite de: FLYNCBaseModel)
> Represents an IEEE 802.1Qci stream with optional traffic policing,
- `name: str` — obligatoire
- `stream_identification: List[FrameFilter]` — obligatoire
- `drop_at_ingress: Optional[bool]` — optionnel (défaut: Field(default=False))
- `max_sdu_size: Optional[int]` — optionnel (défaut: Field(default=1522, ge=0))
- `policer: Optional[SingleRateTwoColorMarker | SingleRateThreeColorMarker | DoubleRateThreeColorMarker]` — optionnel (défaut: Field(default=None, discriminator='type'))
- `ipv: Optional[int]` — optionnel (défaut: Field(default=None, ge=0, le=7))
- `ats: Optional[ATSInstance]` — optionnel (défaut: Field(default=None))

### `TrafficClass` (hérite de: FLYNCBaseModel)
> Defines a traffic class for prioritizing and shaping traffic on device egress queues.
- `name: str` — obligatoire
- `priority: int` — obligatoire
- `frame_priority_values: Annotated[Optional[List[int]], BeforeValidator(common_validators.none_to_empty_list)]` — optionnel (défaut: Field(default=[]))
- `internal_priority_values: Annotated[Optional[List[int]], BeforeValidator(common_validators.none_to_empty_list)]` — optionnel (défaut: Field(default=[]))
- `selection_mechanisms: Optional[CBSShaper | ATSShaper]` — optionnel (défaut: Field(default=None, discriminator='type'))
- validator `validate_priority_values` (field_validator, cible: ['frame_priority_values', 'internal_priority_values'])
- validator `validate_at_least_one_prio_list` (model_validator, cible: after)

### `HTBFilter` (hérite de: FrameFilter)
> Defines a filter for HTB (Hierarchical Token Bucket) child
- `filter_priority: int` — obligatoire

### `ChildClass` (hérite de: FLYNCBaseModel)
> Defines a child class for HTB (Hierarchical Token Bucket).
- `classid: int` — obligatoire
- `rate: int` — obligatoire
- `ceil: int` — obligatoire
- `priority: int` — obligatoire
- `filter: Annotated[Optional[List[HTBFilter]], BeforeValidator(common_validators.none_to_empty_list)]` — optionnel (défaut: Field(default=[]))
- `child_classes: Annotated[Optional[List['ChildClass']], BeforeValidator(common_validators.none_to_empty_list)]` — optionnel (défaut: Field(default=[]))

### `HTBInstance` (hérite de: FLYNCBaseModel)
> Defines an HTB (Hierarchical Token Bucket) instance for traffic shaping and class-based bandwidth management.
- `root_id: str` — obligatoire
- `default_class: Optional[int]` — optionnel (défaut: Field(default=None))
- `child_classes: list[ChildClass]` — obligatoire
- validator `validate_htb_config` (model_validator, cible: after)

### `PTPTimeTransmitterConfig` (hérite de: FLYNCBaseModel)
> Configuration for a PTP (Precision Time Protocol) time transmitter.
- `type: Literal['time_transmitter']` — optionnel (défaut: Field(default='time_transmitter'))
- `log_tx_period: int` — obligatoire
- `two_step: Optional[bool]` — optionnel (défaut: Field(default=True))
- `tlv: Annotated[Optional[List[str]], BeforeValidator(common_validators.none_to_empty_list)]` — optionnel (défaut: Field(default=[]))

### `PTPTimeReceiverConfig` (hérite de: FLYNCBaseModel)
> Configuration for a PTP (Precision Time Protocol) time receiver.
- `type: Literal['time_receiver']` — optionnel (défaut: Field(default='time_receiver'))
- `sync_timeout: int` — obligatoire
- `sync_followup_timeout: int` — obligatoire

### `PTPPdelayConfig` (hérite de: FLYNCBaseModel)
> Configuration for PTP peer delay (PDelay) messages.
- `log_tx_period: int` — obligatoire

### `PTPPort` (hérite de: FLYNCBaseModel)
> PTP port configuration for an ECU (Electronic Control Unit).
- `domain_id: int` — obligatoire
- `src_port_identity: int` — obligatoire
- `sync_config: PTPTimeTransmitterConfig | PTPTimeReceiverConfig` — obligatoire
- `pdelay_config: Optional[PTPPdelayConfig]` — optionnel (défaut: Field(default=None))

### `PTPConfig` (hérite de: FLYNCBaseModel)
> Top-level PTP configuration for an ECU.
- `cmlds_linkport_enabled: bool` — optionnel (défaut: Field(default=False))
- `ptp_ports: List[PTPPort]` — obligatoire
