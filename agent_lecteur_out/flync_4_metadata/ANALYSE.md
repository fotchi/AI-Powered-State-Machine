# `flync_4_metadata` — analyse indépendante

`KEY` = `MET` | API publique = `['BaseMetadata', 'BaseVersion', 'ECUMetadata', 'EmbeddedMetadata', 'HardwareBaseMetadata', 'SoftwareBaseMetadata', 'SocketsPerVLANMetadata', 'SOMEIPServiceMetadata', 'SystemMetadata']`

### `BaseVersion` (hérite de: FLYNCBaseModel)
> Represents a version descriptor used within the model.
- `version_schema: Optional[Literal['semver', 'pep440']]` — optionnel (défaut: Field(default='semver'))
- `version: str` — obligatoire
- validator `validate_and_parse_version` (model_validator, cible: after)

### `SoftwareBaseMetadata` (hérite de: BaseVersion)
> Represents software-related metadata.

### `HardwareBaseMetadata` (hérite de: BaseVersion)
> Represents hardware-related metadata.
- `supplier: Optional[str]` — optionnel (défaut: Field(default=None))
- `product_id: Optional[str]` — optionnel (défaut: Field(default=None))

### `BaseMetadata` (hérite de: FLYNCBaseModel)
> Base class for model and system metadata definitions.
- `type: str` — obligatoire
- `author: str` — obligatoire
- `compatible_flync_version: BaseVersion` — obligatoire
- `extensions: Optional[Dict[str, str]]` — optionnel (défaut: Field(default=None))

### `SystemMetadata` (hérite de: BaseMetadata)
> Represents system-level metadata.
- `type: Literal['system']` — obligatoire
- `oem: Optional[str]` — optionnel (défaut: Field(default=None))
- `platform: Optional[str]` — optionnel (défaut: Field(default=None))
- `variant: Optional[str]` — optionnel (défaut: Field(default=None))
- `release: BaseVersion` — obligatoire

### `ECUMetadata` (hérite de: BaseMetadata)
> Represents metadata for an Electronic Control Unit (ECU).
- `type: Literal['ecu']` — obligatoire
- `hardware: Optional[HardwareBaseMetadata]` — optionnel (défaut: Field(default=None))
- `software: Optional[SoftwareBaseMetadata]` — optionnel (défaut: Field(default=None))

### `EmbeddedMetadata` (hérite de: BaseMetadata)
> Represents metadata for an embedded platform.
- `type: Literal['embedded']` — obligatoire
- `hardware: Optional[HardwareBaseMetadata]` — optionnel (défaut: Field(default=None))
- `app: Optional[SoftwareBaseMetadata]` — optionnel (défaut: Field(default=None))
- `bootloader: Optional[SoftwareBaseMetadata]` — optionnel (défaut: Field(default=None))
- `target_system: str` — obligatoire

### `SocketsPerVLANMetadata` (hérite de: BaseMetadata)
> Represents metadata for sockets-per-VLAN configuration.
- `type: Literal['sockets_per_vlan']` — obligatoire

### `SOMEIPServiceMetadata` (hérite de: BaseMetadata)
> Represents metadata for a SOME/IP service interface.
- `type: Literal['someip_service']` — obligatoire
