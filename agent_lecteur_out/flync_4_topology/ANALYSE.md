# `flync_4_topology` — analyse indépendante

`KEY` = `TOP` | API publique = `['ExternalConnection', 'SystemTopology', 'FLYNCTopology']`

### `ExternalConnection` (hérite de: FLYNCBaseModel)
> Represents a connection between two ECU (Electronic Control Unit)
- `type: Literal['ecu_port_to_ecu_port']` — optionnel (défaut: Field(default='ecu_port_to_ecu_port'))
- `id: str` — obligatoire
- `ecu1_port_name: Annotated[str, Reference(source='_ecu1_port')]` — obligatoire
- `ecu2_port_name: Annotated[str, Reference(source='_ecu2_port')]` — obligatoire

### `SystemTopology` (hérite de: FLYNCBaseModel)
> Represents the system-wide topology consisting of external connections
- `connections: List[ExternalConnection]` — obligatoire

### `FLYNCTopology` (hérite de: FLYNCBaseModel)
> Represents the complete FLYNC system topology, including ECU connections
- `system_topology: Annotated[SystemTopology, External(output_structure=OutputStrategy.SINGLE_FILE | OutputStrategy.OMMIT_ROOT)]` — obligatoire

### Dépendances croisées
- `flync.model.flync_4_ecu.port` -> ECUPort