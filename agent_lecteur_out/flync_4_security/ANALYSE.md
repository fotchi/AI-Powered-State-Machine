# `flync_4_security` — analyse indépendante

`KEY` = `SEC` | API publique = `['Firewall', 'FirewallRule', 'IntegrityWithConfidentiality', 'IntegrityWithoutConfidentiality', 'MACsecConfig']`

### `FirewallRule` (hérite de: FLYNCBaseModel)
> Defines a single firewall rule for matching and handling frames.
- `name: str` — obligatoire
- `action: Literal['reject', 'accept', 'drop']` — obligatoire
- `pattern: FrameFilter` — obligatoire
- validator `validate_pattern` (model_validator, cible: after)

### `Firewall` (hérite de: FLYNCBaseModel)
> Represents a set of firewall rules with a default action.
- `default_action: Optional[Literal['reject', 'accept', 'drop']]` — optionnel (défaut: Field(default='reject'))
- `input_rules: Annotated[Optional[List[FirewallRule]], BeforeValidator(common_validators.none_to_empty_list)]` — optionnel (défaut: Field(default=[]))
- `output_rules: Annotated[Optional[List[FirewallRule]], BeforeValidator(common_validators.none_to_empty_list)]` — optionnel (défaut: Field(default=[]))
- `forward_rules: Annotated[Optional[List[FirewallRule]], BeforeValidator(common_validators.none_to_empty_list)]` — optionnel (défaut: Field(default=[]))
- validator `check_duplicate_rules` (field_validator, cible: ['input_rules', 'output_rules', 'forward_rules'])

### `IntegrityWithoutConfidentiality` (hérite de: FLYNCBaseModel)
> Cipher configuration representing integrity protection without confidentiality.
- `type: Literal['integrity_without_confidentiality']` — optionnel (défaut: Field(default='integrity_without_confidentiality'))
- `offset_preference: Optional[Literal[0]]` — optionnel (défaut: Field(default=0))

### `IntegrityWithConfidentiality` (hérite de: FLYNCBaseModel)
> Cipher configuration representing both integrity protection and confidentiality.
- `type: Literal['integrity_with_confidentiality']` — optionnel (défaut: Field(default='integrity_with_confidentiality'))
- `offset_preference: Optional[Literal[0, 30, 50]]` — optionnel (défaut: Field(default=0))

### `MACsecConfig` (hérite de: FLYNCBaseModel)
> Configuration for MACsec (Media Access Control Security).
- `vlan_bypass: List[Annotated[int, Field(ge=1), AfterValidator(validate_vlan_id)]]` — obligatoire
- `mka_enabled: Optional[bool]` — optionnel (défaut: Field(default=True))
- `hello_time: int` — obligatoire
- `bounded_hello_time: int` — obligatoire
- `life_time: int` — obligatoire
- `sak_retire_time: int` — obligatoire
- `hello_time_rampup: List[int]` — obligatoire
- `sak_rekey_time: Optional[int]` — optionnel (défaut: Field(default=3, ge=0))
- `macsec_mode: Literal['disabled', 'integrity', 'integrity_confidentiality']` — obligatoire
- `kay_on: bool` — obligatoire
- `key_role: Literal['key_server_always', 'key_server_never']` — obligatoire
- `delay_protect: bool` — obligatoire
- `participant_activation: Literal['disabled', 'onoperup', 'always']` — obligatoire
- `sci_included: Optional[bool]` — optionnel (défaut: Field(default=False))
- `cipher_preference: List[DiscriminatedCipher]` — optionnel (défaut: Field(default_factory=lambda: MACsecConfig.default_entries_list()))
- validator `validate_mka_macsecmode_disabled` (model_validator, cible: after)
- validator `validate_life_time_greater_than_hello_time` (model_validator, cible: after)

### Dépendances croisées
- `flync.model.flync_4_tsn.qos` -> FrameFilter