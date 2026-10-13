"""
Aggregates the static networking + automotive knowledge bases and the
fault-injection patterns used to steer Negative scenario generation.
"""
from phase1.knowledge_base.networking_rules import ALL_NETWORKING_RULES
from phase1.knowledge_base.automotive_rules import ALL_AUTOMOTIVE_RULES

FAULT_PATTERNS = [
    "duplicate identifier (IP, MAC, Service ID, Frame ID)",
    "size mismatch between container and contained element (DLC vs PDU length)",
    "out-of-range value at or beyond a boundary (max payload, max ID, max timeout)",
    "missing or dangling reference (forwarder pointing to a non-existent socket/ECU)",
    "cyclic reference in forwarding chains",
    "unreachable multicast/VLAN path between TX and RX",
    "replay / stale freshness value on a secured PDU",
    "malformed or unauthenticated handshake (TCP, TLS, MACsec MKA)",
]


def get_rules_for(submodel_focus: str) -> dict:
    """Same shared knowledge base injected into every agent — the
    submodel-specific angle comes from the agent's own doc chunks, not
    from filtering this knowledge base.
    """
    return {
        "networking": ALL_NETWORKING_RULES,
        "automotive": ALL_AUTOMOTIVE_RULES,
        "fault_patterns": FAULT_PATTERNS,
    }