"""
Static automotive/AUTOSAR knowledge base.

Same principle as networking_rules.py: stable domain facts, written once,
not re-scraped on every run.

Grounded in: ISO 11898 (CAN), ISO 17987 (LIN), ISO 17458 (FlexRay),
AUTOSAR SWS (NM, SecOC, SOME/IP, Application layer), IEEE 1588/802.1AS,
Semantic Versioning 2.0.0, PEP 440.
"""

IN_VEHICLE_BUS_RULES = [
    "CAN arbitration is non-destructive: the frame with the lowest ID wins bit-by-bit, the loser retransmits later",
    "Standard CAN uses an 11-bit ID (2,048 values); Extended CAN uses a 29-bit ID, both can coexist on the same bus",
    "CAN FD extends payload to 64 bytes and adds a Bit Rate Switch (BRS) for a faster data-phase transmission",
    "LIN is single-master/multi-slave: the master's PID in the header determines which slave responds, no arbitration needed",
    "FlexRay splits its communication cycle into a deterministic Static Segment (fixed slots) and a Dynamic Segment (on-demand slots)",
    "Automotive Ethernet (100BASE-T1/1000BASE-T1) is switch-based and full-duplex, unlike the shared-bus model of CAN/LIN",
]

BOUNDARY_VALUE_RULES = [
    "Standard CAN ID range: 0 to 2047 (11 bits); Extended CAN ID range: 0 to 536,870,911 (29 bits)",
    "Classic CAN DLC (payload) range: 0 to 8 bytes; CAN FD DLC range: 0 to 64 bytes (non-linear encoding above 8)",
    "LIN payload range: 0 to 8 bytes; LIN identifies up to 16 slave nodes per master",
    "FlexRay frame payload range: 0 to 254 bytes; FlexRay static slot count and cycle length are configuration-bound upper limits",
    "SOME/IP TP (Transport Protocol / segmentation) activates once payload exceeds the configured UDP segment size threshold",
]

TSN_QOS_RULES = [
    "TSN traffic shaping assigns each Ethernet stream to a Traffic Class, each with its own priority and bandwidth reservation",
    "CBS (Credit-Based Shaper) limits a stream's transmission rate via an idle/send credit that must stay within configured min/max bounds",
    "ATS (Asynchronous Traffic Shaping) and HTB (Hierarchical Token Bucket) provide alternative rate-limiting/queueing strategies for non-AVB traffic classes",
    "Per-stream filtering and policing (ingress) enforce that incoming traffic conforms to its declared rate before being queued for egress shaping",
]

DIAGNOSTICS_RULES = [
    "DoIP (Diagnostics over IP, ISO 13400) tunnels UDS diagnostic requests over TCP/UDP to ECUs on an Ethernet-based vehicle network",
    "A DoIP routing activation must succeed before diagnostic (UDS) requests are accepted by the target ECU",
]

PDU_VARIANT_RULES = [
    "A MultiplexedPDU's active signal group is selected by a mux selector value; an undefined selector value is an invalid configuration",
    "A ContainerPDU packages multiple independent PDUs together; a ContainedPDURef pointing to a non-existent PDU is a dangling reference",
]

MIDDLEWARE_RULES = [
    "SOME/IP Methods are Request/Response (two-way) or Fire & Forget (one-way)",
    "SOME/IP Events require a prior Subscribe via SOME/IP-SD before the server starts sending Notifications",
    "SOME/IP Fields combine a Getter and Setter (two-way, Request/Response) with a Notifier (one-way, like an Event)",
    "SOME/IP-SD Offer/Find/Subscribe messages use IP multicast for dynamic service discovery",
    "Each SOME/IP Service Identifier must be unique system-wide; two services sharing the same ID is a configuration error",
    "A SOMEIPServiceDeployment binds a service to a Layer4Endpoint (IP + port) over either UDP or TCP -- a deployment missing this endpoint cannot be reached",
    "A SOMEIPServiceConsumer must reference a Service Interface and Eventgroup that are actually declared on the provider side, or the subscription is dangling",
]

NETWORK_MANAGEMENT_RULES = [
    "AUTOSAR NM keeps a bus awake as long as any node is sending periodic NM messages; absence for a timeout period triggers sleep",
    "CAN NM messages carry no application data by default — only a Source Node ID and a Control Bit Vector",
    "FlexRay NM can separate NM-Vote (fast, sleep-readiness voting) from NM-Data (slower, fuller node state)",
    "UDP NM supports Partial Network (PN) management via a PNI bit, waking only the ECUs relevant to a requested function",
]

SECURITY_RULES = [
    "SecOC adds a Message Authentication Code (MAC) plus a monotonic Freshness Value to a PDU to prevent tampering and replay attacks",
    "SecOC does not encrypt the payload — it only authenticates it; confidentiality requires a separate mechanism (e.g. TLS)",
    "MACsec secures Ethernet traffic link-by-link (Layer 2, hop-by-hop) using a shared key established via MKA",
    "IPsec ESP encrypts + authenticates IP packets; IPsec AH authenticates only, without encryption",
    "TLS establishes a session key via an asymmetric handshake, then encrypts application data symmetrically",
]

FIREWALL_RULES = [
    "A FirewallRule matches traffic by source/destination address and port, then applies an action (e.g. Allow, Drop)",
    "Firewall destination port values must fall within the valid 0-65535 range; a rule referencing a port outside this range is invalid",
    "A Firewall rule referencing a non-existent network interface or ECU identifier is a dangling reference and must fail validation",
    "Overlapping Firewall rules are evaluated in a defined precedence order; a more specific rule should not be silently shadowed by a broader one",
]

APP_RULES = [
    "An App groups a ServiceProviderReference and/or a ServiceConsumerReference, describing what services it offers or consumes",
    "A ServiceProviderReference/ServiceConsumerReference must point to a service (e.g. SOME/IP or transport service) that actually exists in the system configuration -- a reference to an undefined service is dangling",
    "AppBindings map an App to a specific ECU controller; an App with no binding is never deployed to any controller",
    "The same App can be referenced by AppBindings on multiple controllers, but each App identifier must be unique system-wide",
]

METADATA_VERSIONING_RULES = [
    "SystemMetadata and software versions follow Semantic Versioning 2.0.0 (MAJOR.MINOR.PATCH), e.g. '2.1.4'; '0.0.0' is the valid lower boundary",
    "HardwareBaseMetadata/SoftwareBaseMetadata version strings must parse as valid semver or PEP 440 depending on context -- a malformed version string (e.g. missing a required segment) must fail validation",
    "Every ECUMetadata identifier must be unique system-wide; two ECUs sharing the same metadata ID is a duplicate-identifier error",
    "EmbeddedMetadata (e.g. controller_metadata) must reference a parent ECU identifier that is actually declared in ecu_metadata -- otherwise it is a dangling reference",
]

ALL_AUTOMOTIVE_RULES = (
    IN_VEHICLE_BUS_RULES
    + BOUNDARY_VALUE_RULES
    + MIDDLEWARE_RULES
    + TSN_QOS_RULES
    + DIAGNOSTICS_RULES
    + PDU_VARIANT_RULES
    + NETWORK_MANAGEMENT_RULES
    + SECURITY_RULES
    + FIREWALL_RULES
    + APP_RULES
    + METADATA_VERSIONING_RULES
)