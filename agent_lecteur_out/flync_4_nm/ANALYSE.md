# `flync_4_nm` — analyse indépendante

`KEY` = `None` | API publique = `['AnnouncementPhaseTiming', 'GroupTiming', 'SleepTiming', 'StateManagementConfig', 'StateManagementGroup', 'StateMembershipRef']`

### `EffectiveMember` (hérite de: NamedTuple)
> One resolved membership after merging all declaration sites.
- `group: str` — obligatoire
- `entity_kind: Literal['ecu', 'controller', 'app', 'bus']` — obligatoire
- `entity_path: str` — obligatoire
- `ecu_name: Optional[str]` — obligatoire
- `role: Literal['participant', 'observer']` — obligatoire
- `relevance_bit: Optional[str]` — obligatoire

### `AnnouncementPhaseTiming` (hérite de: FLYNCBaseModel)
> Timing of a group's announcement phase.
- `duration_ms: int` — obligatoire
- `burst_count: Optional[int]` — optionnel (défaut: Field(default=None, gt=0))
- `burst_cycle_time_ms: Optional[int]` — optionnel (défaut: Field(default=None, gt=0))
- validator `check_burst_pair` (model_validator, cible: after)

### `SleepTiming` (hérite de: FLYNCBaseModel)
> Timing of a group's go-to-sleep progression.
- `timeout_ms: int` — obligatoire
- `wait_before_sleep_ms: int` — obligatoire

### `GroupTiming` (hérite de: FLYNCBaseModel)
> A reusable, bus-abstract NM timing profile.
- `name: str` — obligatoire
- `description: Optional[str]` — optionnel (défaut: Field(default=None))
- `cycle_time_ms: int` — obligatoire
- `announcement: Optional[AnnouncementPhaseTiming]` — optionnel (défaut: Field(default=None))
- `sleep: SleepTiming` — obligatoire
- `extensions: Optional[Dict[str, str]]` — optionnel (défaut: Field(default=None))
- validator `check_consistency` (model_validator, cible: after)

### `StateManagementGroup` (hérite de: FLYNCBaseModel)
> A user-defined state management group.
- `name: str` — obligatoire
- `nm_pdu: str` — obligatoire
- `timing_profile: str` — obligatoire
- `description: Optional[str]` — optionnel (défaut: Field(default=None))
- `extensions: Optional[Dict[str, str]]` — optionnel (défaut: Field(default=None))

### `StateMembershipRef` (hérite de: FLYNCBaseModel)
> Entity-side assignment of an ECU, controller, or bus to a state
- `group: str` — obligatoire
- `role: Literal['participant', 'observer']` — optionnel (défaut: Field(default='participant'))
- `relevance_bits: Optional[List[str]]` — optionnel (défaut: Field(default=None))
- `extensions: Optional[Dict[str, str]]` — optionnel (défaut: Field(default=None))
- validator `observer_owns_no_bit` (model_validator, cible: after)
- validator `no_duplicate_bits` (model_validator, cible: after)

### `StateManagementConfig` (hérite de: FLYNCBaseModel)
> System-wide state management configuration.
- `groups: Annotated[List[StateManagementGroup], External(output_structure=OutputStrategy.SINGLE_FILE), BeforeValidator(common_validators.none_to_empty_list)]` — optionnel (défaut: Field(default=[]))
- `timing_profiles: Annotated[List[GroupTiming], External(output_structure=OutputStrategy.SINGLE_FILE), BeforeValidator(common_validators.none_to_empty_list)]` — optionnel (défaut: Field(default=[]))
- validator `validate_unique_names` (model_validator, cible: after)
