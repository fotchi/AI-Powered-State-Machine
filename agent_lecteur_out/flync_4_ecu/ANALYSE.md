# `flync_4_ecu` — analyse indépendante

`KEY` = `ECU` | API publique = `['ComputeNodes', 'Controller', 'ControllerInterface', 'EthernetInterface', 'EthernetInterfaceConfig', 'FrameMask', 'VirtualSwitch', 'VirtualSwitchPort', 'VirtualControllerInterface', 'IPv4AddressEndpoint', 'IPv6AddressEndpoint', 'Socket', 'TCPOption', 'UDPOption', 'SocketTCP', 'SocketUDP', 'SocketContainer', 'ECU', 'InternalTopology', 'MII', 'RMII', 'RGMII', 'SGMII', 'XFI', 'BASET', 'BASET1', 'BASET1S', 'ECUPort', 'RouteEntry', 'Switch', 'SwitchPort', 'VLANEntry', 'MulticastGroup', 'TCAMRule', 'TrafficClass', 'MulticastGroupMembership', 'AVTPMulticastEndpoint', 'MACMulticastEndpoint', 'MACMulticastEndpoints']`

### `CANFrameRef` (hérite de: FLYNCBaseModel)
> Reference to a CAN frame by bus and CAN ID.
- `bus_ref: str` — obligatoire
- `frame_ref: int` — obligatoire

### `CANInterface` (hérite de: ControllerInterface)
> CAN interface of a controller, declaring which frames the controller sends, receives, and forwards on a CAN bus.
- `name: Annotated[str, Implied(strategy=ImpliedStrategy.FILE_NAME)]` — obligatoire
- `bus_ref: str` — obligatoire
- `sender_frames: List[CANFrameRef]` — optionnel (défaut: Field(default_factory=list))
- `receiver_frames: List[CANFrameRef]` — optionnel (défaut: Field(default_factory=list))
- `forwarder_frames: List[CANFrameForwarder]` — optionnel (défaut: Field(default_factory=list))
- validator `validate_forwarder_frame_uniqueness` (model_validator, cible: after)

### `VirtualControllerInterface` (hérite de: FLYNCBaseModel)
> A VLAN-tagged virtual interface stacked on top of a physical controller interface or a compute node.
- `name: str` — obligatoire
- `vlanid: Annotated[Optional[int], AfterValidator(common_validators.validate_vlan_id)]` — optionnel (défaut: Field(default=None))
- `addresses: List[IPv6AddressEndpoint | IPv4AddressEndpoint]` — obligatoire
- `multicast: Annotated[Optional[List[IPvAnyAddress | FLYNCMacAddress]], AfterValidator(common_validators.validate_multicast_list), BeforeValidator(common_validators.none_to_empty_list)]` — optionnel (défaut: Field(default=[]))

### `ComputeNodes` (hérite de: FLYNCBaseModel)
> **WARNING: ComputeNode is currently experimental! Subject to change, please use with care.**
- `name: str` — obligatoire
- `mac_address: Optional[FLYNCMacAddress]` — optionnel (défaut: Field(default=None))
- `virtual_interfaces: Annotated[List[VirtualControllerInterface], BeforeValidator(common_validators.validate_list_items_and_remove('virtual interface', VirtualControllerInterface, severity='minor'))]` — obligatoire
- `ptp_config: _PTPConfigField` — optionnel (défaut: Field(default=None))
- `macsec_config: _MACsecConfigField` — optionnel (défaut: Field(default=None))
- `firewall: _FirewallField` — optionnel (défaut: Field(default=None))
- `htb: _HTBField` — optionnel (défaut: Field(default=None))
- `ingress_streams: _IngressStreamsField` — optionnel (défaut: Field(default=[]))
- `traffic_classes: _TrafficClassesField` — optionnel (défaut: Field(default_factory=list))
- validator `validate_ingress_streams` (field_validator, cible: ['ingress_streams'])
- validator `experimental_warning` (model_validator, cible: before)
- validator `validate_vlans` (model_validator, cible: after)

### `VirtualSwitchPort` (hérite de: FLYNCBaseModel)
> A port on the :class:`VirtualSwitch`, referencing a connected node by name.
- `name: str` — obligatoire
- `node_connected: str` — obligatoire

### `VirtualSwitch` (hérite de: FLYNCBaseModel)
> **WARNING: VirtualSwitch is currently experimental! Subject to change, please use with care.**
- `name: str` — obligatoire
- `ports: List[VirtualSwitchPort]` — obligatoire
- `vlans: List[VLANEntry]` — obligatoire
- validator `experimental_warning` (model_validator, cible: before)

### `EthernetInterfaceConfig` (hérite de: FLYNCBaseModel)
> Configuration for a physical Ethernet interface on a controller.
- `mac_address: Optional[FLYNCMacAddress]` — optionnel (défaut: Field(default=None))
- `mii_config: Optional[MII | RMII | SGMII | RGMII | XFI]` — optionnel (défaut: Field(default=None, discriminator='type'))
- `compute_nodes: Optional[List[ComputeNodes]]` — optionnel (défaut: Field(default_factory=list))
- `virtual_interfaces: Annotated[Optional[List[VirtualControllerInterface]], BeforeValidator(common_validators.validate_list_items_and_remove('virtual interface', VirtualControllerInterface, severity='minor'))]` — optionnel (défaut: Field(default_factory=list))
- `ptp_config: _PTPConfigField` — optionnel (défaut: Field(default=None))
- `macsec_config: _MACsecConfigField` — optionnel (défaut: Field(default=None))
- `firewall: _FirewallField` — optionnel (défaut: Field(default=None))
- `htb: _HTBField` — optionnel (défaut: Field(default=None))
- `ingress_streams: _IngressStreamsField` — optionnel (défaut: Field(default=[]))
- `traffic_classes: _TrafficClassesField` — optionnel (défaut: Field(default_factory=list))
- `routing_table: Annotated[Optional[List[RouteEntry]], BeforeValidator(common_validators.none_to_empty_list)]` — optionnel (défaut: Field(default=[]))
- validator `validate_ingress_streams` (field_validator, cible: ['ingress_streams'])
- validator `require_valid_virtual_interface` (model_validator, cible: after)
- validator `validate_vlans` (model_validator, cible: after)
- validator `validate_offloaded_configs_not_duplicated` (model_validator, cible: after)
- validator `validate_routing_table_egress_interface` (model_validator, cible: after)
- validator `validate_routing_table_default_gateway` (model_validator, cible: after)

### `EthernetInterface` (hérite de: ControllerInterface)
> An Ethernet Interface of a Controller.
- `name: Annotated[str, Implied(strategy=ImpliedStrategy.FOLDER_NAME)]` — obligatoire
- `interface_config: Annotated[EthernetInterfaceConfig, External(output_structure=OutputStrategy.SINGLE_FILE | OutputStrategy.OMMIT_ROOT, naming_strategy=NamingStrategy.FIELD_NAME)]` — obligatoire
- `sockets: Annotated[Optional[List[SocketContainer]], External(output_structure=OutputStrategy.FOLDER, naming_strategy=NamingStrategy.FIELD_NAME)]` — optionnel (défaut: Field(default_factory=list))

### `Controller` (hérite de: FLYNCBaseModel)
> Represents a controller device that contains multiple interfaces.
- `name: Annotated[str, Implied(strategy=ImpliedStrategy.FOLDER_NAME)]` — obligatoire
- `controller_metadata: Annotated[EmbeddedMetadata, External(output_structure=OutputStrategy.SINGLE_FILE, naming_strategy=NamingStrategy.FIELD_NAME)]` — obligatoire
- `ethernet_interfaces: Annotated[Optional[List[EthernetInterface]], External(output_structure=OutputStrategy.FOLDER, naming_strategy=NamingStrategy.FIELD_NAME)]` — optionnel (défaut: Field(default_factory=list))
- `can_interfaces: Annotated[Optional[List[CANInterface]], External(output_structure=OutputStrategy.FOLDER, naming_strategy=NamingStrategy.FIELD_NAME)]` — optionnel (défaut: Field(default_factory=list))
- `lin_interfaces: Annotated[Optional[List[AnyLINInterface]], External(output_structure=OutputStrategy.FOLDER, naming_strategy=NamingStrategy.FIELD_NAME)]` — optionnel (défaut: Field(default_factory=list))
- `virtual_switch: Annotated[Optional[VirtualSwitch], External(output_structure=OutputStrategy.SINGLE_FILE | OutputStrategy.OMMIT_ROOT, naming_strategy=NamingStrategy.FIELD_NAME)]` — optionnel (défaut: Field(default=None))
- `app_bindings: Annotated[Optional[AppBindings], External(output_structure=OutputStrategy.SINGLE_FILE | OutputStrategy.OMMIT_ROOT)]` — optionnel (défaut: Field(default=None, description='Applications a controller should bind to.'))
- `state_memberships: Annotated[Optional[List[StateMembershipRef]], External(output_structure=OutputStrategy.SINGLE_FILE), BeforeValidator(common_validators.validate_or_remove('state memberships', List[StateMembershipRef])), BeforeValidator(common_validators.none_to_empty_list)]` — optionnel (défaut: Field(default=[], description='Assignments of this controller to state management groups.'))
- validator `reject_legacy_controller_layout` (model_validator, cible: before)
- validator `require_at_least_one_interface` (model_validator, cible: after)
- validator `validate_unique_interface_names` (model_validator, cible: after)
- validator `check_ports_virtual_switch_are_interfaces_or_compute_nodes` (model_validator, cible: after)

### `ControllerInterface` (hérite de: FLYNCBaseModel)
> Base class for all controller interfaces (Ethernet, CAN, LIN).
- `name: str` — obligatoire

### `ECU` (hérite de: FLYNCBaseModel)
> Represents an Electronic Control Unit (ECU) in the network.
- `name: Annotated[str, Implied(strategy=ImpliedStrategy.FOLDER_NAME)]` — obligatoire
- `ports: Annotated[List['ECUPort'], External(output_structure=OutputStrategy.SINGLE_FILE, naming_strategy=NamingStrategy.FIELD_NAME)]` — optionnel (défaut: Field(min_length=1, default_factory=list))
- `controllers: Annotated[List['Controller'], External(output_structure=OutputStrategy.FOLDER, naming_strategy=NamingStrategy.FIELD_NAME)]` — obligatoire
- `switches: Annotated[Optional[List['Switch']], External(output_structure=OutputStrategy.FOLDER, naming_strategy=NamingStrategy.FIELD_NAME)]` — optionnel (défaut: Field(default_factory=list))
- `topology: Annotated['InternalTopology', External(output_structure=OutputStrategy.SINGLE_FILE | OutputStrategy.OMMIT_ROOT, naming_strategy=NamingStrategy.FIELD_NAME), BeforeValidator(common_validators.validate_or_remove('internal topology', InternalTopology, severity='major'))]` — obligatoire
- `ecu_metadata: Annotated['ECUMetadata', External(output_structure=OutputStrategy.SINGLE_FILE | OutputStrategy.OMMIT_ROOT)]` — obligatoire
- `mac_multicast_endpoints: Annotated[Optional['MACMulticastEndpoints'], External(output_structure=OutputStrategy.SINGLE_FILE | OutputStrategy.OMMIT_ROOT)]` — optionnel (défaut: Field(exclude=True, default=None))
- `multicast_groups: Optional[List[MulticastGroupMembership]]` — optionnel (défaut: Field(default_factory=list, exclude=True))
- `state_memberships: Annotated[Optional[List[StateMembershipRef]], External(output_structure=OutputStrategy.SINGLE_FILE), BeforeValidator(common_validators.validate_or_remove('state memberships', List[StateMembershipRef])), BeforeValidator(common_validators.none_to_empty_list)]` — optionnel (défaut: Field(default=[], description='Assignments of this ECU to state management groups (whole-ECU granularity).'))
- validator `skip_on_broken_controllers` (model_validator, cible: before)
- validator `resolve_topology_connections` (model_validator, cible: after)
- validator `validate_vlans_in_sockets` (model_validator, cible: after)

### `InternalConnection` (hérite de: FLYNCBaseModel)
> Represents a base internal connection between two ECU components.
- `type: str` — obligatoire
- `id: str` — obligatoire

### `ECUPortToXConnection` (hérite de: InternalConnection)
> Base class for connections from an ECU port to another ECU component.
- `ecu_port_name: Annotated[str, Reference(source='_ecu_port')]` — obligatoire

### `SwitchPortToXConnection` (hérite de: InternalConnection)
> Base class for connections from an ECU switch port to another component.
- `switch_port_name: Annotated[str, Reference(source='_switch_port')]` — obligatoire
- `switch_name: Annotated[Optional[str], Reference(source='_switch')]` — optionnel (défaut: Field(default=None, alias='switch'))

### `ControllerInterfaceToXConnection` (hérite de: InternalConnection)
> Base class for connections from an controller interface to another component inside an ECU.
- `iface_name: Annotated[str, Reference(source='_iface')]` — obligatoire
- `controller_name: Annotated[Optional[str], Reference(source='_controller')]` — optionnel (défaut: Field(default=None, alias='controller'))

### `ECUPortToSwitchPort` (hérite de: ECUPortToXConnection, SwitchPortToXConnection)
> Represents a connection from an ECU port to a switch port.
- `type: Literal['ecu_port_to_switch_port']` — obligatoire

### `ECUPortToControllerInterface` (hérite de: ECUPortToXConnection, ControllerInterfaceToXConnection)
> Represents a connection from an ECU port to a controller interface.
- `type: Literal['ecu_port_to_controller_interface']` — obligatoire

### `SwitchPortToControllerInterface` (hérite de: SwitchPortToXConnection, ControllerInterfaceToXConnection)
> Represents a connection from a switch port to a controller interface.
- `type: Literal['switch_port_to_controller_interface']` — obligatoire

### `SwitchPortToSwitchPort` (hérite de: SwitchPortToXConnection)
> Represents a connection between two switch ports on the same ECU.
- `type: Literal['switch_to_switch_same_ecu']` — obligatoire
- `switch2_port_name: Annotated[str, Reference(source='_switch2_port')]` — obligatoire
- `switch2_name: Annotated[Optional[str], Reference(source='_switch2')]` — optionnel (défaut: Field(default=None, alias='switch2'))

### `ControllerInterfaceToControllerInterface` (hérite de: ControllerInterfaceToXConnection)
> Represents a direct connection between two controller interfaces in an ECU.
- `type: Literal['controller_interface_to_controller_interface']` — obligatoire
- `iface2_name: Annotated[str, Reference(source='_iface2')]` — obligatoire
- `controller2_name: Annotated[Optional[str], Reference(source='_controller2')]` — optionnel (défaut: Field(default=None, alias='controller2'))

### `InternalConnectionUnion` (hérite de: RootModel)
> Union type representing a connection between two internal ECU components.
- `root: ECUPortToSwitchPort | ECUPortToControllerInterface | SwitchPortToControllerInterface | SwitchPortToSwitchPort | ControllerInterfaceToControllerInterface` — obligatoire

### `InternalTopology` (hérite de: FLYNCBaseModel)
> Parameters
- `connections: List[InternalConnectionUnion]` — optionnel (défaut: Field(default_factory=list))

### `LINFrameRef` (hérite de: FLYNCBaseModel)
> Reference to a LIN frame by bus and LIN ID.
- `bus_ref: str` — obligatoire
- `frame_ref: int` — obligatoire

### `LINMasterInterface` (hérite de: ControllerInterface)
> LIN interface for a controller acting as LIN master on a bus.
- `name: Annotated[str, Implied(strategy=ImpliedStrategy.FILE_NAME)]` — obligatoire
- `node_type: Literal['master']` — optionnel (défaut: Field(default='master'))
- `bus_ref: str` — obligatoire
- `lin_protocol: _LINProtocol` — obligatoire
- `p2_min: float` — obligatoire
- `st_min: float` — obligatoire
- `sender_frames: List[LINFrameRef]` — optionnel (défaut: Field(default_factory=list))

### `LINSlaveInterface` (hérite de: ControllerInterface)
> LIN interface for a controller acting as LIN slave on a bus.
- `name: Annotated[str, Implied(strategy=ImpliedStrategy.FILE_NAME)]` — obligatoire
- `node_type: Literal['slave']` — optionnel (défaut: Field(default='slave'))
- `bus_ref: str` — obligatoire
- `lin_protocol: _LINProtocol` — obligatoire
- `configured_nad: Annotated[int, Field(ge=0, le=255)]` — obligatoire
- `initial_nad: Annotated[int, Field(ge=0, le=255)]` — obligatoire
- `product_id: Optional[str]` — optionnel (défaut: Field(default=None))
- `response_error: Optional[str]` — optionnel (défaut: Field(default=None))
- `receiver_frames: List[LINFrameRef]` — optionnel (défaut: Field(default_factory=list))

### `MACMulticastEndpoint` (hérite de: FLYNCBaseModel)
> Represents a multicast endpoint that is bound to a specific controller.
- `name: str` — obligatoire
- `mac_address: FLYNCMacAddress` — obligatoire
- `protocol: str` — obligatoire
- `ethertype: Optional[int]` — optionnel (défaut: Field(description='EtherType that is expected on this endpoint.', ge=0, le=65535, default=None))
- `vlan_id: Annotated[Optional[int], AfterValidator(validate_vlan_id)]` — optionnel (défaut: Field(description='VLAN ID expected on this endpoint (``None`` for untagged).', default=None))
- `multicast_tx: Optional[List[Annotated[FLYNCMacAddress, AfterValidator(validate_mac_multicast)]]]` — optionnel (défaut: Field(description='List of multicast addresses that this endpoint should             transmit to.', default=[]))

### `AVTPMulticastEndpoint` (hérite de: MACMulticastEndpoint)
> Represents an AVTP multicast endpoint that is bound to a specific controller.
- `ethertype: Literal[8944]` — optionnel (défaut: Field(default=8944))
- `protocol: Literal['avtp'] | Literal['AVTP']` — obligatoire
- validator `validate_avtp_multicast_range` (field_validator, cible: ['multicast_tx'])

### `MACEndpointUnion` (hérite de: RootModel)
> Union type for MAC multicast endpoints, discriminated by the 'ethertype'
- `root: AVTPMulticastEndpoint` — obligatoire

### `MACMulticastEndpoints` (hérite de: FLYNCBaseModel)
> Represents a collection of multicast endpoints for an ECU.
- `endpoints: List[MACEndpointUnion]` — optionnel (défaut: Field(default_factory=list))

### `MulticastGroupMembership` (hérite de: FLYNCBaseModel)
> Represents a multicast group membership for virtual controller interfaces.
- `group: Annotated[IPvAnyAddress | FLYNCMacAddress, AfterValidator(common_validators.validate_any_multicast_address)]` — obligatoire
- `description: Optional[str]` — optionnel (défaut: Field(default=''))
- `mode: Literal['tx'] | Literal['rx']` — optionnel (défaut: Field(default='rx'))
- `vlan: Annotated[Optional[int], AfterValidator(validate_vlan_id)]` — optionnel (défaut: Field(default=0))
- `src_ip: Optional[IPvAnyAddress]` — optionnel (défaut: Field(default=None))
- `solicited_node_multicast: Optional[bool]` — optionnel (défaut: Field(default=False))
- validator `validate_src_ip_set_on_tx_ip_groups` (model_validator, cible: after)

### `BASET1` (hérite de: FLYNCBaseModel)
> Represents a BASE-T1 Ethernet interface configuration.
- `mode: Literal['base_t1']` — optionnel (défaut: Field(default='base_t1'))
- `speed: Literal[100, 1000]` — optionnel (défaut: Field(default=100))
- `duplex: Literal['full']` — optionnel (défaut: Field(default='full'))
- `role: Literal['master', 'slave']` — optionnel (défaut: Field(default='slave'))
- `autonegotiation: bool` — optionnel (défaut: Field(default=False))

### `BASET1S` (hérite de: FLYNCBaseModel)
> Represents a BASE-T1S Ethernet interface configuration.
- `mode: Literal['base_t1s']` — optionnel (défaut: Field(default='base_t1s'))
- `speed: Literal[10]` — optionnel (défaut: Field(default=10))
- `duplex: Literal['half']` — optionnel (défaut: Field(default='half'))
- `role: Literal['master', 'slave']` — obligatoire
- `autonegotiation: bool` — optionnel (défaut: Field(default=False))

### `BASET` (hérite de: FLYNCBaseModel)
> Represents a BASE-T Ethernet interface configuration.
- `mode: Literal['base_t']` — optionnel (défaut: Field(default='base_t'))
- `speed: Literal[100, 1000]` — obligatoire
- `duplex: Literal['full']` — optionnel (défaut: Field(default='full'))
- `role: Literal['master', 'slave']` — optionnel (défaut: Field(default='slave'))
- `autonegotiation: bool` — optionnel (défaut: Field(default=False))

### `MII` (hérite de: FLYNCBaseModel)
> Represents a Media Independent Interface (MII) configuration.
- `type: Literal['mii']` — optionnel (défaut: Field(default='mii'))
- `speed: Optional[Literal[10, 100]]` — optionnel (défaut: Field(default=100))
- `mode: Literal['mac', 'phy']` — obligatoire

### `RMII` (hérite de: FLYNCBaseModel)
> Represents a Reduced Media Independent Interface (RMII)
- `type: Literal['rmii']` — optionnel (défaut: Field(default='rmii'))
- `speed: Optional[Literal[10, 100]]` — optionnel (défaut: Field(default=100))
- `mode: Literal['mac', 'phy']` — obligatoire

### `SGMII` (hérite de: FLYNCBaseModel)
> Represents a Serial Gigabit Media Independent Interface
- `type: Literal['sgmii']` — optionnel (défaut: Field(default='sgmii'))
- `speed: Optional[Literal[10, 100, 1000, 2500]]` — optionnel (défaut: Field(default=1000))
- `mode: Literal['mac', 'phy']` — obligatoire

### `RGMII` (hérite de: FLYNCBaseModel)
> Represents a Reduced Gigabit Media Independent Interface (RGMII) configuration.
- `type: Literal['rgmii']` — optionnel (défaut: Field(default='rgmii'))
- `speed: Optional[Literal[10, 100, 1000]]` — optionnel (défaut: Field(default=1000))
- `mode: Literal['mac', 'phy']` — obligatoire

### `XFI` (hérite de: FLYNCBaseModel)
> Represents a 10-Gigabit Ethernet (10GbE) serial electrical interface
- `type: Literal['xfi']` — optionnel (défaut: Field(default='xfi'))
- `speed: Literal[10000]` — optionnel (défaut: Field(default=10000))
- `mode: Literal['mac', 'phy']` — obligatoire

### `ECUPort` (hérite de: FLYNCBaseModel)
> Represents an ECU port and its configuration.
- `name: str` — obligatoire
- `mdi_config: BASET1 | BASET1S | BASET` — optionnel (défaut: Field(default_factory=BASET1, discriminator='mode', description='how to use this'))
- `mii_config: Optional[MII | RMII | SGMII | RGMII | XFI]` — optionnel (défaut: Field(default=None, discriminator='type'))
- validator `verify_mdi_and_mii_config_have_same_speed` (model_validator, cible: after)

### `RouteEntry` (hérite de: FLYNCBaseModel)
> Represents a static routing table entry.
- `destination: IPv4AddressEntry | IPv6AddressEntry` — obligatoire
- `default_gateway: IPvAnyAddress` — obligatoire
- `egress_interface: str` — obligatoire

### `SocketContainer` (hérite de: FLYNCBaseModel)
> Represents a socket container for the ecu.
- `name: Annotated[str, Implied(strategy=ImpliedStrategy.FILE_NAME)]` — obligatoire
- `vlan_id: Annotated[Optional[int], AfterValidator(common_validators.validate_vlan_id)]` — optionnel (défaut: Field(default=0))
- `sockets: Annotated[Optional[List[Annotated[Union[SocketTCP, SocketUDP], Field(discriminator='protocol')]]], BeforeValidator(common_validators.validate_list_items_and_remove('socket', Annotated[Union[SocketTCP, SocketUDP], Field(discriminator='protocol')], severity='minor'))]` — optionnel (défaut: Field(default_factory=list))

### `DeploymentUnion` (hérite de: RootModel)
> Union type representing a deployment configuration for a socket. This model wraps a union of different deployment models and uses the
- `root: SOMEIPServiceConsumer | SOMEIPServiceProvider | SOMEIPSDDeployment | PDUSender | PDUReceiver | PDUForwarder` — obligatoire

### `Socket` (hérite de: FLYNCBaseModel)
> Defines a virtual-interface socket that is bound to a specific IP
- `name: str` — obligatoire
- `endpoint_address: IPvAnyAddress` — obligatoire
- `port_no: int` — obligatoire
- `deployments: Optional[List[DeploymentUnion]]` — optionnel (défaut: Field(default_factory=list))
- `endpoint_type: Optional[Literal['multicast', 'unicast']]` — optionnel (défaut: Field(default_factory=lambda x: get_endpoint_type_from_address(x['endpoint_address'])))
- `multicast_tx: Optional[List[IPvAnyAddress]]` — optionnel (défaut: Field(default_factory=list))
- validator `drop_invalid_deployment` (field_validator, cible: ['deployments'])
- validator `validate_unique_forwarder_per_pdu` (model_validator, cible: after)

### `TCPOption` (hérite de: FLYNCBaseModel)
> TCP options that can be enabled for a connection.
- `tcp_profile_id: int` — obligatoire
- `nagle: Optional[StrictBool]` — optionnel (défaut: Field(default=False))
- `keepalive_enabled: Optional[StrictBool]` — optionnel (défaut: Field(default=True))
- `keepidle: Optional[int]` — optionnel (défaut: Field(default=10))
- `keepcount: Optional[int]` — optionnel (défaut: Field(default=10))
- `keepintvl: Optional[int]` — optionnel (défaut: Field(default=2))
- `user_timeout: Optional[int]` — optionnel (défaut: Field(default=28))
- `congestion_avoidance: Optional[Literal['reno', 'cubic', 'bbr']]` — optionnel (défaut: Field(default='reno'))
- `tcp_maxseg: Optional[int]` — optionnel (défaut: Field(default=1460))
- `tcp_quickack: Optional[StrictBool]` — optionnel (défaut: Field(default=False))
- `tcp_syncnt: Optional[int]` — optionnel (défaut: Field(default=6))

### `UDPOption` (hérite de: FLYNCBaseModel)
> UDP options that can be enabled for a connection.
- `udp_cork: Optional[StrictBool]` — optionnel (défaut: Field(default=False))

### `SocketTCP` (hérite de: Socket)
> Represents a TCP socket.
- `protocol: Literal['tcp']` — optionnel (défaut: Field(default='tcp'))
- `tcp_profile: int` — obligatoire

### `SocketUDP` (hérite de: Socket)
> Represents a UDP socket.
- `protocol: Literal['udp']` — optionnel (défaut: Field(default='udp'))
- `udp_options: Optional[UDPOption]` — optionnel (défaut: Field(default=UDPOption(udp_cork=False)))

### `IPv4AddressEndpoint` (hérite de: IPv4AddressEntry)
> Represents an IPv4 address endpoint for a network interface.
- `sockets: Optional[List[Annotated[Union[SocketTCP, SocketUDP], Field(discriminator='protocol')]]]` — optionnel (défaut: Field(default_factory=list, exclude=True))
- validator `check_if_sockets_have_the_same_ip` (model_validator, cible: after)

### `IPv6AddressEndpoint` (hérite de: IPv6AddressEntry)
> Represents an IPv6 address endpoint for a network interface.
- `sockets: Optional[List[Annotated[Union[SocketTCP, SocketUDP], Field(discriminator='protocol')]]]` — optionnel (défaut: Field(default_factory=list, exclude=True))
- validator `check_if_sockets_have_the_same_ip` (model_validator, cible: after)

### `SwitchPort` (hérite de: FLYNCBaseModel)
> Represents a Switch Port and its configuration.
- `name: str` — obligatoire
- `silicon_port_no: int` — obligatoire
- `default_vlan_id: int` — obligatoire
- `mii_config: Optional[MII | RMII | SGMII | RGMII | XFI]` — optionnel (défaut: Field(default=None, discriminator='type'))
- `ptp_config: Annotated[Optional[PTPConfig], BeforeValidator(common_validators.validate_or_remove('PTP config', PTPConfig))]` — optionnel (défaut: Field(default=None))
- `ingress_streams: Annotated[Optional[List[Stream]], BeforeValidator(common_validators.validate_or_remove('ingress streams', List[Stream])), BeforeValidator(common_validators.none_to_empty_list)]` — optionnel (défaut: Field(default=[]))
- `traffic_classes: Annotated[Optional[List[TrafficClass]], AfterValidator(common_validators.validate_traffic_classes), BeforeValidator(common_validators.validate_or_remove('traffic classes', List[TrafficClass])), BeforeValidator(common_validators.none_to_empty_list)]` — optionnel (défaut: Field(default=[]))
- `macsec_config: Annotated[Optional[MACsecConfig], BeforeValidator(common_validators.validate_or_remove('MACsec config', MACsecConfig))]` — optionnel (défaut: Field(default=None))
- validator `validate_traffic_classes` (model_validator, cible: after)

### `PortScopedAction` (hérite de: FLYNCBaseModel)
> Base class for TCAM actions whose ``ports`` list defaults to all switch ports

### `Drop` (hérite de: PortScopedAction)
> Action that discards traffic on the selected egress ports.
- `type: Literal['drop']` — optionnel (défaut: Field(default='drop'))
- `ports: Optional[List[str]]` — optionnel (défaut: Field(default_factory=list))

### `Mirror` (hérite de: PortScopedAction)
> Action that mirrors incoming traffic to additional egress ports.
- `type: Literal['mirror']` — optionnel (défaut: Field(default='mirror'))
- `ports: Optional[List[str]]` — optionnel (défaut: Field(default_factory=list))

### `ForceEgress` (hérite de: PortScopedAction)
> Action that forces a packet to leave through a given set of ports, bypassing the normal forwarding decision.
- `type: Literal['force_egress']` — optionnel (défaut: Field(default='force_egress'))
- `ports: Optional[List[str]]` — optionnel (défaut: Field(default_factory=list))

### `VLANOverwrite` (hérite de: PortScopedAction)
> Action that overwrites VLAN ID and/or PCP values on selected ports.
- `type: Literal['vlan_overwrite']` — optionnel (défaut: Field(default='vlan_overwrite'))
- `overwrite_vlan_id: Annotated[Optional[int], AfterValidator(validate_vlan_id)]` — optionnel (défaut: Field(default=None))
- `overwrite_vlan_pcp: Optional[int]` — optionnel (défaut: Field(default=None))
- `ports: Optional[List[str]]` — optionnel (défaut: Field(default_factory=list))

### `RemoveVLAN` (hérite de: PortScopedAction)
> Action that removes the VLAN tag from packets on the given ports.
- `type: Literal['remove_vlan']` — optionnel (défaut: Field(default='remove_vlan'))
- `ports: Optional[List[str]]` — optionnel (défaut: Field(default_factory=list))

### `FrameMask` (hérite de: FLYNCBaseModel)
> Byte-level pattern matching of an Ethernet frame.
- `offset: int` — obligatoire
- `data: str` — obligatoire
- `mask: str` — obligatoire
- `frame_window: int` — optionnel (défaut: Field(default=96))
- validator `_require_string` (field_validator, cible: ['data', 'mask'])
- validator `_normalize_format` (field_validator, cible: ['data', 'mask'])
- validator `validate_widths_and_window` (model_validator, cible: after)

### `TCAMRule` (hérite de: FLYNCBaseModel)
> Definition of a TCAM (ternary content-addressable memory) rule for a
- `name: str` — obligatoire
- `id: StrictInt` — obligatoire
- `match_filter: Optional[FrameFilter]` — optionnel (défaut: Field(default=None))
- `frame_mask: Optional[FrameMask]` — optionnel (défaut: Field(default=None))
- `match_ports: Optional[List[str]]` — optionnel (défaut: Field(default_factory=list))
- `action: List[Drop | Mirror | VLANOverwrite | ForceEgress | RemoveVLAN]` — obligatoire
- `vehicle_state: Optional[int]` — optionnel (défaut: Field(default=None, ge=0, le=255))
- `vehicle_state_mask: Optional[int]` — optionnel (défaut: Field(default=None, gt=0, le=255))
- validator `validate_vehicle_state` (model_validator, cible: after)
- validator `validate_match_filter_or_mask_exclusive` (model_validator, cible: after)
- validator `validate_exclusive_drop_force_mirror` (model_validator, cible: after)
- validator `validate_exclusive_vlan_action` (model_validator, cible: after)

### `Switch` (hérite de: FLYNCBaseModel)
> Represents an automotive Ethernet network switch configuration.
- `name: str` — obligatoire
- `tcam_rules: Annotated[Optional[List[TCAMRule]], BeforeValidator(common_validators.none_to_empty_list)]` — optionnel (défaut: Field(default=[]))
- `ports: List[SwitchPort]` — obligatoire
- `vlans: List[VLANEntry]` — obligatoire
- `host_controller: Optional[EthernetInterfaceConfig]` — optionnel (défaut: Field(default=None))
- `meta: EmbeddedMetadata` — obligatoire
- validator `validate_unique_port_number` (model_validator, cible: after)
- validator `validate_unique_port_names` (model_validator, cible: after)
- validator `validate_ipv_mapping` (model_validator, cible: after)
- validator `validate_ats_instances` (model_validator, cible: after)
- validator `validate_ports_in_tcam_exist` (model_validator, cible: after)
- validator `validate_tcam_ids_unique` (model_validator, cible: after)
- validator `validate_tcam_name_unique` (model_validator, cible: after)

### `MulticastGroup` (hérite de: FLYNCBaseModel)
> Represents a multicast group configuration.
- `address: IPvAnyAddress | FLYNCMacAddress` — obligatoire
- `ports: List[str]` — obligatoire
- validator `validate_multicast_address` (field_validator, cible: ['address'])

### `VLANEntry` (hérite de: FLYNCBaseModel)
> Represents a VLAN entry for a switch.
- `name: str` — obligatoire
- `id: Annotated[int, AfterValidator(common_validators.validate_vlan_id)]` — obligatoire
- `default_priority: int` — obligatoire
- `ports: List[str]` — obligatoire
- `multicast: List[MulticastGroup] | None` — optionnel (défaut: Field(default=[]))
- validator `normalize_multicast` (field_validator, cible: ['multicast'])

### Dépendances croisées
- `flync.model.flync_4_signal.forwarder` -> CANFrameForwarder, PDUForwarder
- `flync.model.flync_4_app.app_bindings` -> AppBindings
- `flync.model.flync_4_metadata.metadata` -> EmbeddedMetadata
- `flync.model.flync_4_nm` -> StateMembershipRef
- `flync.model.flync_4_security` -> Firewall, MACsecConfig
- `flync.model.flync_4_tsn` -> HTBInstance, PTPConfig, Stream, TrafficClass, FrameFilter
- `flync.model.flync_4_metadata` -> ECUMetadata, EmbeddedMetadata
- `flync.model.flync_4_nm.state_management` -> EffectiveMember
- `flync.model.flync_4_someip` -> SOMEIPServiceConsumer, SOMEIPServiceDeployment, SOMEIPServiceProvider, SOMEIPSDDeployment
- `flync.model.flync_4_signal.pdu_deployment` -> PDUReceiver, PDUSender