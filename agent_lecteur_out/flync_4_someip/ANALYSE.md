# `flync_4_someip` — analyse indépendante

`KEY` = `SOM` | API publique = `['AllTypes', 'Boolean', 'Int8', 'Int16', 'Int32', 'Int64', 'UInt8', 'UInt16', 'UInt32', 'UInt64', 'Float32', 'Float64', 'Ints', 'Floats', 'Enum', 'Struct', 'Union', 'ArrayType', 'DynamicLengthString', 'FixedLengthString', 'Bitfield', 'SOMEIPSDDeployment', 'SOMEIPServiceDeployment', 'SOMEIPServiceConsumer', 'SOMEIPServiceProvider', 'BaseUDPDeployment', 'UDPDeployment', 'TCPDeployment', 'MulticastEndpoint', 'MulticastSDEndpoint', 'Layer4Endpoint', 'SOMEIPEvent', 'SOMEIPEventgroup', 'SOMEIPEventTimings', 'SOMEIPField', 'SOMEIPFieldTimings', 'SOMEIPMethod', 'SOMEIPMethodTimings', 'SOMEIPFireAndForgetMethod', 'SOMEIPRequestResponseMethod', 'SOMEIPParameter', 'SOMEIPServiceInterface', 'SOMEIPConfig', 'SDConfig', 'SDTimings', 'SOMEIPTP', 'SOMEIPTimingProfile']`

### `Layer4Endpoint` (hérite de: FLYNCBaseModel)
> Layer4Endpoint Class method for Layer4 endpoint .
- `protocol: Literal['UDP', 'TCP']` — optionnel (défaut: 'UDP')
- `port: Annotated[int, Field(gt=0, le=65535)]` — obligatoire

### `BaseUDPDeployment` (hérite de: Layer4Endpoint)
> Base class for deploying a SOME/IP service onto a UDP-endpoint.
- `protocol: Literal['UDP']` — optionnel (défaut: 'UDP')

### `MulticastEndpoint` (hérite de: BaseUDPDeployment)
> MulticastEndpoint for UDP Deployments.
- `ip_address: Annotated[IPvAnyAddress, is_ip_multicast]` — obligatoire

### `MulticastSDEndpoint` (hérite de: MulticastEndpoint)
> MulticastSDEndpoint
- `ip_ttl: Annotated[int, Field(ge=0, le=255)]` — obligatoire

### `UDPDeployment` (hérite de: BaseUDPDeployment)
> Allows deploying a SOME/IP service onto a UDP-endpoint (including multicast).
- `multicast: Optional['MulticastEndpoint']` — optionnel (défaut: Field(description='multicast configuration for this endpoint', default=None))

### `TCPDeployment` (hérite de: Layer4Endpoint)
> Base class for deploying a SOME/IP service onto a TCP-endpoint
- `protocol: Literal['TCP']` — optionnel (défaut: 'TCP')

### `SOMEIPSDDeployment` (hérite de: FLYNCBaseModel)
> Defines the Service Discovery endpoint of SOME/IP.
- `deployment_type: Literal['someip_sd']` — optionnel (défaut: Field(default='someip_sd'))
- `multicast: Optional['MulticastSDEndpoint']` — optionnel (défaut: Field(description='multicast configuration for SD endpoint', default=None))

### `SOMEIPServiceDeployment` (hérite de: ABC, FLYNCBaseModel)
> SOMEIPServiceDeployment Create a service deployment that will be used for provided service.
- `deployment_type: DeploymentTypes` — obligatoire
- `service: Annotated[int, Reference(source='_service_ref')]` — obligatoire
- `major_version: Annotated[int, Field(gt=0, le=255, strict=True)]` — optionnel (défaut: Field(description='the major version of this service interface', default=0))
- `instance_id: Annotated[int, Field(gt=0, lt=65535)]` — obligatoire
- `someip_sd_timings_profile: str` — obligatoire

### `SOMEIPServiceConsumer` (hérite de: SOMEIPServiceDeployment)
> Defines the consumer of a SOME/IP service instance (like subscribing & calling methods).
- `deployment_type: Literal['someip_consumer']` — optionnel (défaut: Field(default='someip_consumer'))
- `major_version: Annotated[int, Field(gt=0, le=255, strict=True)]` — optionnel (défaut: Field(description='the major version of this service interface', default=0))
- `consumed_eventgroups: Optional[List[str]]` — optionnel (défaut: Field(default=None))

### `SOMEIPEventgroupMulticastConfig` (hérite de: FLYNCBaseModel)
> Multicast Configuration for a SOME/IP Eventgroup.
- `ip_address: Annotated[IPvAnyAddress, AfterValidator(common_validators.validate_ip_multicast)]` — obligatoire
- `port: Annotated[int, Field(gt=0, lt=65535)]` — obligatoire
- `threshold: Annotated[int, Field(gt=0)]` — obligatoire
- `eventgroups: List[str]` — obligatoire

### `SOMEIPServiceProvider` (hérite de: SOMEIPServiceDeployment)
> Defines the provider of a SOME/IP service instance (like offering & sending responses, events).
- `deployment_type: Literal['someip_provider']` — optionnel (défaut: Field(default='someip_provider'))
- `major_version: Annotated[int, Field(gt=0, lt=255, strict=True)]` — obligatoire
- `minor_version: Annotated[int, Field(ge=0, lt=4294967295, strict=True)]` — optionnel (défaut: Field(description='the major version of this service interface', default=0))
- `provided_eventgroups: Optional[List[str]]` — optionnel (défaut: Field(default=None))
- `multicast_config: Optional[List[SOMEIPEventgroupMulticastConfig]]` — optionnel (défaut: Field(default=None))

### `SOMEIPFieldTimings` (hérite de: FLYNCBaseModel)
> Timings for field.
- `profile_id: str` — obligatoire
- `type: Literal['field']` — optionnel (défaut: Field(default='field'))
- `getter_req_debounce: int` — optionnel (défaut: Field(description='Minimum time in milliseconds between 2 request messages for same getter method/service.', default=0))
- `getter_req_max_retention: int` — optionnel (défaut: Field(description='Maximum time in milliseconds indicating how long a getter request may be withheld.', default=0))
- `getter_res_max_retention: int` — optionnel (défaut: Field(description='Maximum time in milliseconds indicating how long a getter response may be withheld.', default=0))
- `setter_req_debounce: int` — optionnel (défaut: Field(description='Minimum time in milliseconds between 2 request messages for same setter method/service.', default=0))
- `setter_req_max_retention: int` — optionnel (défaut: Field(description='Maximum time in milliseconds indicating how long a setter request may be withheld.', default=0))
- `setter_res_max_retention: int` — optionnel (défaut: Field(description='Maximum time in milliseconds indicating how long a setter response may be withheld.', default=0))
- `notifier_debounce: int` — optionnel (défaut: Field(description='Minimum time in milliseconds between 2 notification messages for same service.', default=0))
- `notifier_max_retention: int` — optionnel (défaut: Field(description='Maximum time in milliseconds indicating how long a notification may be withheld.', default=0))

### `SOMEIPEventTimings` (hérite de: FLYNCBaseModel)
> Timings for event.
- `profile_id: str` — obligatoire
- `type: Literal['event']` — optionnel (défaut: Field(default='event'))
- `debounce: int` — optionnel (défaut: Field(description='Minimum time in milliseconds between 2 event messages for same service.', default=0))
- `max_retention: int` — optionnel (défaut: Field(description='Maximum time in milliseconds indicating how long an event may be withheld.', default=0))

### `SOMEIPMethodTimings` (hérite de: FLYNCBaseModel)
> Timings for method invocation.
- `profile_id: str` — obligatoire
- `type: Literal['method']` — optionnel (défaut: Field(default='method'))
- `req_debounce: int` — optionnel (défaut: Field(description='Minimum time in milliseconds between 2 request messages for same method/service.', default=0))
- `req_max_retention: int` — optionnel (défaut: Field(description='Maximum time in milliseconds indicating how long a request may be withheld.', default=0))
- `res_max_retention: int` — optionnel (défaut: Field(description='Maximum time in milliseconds indicating how long a response may be withheld.', default=0))

### `SOMEIPTimingProfile` (hérite de: FLYNCBaseModel)
> Timings for field.
- `profiles: Annotated[List[SOMEIPEvenTimingsProfilesUnion], Field(description='List of timing profiles for SOME/IP')]` — optionnel (défaut: Field(default_factory=list))
- `defaults: Annotated[List[SOMEIPEvenTimingsProfilesUnion], Field(description='List of default timing profiles for SOME/IP')]` — optionnel (défaut: Field(default_factory=list))

### `SOMEIPField` (hérite de: FLYNCBaseModel)
> Base datastructure to design a SOME/IP Field
- `name: str` — obligatoire
- `parameters: Annotated[Optional[List['SOMEIPParameter']], Field(description='name of the parameter')]` — optionnel (défaut: Field(default=[]))
- `description: Optional[str]` — optionnel (défaut: Field(default=''))
- `notifier_id: Optional[Annotated[int, Field(gt=0, le=65535, strict=True)]]` — optionnel (défaut: Field(description='identifies the field setter', default=None))
- `setter_id: Optional[Annotated[int, Field(gt=0, le=65535, strict=True)]]` — optionnel (défaut: Field(description='identifies the field setter', default=None))
- `getter_id: Optional[Annotated[int, Field(gt=0, le=65535, strict=True)]]` — optionnel (défaut: Field(description='identifies the field getter', default=None))
- `reliable: bool` — optionnel (défaut: Field(default=False))
- `notifier_e2e: Optional[E2EConfig]` — optionnel (défaut: Field(default=None))
- `someip_timing: Optional[str]` — optionnel (défaut: Field(description='SOME/IP timings for the field', default='field_default'))
- validator `validate_at_least_one_identifier_to_be_defined` (model_validator, cible: after)

### `SOMEIPParameter` (hérite de: FLYNCBaseModel)
> Definition of Parameters for SOME/IP.
- `name: str` — obligatoire
- `description: Optional[str]` — obligatoire
- `datatype: 'AllTypes'` — obligatoire

### `SOMEIPEvent` (hérite de: FLYNCBaseModel)
> Defines a SOME/IP event definition.
- `name: str` — obligatoire
- `description: Optional[str]` — optionnel (défaut: Field(default=''))
- `id: Annotated[int, Field(gt=0, le=65535, strict=True)]` — obligatoire
- `reliable: bool` — optionnel (défaut: Field(default=False))
- `e2e: Optional[E2EConfig]` — optionnel (défaut: Field(default=None))
- `parameters: Annotated[Optional[List['SOMEIPParameter']], Field(description='name of the parameter')]` — optionnel (défaut: Field(default=[]))
- `someip_timing: Optional[str]` — optionnel (défaut: Field(default='event_default'))

### `SOMEIPEventgroup` (hérite de: FLYNCBaseModel)
> Main datastructure to model a SOME/IP Eventgroup.
- `name: str` — obligatoire
- `description: Optional[str]` — optionnel (défaut: Field(default=''))
- `id: Annotated[int, Field(gt=0, le=65535, strict=True)]` — obligatoire
- `events: Annotated[List[SOMEIPEvent | SOMEIPField], conset(item_type=SOMEIPEvent | SOMEIPField, min_length=1)]` — obligatoire

### `SOMEIPTP` (hérite de: FLYNCBaseModel)
> SOME/IP Transport Protocol configuration.
- `enabled: bool` — optionnel (défaut: Field(default=False))
- `max_segment_length: int` — optionnel (défaut: Field(default=0, description='maximum segment length'))

### `SOMEIPMethod` (hérite de: FLYNCBaseModel)
> Datastructure to model SOME/IP methods.
- `name: str` — obligatoire
- `description: Optional[str]` — optionnel (défaut: Field(description='a short description on what this method does', default=''))
- `type: Literal['request_response', 'fire_and_forget']` — obligatoire
- `id: Annotated[int, Field(gt=0, le=65535, strict=True)]` — obligatoire
- `reliable: bool` — optionnel (défaut: Field(default=False))
- `someip_tp: Optional[SOMEIPTP]` — optionnel (défaut: Field(description='SOME/IP Transport Protocol configuration for this method', default=None))
- `input_parameters: Annotated[Optional[List['SOMEIPParameter']], BeforeValidator(common_validators.none_to_empty_list)]` — optionnel (défaut: Field(default=[]))
- `someip_timing: Optional[str]` — optionnel (défaut: Field(default='method_default'))

### `SOMEIPRequestResponseMethod` (hérite de: SOMEIPMethod)
> Allows to model SOME/IP methods which will return a response.
- `type: Literal['request_response']` — optionnel (défaut: 'request_response')
- `output_parameters: Annotated[Optional[List['SOMEIPParameter']], BeforeValidator(common_validators.none_to_empty_list)]` — optionnel (défaut: Field(default=[]))

### `SOMEIPFireAndForgetMethod` (hérite de: SOMEIPMethod)
> Allows to model SOME/IP methods which will not return a response.
- `type: Literal['fire_and_forget']` — optionnel (défaut: 'fire_and_forget')

### `SOMEIPServiceInterface` (hérite de: FLYNCBaseModel)
> Class to create a SOME/IP service interface definition.
- `name: str` — obligatoire
- `description: Optional[str]` — optionnel (défaut: Field(default=''))
- `id: Annotated[int, Field(gt=0, le=65535, strict=True)]` — obligatoire
- `major_version: Annotated[int, Field(ge=0, le=255, strict=True)]` — optionnel (défaut: Field(description='the major version of this service interface', default=0))
- `minor_version: Annotated[int, Field(ge=0, le=4294967295, strict=True)]` — optionnel (défaut: Field(description='the minor version of this service interface', default=0))
- `fields: Annotated[Optional[List[SOMEIPField]], BeforeValidator(common_validators.none_to_empty_list)]` — optionnel (défaut: Field(default=[], description='fields of the service'))
- `events: Annotated[Optional[List[SOMEIPEvent]], BeforeValidator(common_validators.none_to_empty_list)]` — optionnel (défaut: Field(default=[], description='events of the service'))
- `eventgroups: Annotated[Optional[List[SOMEIPEventgroup]], BeforeValidator(common_validators.none_to_empty_list)]` — optionnel (défaut: Field(default=[], description='eventgroups of the service'))
- `methods: Annotated[List[Union[SOMEIPFireAndForgetMethod, SOMEIPRequestResponseMethod]], BeforeValidator(common_validators.none_to_empty_list)]` — optionnel (défaut: Field(default=[], description='methods of the service'))
- `meta: SOMEIPServiceMetadata` — obligatoire
- validator `resolve_eventgroup_event_refs` (model_validator, cible: before)
- validator `validate_for_notifiers_without_eventgroup` (model_validator, cible: after)
- validator `validate_service_owns_elements_of_eventgroups` (model_validator, cible: after)
- validator `validate_all_identifiers_to_be_unique` (model_validator, cible: after)

### `SDTimings` (hérite de: FLYNCBaseModel)
> Configurations for SOME/IP-SD Timings.
- `profile_id: str` — obligatoire
- `initial_delay_min: int` — optionnel (défaut: Field(ge=0, description='Initial delay in milliseconds: This parameter keeps back service offers to pack more entries together.', default=10))
- `initial_delay_max: int` — optionnel (défaut: Field(ge=0, description='Initial delay in milliseconds: This parameter keeps back service offers to pack more entries together.', default=10))
- `repetitions_base_delay: int` — optionnel (défaut: Field(ge=0, description='Repetitions Base delay in milliseconds: This parameter helps in fast startup and to make startup more                 robust.Loss of the first offer results in this delay.', default=30))
- `repetitions_max: int` — optionnel (défaut: Field(ge=0, description='Number of repetitions while doubling delay', default=3))
- `request_response_delay_min: int` — optionnel (défaut: Field(ge=0, description='Request response delay in milliseconds: This parameter keeps back subscribes to pack more entries together.', default=10))
- `request_response_delay_max: int` — optionnel (défaut: Field(ge=0, description='Request response delay in milliseconds: This parameter keeps back subscribes to pack more entries together.', default=10))
- `offer_cyclic_delay: Optional[int]` — optionnel (défaut: Field(ge=0, description='Offer cyclic delay in milliseconds: This parameter keeps system alive with cyclic offer.', default=1000))
- `offer_ttl: Optional[int]` — optionnel (défaut: Field(ge=0, description='Time to live in milliseconds: This parameter determines how fast to age out state.', default=3000))
- `find_ttl: Optional[int]` — optionnel (défaut: Field(ge=0, description='Offer cyclic delay in milliseconds: This parameter keeps system alive with cyclic offer.', default=1000))
- `subscribe_ttl: Optional[int]` — optionnel (défaut: Field(ge=0, description='Time to live in milliseconds: This parameter determines how fast to age out state.', default=3000))

### `SDConfig` (hérite de: FLYNCBaseModel)
> allows to configure the SOME/IP Service-Discovery. Represent from the Chapter SD, the Endpoint and SD Endpoint.
- `ip_address: Annotated[IPvAnyAddress, AfterValidator(common_validators.validate_ip_multicast)]` — obligatoire
- `port: Annotated[int, Field(gt=0, lt=65535)]` — optionnel (défaut: Field(default=30490, description='port which the service discovery operates on'))
- `sd_timings: List[SDTimings]` — obligatoire

### `SOMEIPConfig` (hérite de: FLYNCBaseModel)
> Basic configuration of SOME/IP for a target system.
- `version: Literal['1.0']` — optionnel (défaut: Field(default='1.0', description='the version of this config'))
- `sd_config: Annotated[SDConfig, External(output_structure=OutputStrategy.SINGLE_FILE | OutputStrategy.OMMIT_ROOT)]` — obligatoire
- `services: Annotated[List[SOMEIPServiceInterface], External()]` — obligatoire
- `someip_timings: Annotated[SOMEIPTimingProfile, External(output_structure=OutputStrategy.SINGLE_FILE | OutputStrategy.OMMIT_ROOT)]` — obligatoire
- validator `validate_all_e2e_identifiers_to_be_unique` (model_validator, cible: after)
- validator `validate_timing_exist` (model_validator, cible: after)

### `PrimitiveDatatype` (hérite de: Datatype)
> Base class for primitive datatypes such as integers, floating-point values, or booleans.

### `ComplexDatatype` (hérite de: Datatype)
> Base class for complex datatypes such as structures, arrays, or unions.

### `Boolean` (hérite de: PrimitiveDatatype)
> Boolean primitive datatype.
- `name: str` — optionnel (défaut: Field(default='BOOLEAN'))
- `type: Literal['boolean']` — obligatoire
- `signed: Literal[False]` — obligatoire
- `endianness: Literal['BE']` — optionnel (défaut: 'BE')
- `bit_size: Annotated[int, Field(ge=8, le=8, default=8)]` — obligatoire

### `BaseInt` (hérite de: PrimitiveDatatype)
> Base class for all integer primitive datatypes.

### `BaseFloat` (hérite de: PrimitiveDatatype)
> Base class for all floating-point primitive datatypes.

### `UInt8` (hérite de: BaseInt)
> Unsigned 8-bit integer datatype.
- `name: str` — optionnel (défaut: Field(default='UINT8'))
- `type: Literal['uint8']` — obligatoire
- `signed: Literal[False]` — obligatoire
- `endianness: Literal['BE']` — obligatoire
- `bit_size: Annotated[int, Field(8)]` — obligatoire

### `UInt16` (hérite de: BaseInt)
> Unsigned 16-bit integer datatype.
- `name: str` — optionnel (défaut: Field(default='UINT16'))
- `type: Literal['uint16']` — obligatoire
- `signed: Literal[False]` — obligatoire
- `endianness: Literal['BE', 'LE']` — optionnel (défaut: 'BE')
- `bit_size: Annotated[int, Field(ge=16, le=16, default=16)]` — obligatoire

### `UInt32` (hérite de: BaseInt)
> Unsigned 32-bit integer datatype.
- `name: str` — optionnel (défaut: Field(default='UINT32'))
- `type: Literal['uint32']` — obligatoire
- `signed: Literal[False]` — obligatoire
- `endianness: Literal['BE', 'LE']` — optionnel (défaut: 'BE')
- `bit_size: Annotated[int, Field(ge=32, le=32, default=32)]` — obligatoire

### `UInt64` (hérite de: BaseInt)
> Unsigned 64-bit integer datatype.
- `name: str` — optionnel (défaut: Field(default='UINT64'))
- `type: Literal['uint64']` — obligatoire
- `signed: Literal[False]` — obligatoire
- `endianness: Literal['BE', 'LE']` — optionnel (défaut: 'BE')
- `bit_size: Annotated[int, Field(ge=64, le=64, default=64)]` — obligatoire

### `Int8` (hérite de: BaseInt)
> Signed 8-bit integer datatype.
- `name: str` — optionnel (défaut: Field(default='INT8'))
- `type: Literal['int8']` — obligatoire
- `signed: Literal[True]` — obligatoire
- `endianness: Literal['BE']` — optionnel (défaut: 'BE')
- `bit_size: Annotated[int, Field(ge=8, le=8, default=8)]` — obligatoire

### `Int16` (hérite de: BaseInt)
> Signed 16-bit integer datatype.
- `name: str` — optionnel (défaut: Field(default='INT16'))
- `type: Literal['int16']` — obligatoire
- `signed: Literal[True]` — obligatoire
- `endianness: Literal['BE', 'LE']` — optionnel (défaut: 'BE')
- `bit_size: Annotated[int, Field(ge=16, le=16, default=16)]` — obligatoire

### `Int32` (hérite de: BaseInt)
> Signed 32-bit integer datatype.
- `name: str` — optionnel (défaut: Field(default='INT32'))
- `type: Literal['int32']` — obligatoire
- `signed: Literal[True]` — obligatoire
- `endianness: Literal['BE', 'LE']` — optionnel (défaut: 'BE')
- `bit_size: Annotated[int, Field(ge=32, le=32, default=32)]` — obligatoire

### `Int64` (hérite de: BaseInt)
> Signed 64-bit integer datatype.
- `name: str` — optionnel (défaut: Field(default='INT64'))
- `type: Literal['int64']` — obligatoire
- `signed: Literal[True]` — obligatoire
- `endianness: Literal['BE', 'LE']` — optionnel (défaut: 'BE')
- `bit_size: Annotated[int, Field(ge=64, le=64, default=64)]` — obligatoire

### `Float32` (hérite de: PrimitiveDatatype)
> 32-bit floating-point datatype.
- `name: str` — optionnel (défaut: Field(default='FLOAT32'))
- `type: Literal['float32']` — obligatoire
- `signed: Literal[True]` — obligatoire
- `endianness: Literal['BE', 'LE']` — optionnel (défaut: 'BE')
- `bit_size: Annotated[int, Field(ge=32, le=32, default=32)]` — obligatoire

### `Float64` (hérite de: BaseFloat)
> 64-bit floating-point datatype.
- `name: str` — optionnel (défaut: Field(default='FLOAT64'))
- `type: Literal['float64']` — obligatoire
- `signed: Literal[True]` — obligatoire
- `endianness: Literal['BE', 'LE']` — optionnel (défaut: 'BE')
- `bit_size: Annotated[int, Field(ge=64, le=64, default=64)]` — obligatoire

### `BitfieldEntryValue` (hérite de: BaseModel)
> Represents a named value within a bitfield entry.
- `value: int` — obligatoire
- `name: str` — obligatoire
- `description: Optional[str]` — obligatoire

### `BitfieldEntry` (hérite de: BaseModel)
> Describes a single field within a bitfield.
- `name: str` — obligatoire
- `bitposition: int` — obligatoire
- `description: Optional[str]` — obligatoire
- `values: Optional[List[BitfieldEntryValue]]` — optionnel (défaut: Field(default_factory=list, description='Optional values defined for the entry'))

### `Bitfield` (hérite de: Datatype)
> Allows modeling of SOME/IP bitfields.
- `name: str` — optionnel (défaut: Field(default='Bitfield'))
- `type: Literal['bitfield']` — obligatoire
- `length: Literal[8, 16, 32, 64]` — optionnel (défaut: Field(default=8, description='defines the possible length of the bitfield'))
- `fields: Optional[List[BitfieldEntry]]` — optionnel (défaut: Field(default=None, description='List of bitfield entries'))
- validator `validate_length_against_fields_size` (model_validator, cible: after)
- validator `validate_bitfieldposition_of_entries` (model_validator, cible: after)

### `EnumEntry` (hérite de: BaseModel)
> Represents a single entry in an enumeration.
- `value: int` — obligatoire
- `name: str` — obligatoire
- `description: str` — obligatoire

### `Enum` (hérite de: Datatype)
> Allows modeling SOME/IP enumerations with value, name, and description.
- `name: str` — optionnel (défaut: Field(default='Enum'))
- `type: Literal['enum']` — obligatoire
- `base_type: TypingUnion['Ints']` — optionnel (défaut: Field(default_factory=lambda: Enum.default_base_type()))
- `entries: List[EnumEntry]` — optionnel (défaut: Field(default_factory=list))
- `BASE_TYPE_RANGES: ClassVar[dict[str, tuple[int, int]]]` — optionnel (défaut: {'UInt8': (0, 2 ** 8 - 1), 'UInt16': (0, 2 ** 16 - 1), 'UInt32': (0, 2 ** 32 - 1), 'UInt64': (0, 2 ** 64 - 1), 'Int8': (-2 ** 7, 2 ** 7 - 1), 'Int16': (-2 ** 15, 2 ** 15 - 1), 'Int32': (-2 ** 31, 2 ** 31 - 1), 'Int64': (-2 ** 63, 2 ** 63 - 1)})
- validator `validate_entries` (field_validator, cible: ['entries'])

### `BaseString` (hérite de: Datatype)
> Base class for all string datatypes.
- `name: str` — optionnel (défaut: Field(default='BaseString'))
- `type: str` — obligatoire
- `encoding: Literal['UTF-8', 'UTF-16BE', 'UTF-16LE']` — optionnel (défaut: Field(description='the encoding of the string\n\n.. needextract::\n\t:filter: id in ["feat_req_someip_234","feat_req_someip_235"]\n\n', default='UTF-8'))

### `FixedLengthString` (hérite de: BaseString)
> Fixed-length string datatype.
- `name: str` — optionnel (défaut: Field(default='FixedLengthString'))
- `type: Literal['fixed_length_string']` — obligatoire
- `length: Annotated[int, Field(ge=1)]` — obligatoire
- `length_of_length_field: Literal[0, 8, 16, 32]` — optionnel (défaut: Field(default=0, description='defines the length of the length-field in bits of the fixed length string where 0 indicates that there isno length field present.'))

### `DynamicLengthString` (hérite de: BaseString)
> Dynamic-length string datatype.
- `name: str` — optionnel (défaut: Field(default='DynamicLengthString'))
- `type: Literal['dynamic_length_string']` — optionnel (défaut: Field(default='dynamic_length_string', description='used internally by flync to efficiently determine the constructor to use from yaml'))
- `max_length: Optional[int]` — optionnel (défaut: Field(default=None, ge=0, description='Maximum string length in bytes.None means no upper limit.'))
- `min_length: Optional[int]` — optionnel (défaut: Field(default=None, ge=0, description='Minimum string length in bytes. None means 0.'))
- `length_of_length_field: Literal[8, 16, 32]` — optionnel (défaut: Field(description='the length of the length field of the string\n\n.. needextract::\n\t:filter: id in ["feat_req_someip_237", "feat_req_someip_582", "feat_req_someip_581"]\n\n', default=32))
- `bit_alignment: Literal[8, 16, 32, 64, 128, 256]` — optionnel (défaut: Field(default=8, description='defines the optional alignment padding that can be added after the dynamic length string to fix the alignment of the next parameter to 8, 16, 32, 64, 128, or 256 bits.'))

### `ArrayType` (hérite de: ComplexDatatype)
> Generic multidimensional array type.
- `name: str` — optionnel (défaut: Field(default='Array'))
- `type: Literal['array']` — obligatoire
- `dimensions: List['ArrayDimension']` — obligatoire
- `element_type: 'AllTypes'` — obligatoire

### `ArrayDimension` (hérite de: FLYNCBaseModel)
> Describes a single array dimension.
- `kind: Literal['fixed', 'dynamic']` — obligatoire
- `length: Optional[int]` — optionnel (défaut: Field(default=None, gt=0, description='Number of elements for fixed-length dimension'))
- `length_of_length_field: Optional[Literal[0, 8, 16, 32]]` — optionnel (défaut: Field(default=None, description='Length of length-field in bits for dynamic dimension'))
- `upper_limit: Optional[int]` — optionnel (défaut: Field(default=None, gt=0, description='Upper bound of elements'))
- `lower_limit: Optional[int]` — optionnel (défaut: Field(default=None, ge=0, description='Lower bound of elements'))
- `bit_alignment: Optional[Literal[8, 16, 32, 64, 128, 256]]` — optionnel (défaut: Field(default=None, description='Optional padding alignment after this dimension'))
- validator `validate` (field_validator, cible: ['length_of_length_field'])

### `Struct` (hérite de: ComplexDatatype)
> Structured datatype composed of multiple ordered members.
- `type: Literal['struct']` — obligatoire
- `members: List['AllTypes']` — obligatoire
- `bit_alignment: Literal[8, 16, 32, 64, 128, 256]` — optionnel (défaut: Field(default=8, description='defines the optional alignment padding that can be added after the variable length data element like struct to fix the alignment of the next parameter to 8, 16, 32, 64, 128, or 256 bits.'))
- `length_of_length_field: Literal[0, 8, 16, 32]` — optionnel (défaut: Field(default=0, description='defines the length of the length-field in bits for the struct'))

### `Typedef` (hérite de: ComplexDatatype)
> Alias datatype that references another datatype definition.
- `type: Literal['typedef']` — obligatoire
- `name: str` — obligatoire
- `datatyperef: 'AllTypes'` — obligatoire

### `UnionMember` (hérite de: Datatype)
> Represents a single member entry of a union datatype.
- `type: Annotated['AllTypes', Field(description="member datatype (discriminated by its 'type' field)")]` — obligatoire
- `index: Annotated[int, Field(description='index of the union member', strict=True, ge=0)]` — obligatoire
- `name: Annotated[str, Field(description='name of the union member')]` — obligatoire
- `mandatory: Annotated[Optional[bool], Field(description='whether the union member is mandatory', default=None)]` — optionnel (défaut: None)
- validator `_wrap_string_type` (field_validator, cible: ['type'])

### `Union` (hérite de: Datatype)
> Represents a union datatype.
- `name: str` — optionnel (défaut: Field(default='Union'))
- `type: Literal['union']` — obligatoire
- `members: List[UnionMember]` — obligatoire
- `bit_alignment: Literal[8, 16, 32, 64, 128, 256]` — optionnel (défaut: Field(default=8, description='defines the optional alignment padding that can be added after union to fix the alignment of the next parameter                 to 8, 16, 32, 64, 128 or 256 bits.'))
- `length_of_length_field: Literal[0, 8, 16, 32]` — optionnel (défaut: Field(default=32, description='defines the length of the length-field in bits for the union'))
- `length_of_type_field: Literal[0, 8, 16, 32]` — optionnel (défaut: Field(default=32, description='defines the length of the type-selector-field in bits for the union'))

### Dépendances croisées
- `flync.model.flync_4_metadata` -> SOMEIPServiceMetadata
- `flync.model.flync_4_safety.e2e` -> E2EConfig