"""
Static networking knowledge base.

Unlike the FLYNC docs (which change often and are re-scraped every run),
these rules are stable reference facts about IP-layer protocols. Written
once, updated manually if needed — no scraping pipeline for this file.

Grounded in: RFC 791 (IPv4), RFC 8200 (IPv6), RFC 768 (UDP), RFC 9293 (TCP),
RFC 792 (ICMP), RFC 826 (ARP), RFC 2131 (DHCP), IEEE 1588 (PTP), IEEE 802.1AS (gPTP).
"""

IP_LAYER_RULES = [
    "IPv4 addresses are 32-bit; IPv6 addresses are 128-bit — both must be unique per host on a network",
    "TTL (IPv4) / Hop Limit (IPv6) range is 0-255; reaching 0 causes the packet to be dropped",
    "IPv6 removes header checksum and fragmentation fields present in IPv4 — fragmentation is handled by the sender only",
    "IPv4 header length (IHL) minimum is 20 bytes (no options); maximum is 60 bytes (with options)",
]

TRANSPORT_LAYER_RULES = [
    "UDP is connectionless: no handshake, no delivery guarantee, no retransmission",
    "TCP is connection-oriented: requires a 3-way handshake (SYN, SYN-ACK, ACK) before data transfer",
    "TCP guarantees ordered, reliable delivery via sequence numbers and acknowledgments; UDP does not",
    "A TCP connection closes via a FIN/ACK exchange on both sides",
    "Port numbers range 0-65535; ports 0-1023 are reserved/well-known (e.g. DoIP uses 13400)",
]

DIAGNOSTIC_AND_RESOLUTION_RULES = [
    "ICMP Echo Request/Reply (ping) verifies reachability; ICMP Destination Unreachable signals routing failures",
    "ARP resolves an IP address to a MAC address via broadcast request + unicast reply, valid only on the local network segment",
    "NDP (Neighbor Discovery Protocol, IPv6) replaces ARP for IPv6: it uses ICMPv6 Neighbor Solicitation/Advertisement over solicited-node multicast addresses to resolve link-layer addresses",
    "DHCP assigns IP addresses dynamically via the DORA sequence: Discover, Offer, Request, Acknowledge",
    "DoIP (ISO 13400) runs diagnostics over TCP/UDP port 13400, requiring a routing activation handshake before UDS requests are accepted",
]

ETHERNET_LINK_RULES = [
    "Standard Ethernet MTU is 1500 bytes; a frame or aggregated payload exceeding this must be rejected or fragmented at a higher layer",
    "Minimum Ethernet frame size is 64 bytes (including header and FCS); frames below this are invalid runt frames",
    "IGMP (Internet Group Management Protocol) lets hosts join/leave IPv4 multicast groups; switches use IGMP snooping to forward multicast only to interested ports",
]

VLAN_AND_MULTICAST_RULES = [
    "VLAN tagging (802.1Q) segments Ethernet traffic into isolated broadcast domains sharing the same physical switch",
    "A multicast group requires at least one reachable transmitter (TX) for every receiver (RX) in the group",
    "Switches must have the correct VLAN entry for a multicast group before traffic can be forwarded to all members",
]

TIME_SYNC_RULES = [
    "PTP (IEEE 1588) synchronizes clocks via Sync/Delay_Req/Delay_Resp message exchange and the Best Master Clock Algorithm (BMCA)",
    "gPTP (IEEE 802.1AS) is a PTP profile restricted to Ethernet Layer 2, using peer-delay measurement on every link (no end-to-end delay)",
    "BMCA elects a Grandmaster automatically based on clock quality attributes carried in Announce messages, and re-elects on failure",
]

ALL_NETWORKING_RULES = (
    IP_LAYER_RULES
    + TRANSPORT_LAYER_RULES
    + DIAGNOSTIC_AND_RESOLUTION_RULES
    + ETHERNET_LINK_RULES
    + VLAN_AND_MULTICAST_RULES
    + TIME_SYNC_RULES
)