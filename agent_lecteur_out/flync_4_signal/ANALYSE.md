# `flync_4_signal` — analyse indépendante

`KEY` = `SIG` | API publique = `['SignalDataType', 'TextEntry', 'TextTable', 'BitfieldState', 'BitfieldGroup', 'BitfieldTextTable', 'BitmaskFlag', 'BitmaskFlags', 'ValueEncoding', 'InstancePlacement', 'Signal', 'SignalInstance', 'SignalGroup', 'SignalGroupInstance', 'PDU', 'StandardPDU', 'MuxGroup', 'MultiplexedPDU', 'ContainedPDURef', 'ContainerPDUHeader', 'PDUInstance', 'ContainerPDU', 'PDUSender', 'PDUReceiver', 'FrameEventTiming', 'FrameCyclicTiming', 'FrameTransmissionTiming', 'Frame', 'CANFrameBase', 'CANFrame', 'CANFDFrame', 'LINFrame', 'PDUForwarder', 'CANFrameForwarder', 'ForwarderEgress', 'CANFrameEgress', 'EthSocketEgress']`

### `CANFrameEgress` (hérite de: FLYNCBaseModel)
> Forwarder egress that re-emits the forwarded PDU on a CAN frame.
- `egress_type: Literal['can_frame']` — optionnel (défaut: Field(default='can_frame'))
- `bus_ref: str` — obligatoire
- `frame_ref: int` — obligatoire
- `extract_pdu_ref: Optional[str]` — optionnel (défaut: Field(default=None))

### `EthSocketEgress` (hérite de: FLYNCBaseModel)
> Forwarder egress that re-emits the forwarded PDU on an Ethernet socket (unicast/multicast follows the target's endpoint_address).
- `egress_type: Literal['eth_socket']` — optionnel (défaut: Field(default='eth_socket'))
- `socket_ref: str` — obligatoire
- `extract_pdu_ref: Optional[str]` — optionnel (défaut: Field(default=None))

### `ForwarderEgress` (hérite de: RootModel)
> Discriminated-union wrapper over a single forwarder egress (``CANFrameEgress`` or ``EthSocketEgress``).
- `root: CANFrameEgress | EthSocketEgress` — obligatoire

### `PDUForwarder` (hérite de: FLYNCBaseModel)
> Socket deployment that consumes a PDU on its parent socket and re-emits it on one or more egresses.
- `deployment_type: Literal['pdu_forwarder']` — optionnel (défaut: Field(default='pdu_forwarder'))
- `pdu_ref: str` — obligatoire
- `egresses: List[ForwarderEgress]` — obligatoire
- validator `validate_pdu_forwarder_egress_uniqueness` (model_validator, cible: after)

### `CANFrameForwarder` (hérite de: FLYNCBaseModel)
> CAN-interface forwarder that consumes an ingress frame and re-emits it on one or more egresses.
- `frame_ref: str` — obligatoire
- `egresses: List[ForwarderEgress]` — obligatoire
- validator `validate_can_frame_forwarder_egress_uniqueness` (model_validator, cible: after)

### `FrameEventTiming` (hérite de: FLYNCBaseModel)
> Event-based transmission timing.
- `final_repetitions: int` — optionnel (défaut: Field(default=0, ge=0))
- `repeating_time_range: float` — optionnel (défaut: Field(default=0.0, ge=0.0))

### `FrameCyclicTiming` (hérite de: FLYNCBaseModel)
> Cyclic transmission timing.
- `cycle: float` — obligatoire

### `FrameTransmissionTiming` (hérite de: FLYNCBaseModel)
> Frame transmission timing configuration.
- `debounce_time: Optional[float]` — optionnel (défaut: Field(default=None))
- `cyclic_timings: List[FrameCyclicTiming]` — optionnel (défaut: Field(default_factory=list))
- `event_timings: List[FrameEventTiming]` — optionnel (défaut: Field(default_factory=list))

### `Frame` (hérite de: FLYNCBaseModel)
> Protocol-agnostic frame base class.
- `name: str` — obligatoire
- `length: int` — obligatoire
- `frame_usage: Optional[Literal['application', 'bap', 'diag_request', 'diag_response', 'diag_state', 'network_management', 'other', 'service', 'tpl', 'xcp_pre_configured', 'xcp_runtime_configured']]` — optionnel (défaut: Field(default=None))
- `description: Optional[str]` — optionnel (défaut: Field(default=None))
- `packed_pdus: List[PDUInstance]` — optionnel (défaut: Field(default_factory=list))
- validator `_validate_pdu_placements` (model_validator, cible: after)

### `CANFrameBase` (hérite de: Frame)
> Shared fields for CAN 2.0 and CAN FD frames.
- `can_id: int` — obligatoire
- `id_format: Literal['standard_11bit', 'extended_29bit']` — obligatoire
- `timing: Optional[FrameTransmissionTiming]` — optionnel (défaut: Field(default=None))

### `CANFrame` (hérite de: CANFrameBase)
> Classical CAN frame (CAN 2.0A/B).
- `type: Literal['can']` — optionnel (défaut: Field(default='can'))
- `is_remote_frame: bool` — optionnel (défaut: Field(default=False))
- `length: int` — obligatoire
- validator `validate_can_frame_constraints` (model_validator, cible: after)

### `CANFDFrame` (hérite de: CANFrameBase)
> CAN FD frame.
- `type: Literal['can_fd']` — optionnel (défaut: Field(default='can_fd'))
- `bit_rate_switch: bool` — optionnel (défaut: Field(default=True))
- `error_state_indicator: bool` — optionnel (défaut: Field(default=False))
- `length: int` — obligatoire
- validator `validate_can_fd_frame_constraints` (model_validator, cible: after)

### `LINFrame` (hérite de: Frame)
> LIN unconditional frame.
- `type: Literal['lin']` — optionnel (défaut: Field(default='lin'))
- `lin_id: Annotated[int, Field(ge=0, le=63)]` — obligatoire
- `checksum_type: Literal['classic', 'enhanced']` — optionnel (défaut: Field(default='enhanced'))
- `length: int` — obligatoire
- `timing: Optional[FrameTransmissionTiming]` — optionnel (défaut: Field(default=None))

### `PDU` (hérite de: FLYNCBaseModel)
> Protocol Data Unit base class.
- `name: str` — obligatoire
- `length: int` — obligatoire
- `pdu_usage: Optional[Literal['application', 'bap', 'diag_request', 'diag_response', 'diag_state', 'network_management', 'other', 'service', 'tpl', 'xcp_pre_configured', 'xcp_runtime_configured']]` — optionnel (défaut: Field(default=None))
- `description: Optional[str]` — optionnel (défaut: Field(default=None))

### `StandardPDU` (hérite de: PDU)
> Non-multiplexed PDU containing a flat list of signal instances.
- `type: Literal['standard']` — optionnel (défaut: Field(default='standard'))
- `signals: List[SignalInstance]` — optionnel (défaut: Field(default_factory=list))
- `signal_groups: List[SignalGroupInstance]` — optionnel (défaut: Field(default_factory=list))
- validator `validate_signals_fit_in_pdu` (model_validator, cible: after)

### `MuxGroup` (hérite de: FLYNCBaseModel)
> Set of signals active for a specific multiplexer selector value.
- `selector_value: int` — obligatoire
- `pdu: StandardPDU` — obligatoire

### `MultiplexedPDU` (hérite de: PDU)
> PDU with a selector signal that determines which signal group is active.
- `type: Literal['multiplexed']` — optionnel (défaut: Field(default='multiplexed'))
- `selector_signal: SignalInstance` — obligatoire
- `static_group: Optional[StandardPDU]` — optionnel (défaut: Field(default=None))
- `mux_groups: List[MuxGroup]` — optionnel (défaut: Field(default_factory=list, min_length=1))
- validator `validate_unique_selector_values` (model_validator, cible: after)
- validator `validate_selector_value_ranges` (model_validator, cible: after)
- validator `validate_selector_overlap` (model_validator, cible: after)

### `ContainedPDURef` (hérite de: FLYNCBaseModel)
> Reference to a PDU packed inside a :class:`ContainerPDU`.
- `pdu_id: int` — obligatoire
- `pdu_ref: str` — obligatoire
- `offset: Optional[int]` — optionnel (défaut: Field(default=0, ge=0))

### `PDUInstance` (hérite de: FLYNCBaseModel)
> Placement of a PDU at a specific bit offset within a CAN or LIN frame.
- `pdu_ref: str` — obligatoire
- `bit_position: Optional[int]` — optionnel (défaut: Field(default=None, ge=0))
- `update_bit_position: Optional[int]` — optionnel (défaut: Field(default=None, ge=0))

### `ContainerPDUHeader` (hérite de: FLYNCBaseModel)
> Per-slot header configuration for a :class:`ContainerPDU`.
- `id_length_bits: int` — obligatoire
- `length_field_bits: int` — obligatoire
- validator `must_be_byte_aligned` (field_validator, cible: ['id_length_bits', 'length_field_bits'])

### `ContainerPDU` (hérite de: PDU)
> Ethernet Container PDU that packs multiple PDUs into one frame payload.
- `type: Literal['container']` — optionnel (défaut: Field(default='container'))
- `pdu_id: int` — obligatoire
- `header: ContainerPDUHeader` — obligatoire
- `contained_pdus: List[ContainedPDURef]` — optionnel (défaut: Field(default_factory=list))
- validator `validate_minimum_container_size` (model_validator, cible: after)
- validator `validate_one_pdu_if_header_length_is_one` (model_validator, cible: after)

### `PDUSender` (hérite de: FLYNCBaseModel)
> Deployment that publishes a PDU onto a socket.
- `deployment_type: Literal['pdu_sender']` — optionnel (défaut: Field(default='pdu_sender'))
- `pdu_ref: str` — obligatoire

### `PDUReceiver` (hérite de: FLYNCBaseModel)
> Deployment that subscribes to a PDU on a socket.
- `deployment_type: Literal['pdu_receiver']` — optionnel (défaut: Field(default='pdu_receiver'))
- `pdu_ref: str` — obligatoire

### `SignalDataType` (hérite de: str, Enum)
> Supported signal base data types for CAN, LIN, FlexRay, and Ethernet.

### `InstancePlacement` (hérite de: FLYNCBaseModel)
> Shared placement metadata for signal and signal-group instances within
- `bit_position: Optional[int]` — optionnel (défaut: Field(default=None, ge=0))
- `update_indication_bit_position: Optional[int]` — optionnel (défaut: Field(default=None))
- `endianness: Literal['BE', 'LE']` — optionnel (défaut: Field(default='LE'))

### `Signal` (hérite de: FLYNCBaseModel)
> Logical or physical data element transmitted within a communication
- `name: str` — obligatoire
- `description: Optional[str]` — optionnel (défaut: Field(default=None))
- `bit_length: int` — obligatoire
- `data_type: SignalDataType` — obligatoire
- `factor: float` — optionnel (défaut: Field(default=1.0))
- `offset: float` — optionnel (défaut: Field(default=0.0))
- `lower_limit: Optional[float]` — optionnel (défaut: Field(default=None))
- `upper_limit: Optional[float]` — optionnel (défaut: Field(default=None))
- `unit: Optional[str]` — optionnel (défaut: Field(default=None))
- `initial_value: Optional[float | int | bytes | str]` — optionnel (défaut: Field(default=None))
- `value_encoding: Optional[ValueEncoding]` — optionnel (défaut: Field(default=None))
- validator `_factor_nonzero` (field_validator, cible: ['factor'])
- validator `_validate_bit_length_for_data_type` (model_validator, cible: after)
- validator `_validate_limits` (model_validator, cible: after)
- validator `_validate_initial_value` (model_validator, cible: after)
- validator `_validate_value_encoding` (model_validator, cible: after)

### `SignalInstance` (hérite de: InstancePlacement)
> Placement of a :class:`Signal` at a specific bit offset within a PDU.
- `signal: Signal` — obligatoire

### `SignalGroup` (hérite de: FLYNCBaseModel)
> A reusable group of signal instances transmitted together within a PDU.
- `name: str` — obligatoire
- `description: Optional[str]` — optionnel (défaut: Field(default=None))
- `signals: List[SignalInstance]` — obligatoire
- validator `_validate_signals_no_overlap` (model_validator, cible: after)

### `SignalGroupInstance` (hérite de: InstancePlacement)
> Placement of a :class:`SignalGroup` at a specific bit offset within a PDU.
- `signal_group: SignalGroup` — obligatoire

### `TextEntry` (hérite de: FLYNCBaseModel)
> Mapping of an inclusive raw value range to a label.
- `value: Optional[int]` — optionnel (défaut: Field(default=None))
- `from_value: Optional[int]` — optionnel (défaut: Field(default_factory=lambda data: data.get('value', 0)))
- `to_value: Optional[int]` — optionnel (défaut: Field(default_factory=lambda data: data.get('value', 0)))
- `label: str` — obligatoire
- validator `_validate_value_input_format` (model_validator, cible: before)
- validator `_validate_bounds` (model_validator, cible: after)

### `TextTable` (hérite de: FLYNCBaseModel)
> Decodes the signal as a set of TextEntries.
- `type: Literal['text_table']` — optionnel (défaut: 'text_table')
- `entries: List[TextEntry]` — obligatoire
- validator `_validate_no_overlap` (model_validator, cible: after)

### `BitfieldState` (hérite de: FLYNCBaseModel)
> Mapping of an inclusive bitfield range to a label of states.
- `label: str` — obligatoire
- `value: Optional[int]` — optionnel (défaut: Field(default=None))
- `from_value: Optional[int]` — optionnel (défaut: Field(ge=0, default_factory=lambda data: data.get('value', 0)))
- `to_value: Optional[int]` — optionnel (défaut: Field(ge=0, default_factory=lambda data: data.get('value', 0)))
- validator `validate_value_input_format` (model_validator, cible: before)
- validator `_validate_bounds` (model_validator, cible: after)

### `BitfieldGroup` (hérite de: FLYNCBaseModel)
> One named region of bits within a signal, with its own enum of states.
- `name: str` — obligatoire
- `mask: int` — obligatoire
- `states: List[BitfieldState]` — obligatoire
- validator `_validate_states` (model_validator, cible: after)

### `BitfieldTextTable` (hérite de: FLYNCBaseModel)
> Decodes a signal as a set of independent :class:`BitfieldGroup` regions.
- `type: Literal['bitfield_text_table']` — optionnel (défaut: 'bitfield_text_table')
- `groups: List[BitfieldGroup]` — obligatoire
- validator `_validate_groups` (model_validator, cible: after)

### `BitmaskFlag` (hérite de: FLYNCBaseModel)
> One named on/off flag inside a :class:`BitmaskFlags` encoding.
- `mask: int` — obligatoire
- `label: str` — obligatoire

### `BitmaskFlags` (hérite de: FLYNCBaseModel)
> Decodes a signal as a set of independent on/off flags.
- `type: Literal['bitmask_flags']` — optionnel (défaut: 'bitmask_flags')
- `flags: List[BitmaskFlag]` — obligatoire
- validator `_validate_flags` (model_validator, cible: after)
