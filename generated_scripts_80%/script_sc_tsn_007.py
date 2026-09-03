import sys
from flync.model.flync_4_tsn.qos import FrameFilter
from pydantic import IPv4AddressEntry, IPv6AddressEntry, MACAddressEntry, ValueRange

scenario = {
    'type': 'Positive',
    'description': 'Define a FrameFilter that matches Ethernet type 0x0800 (IPv4) and source MAC address 00:11:22:33:44:55; all required fields are supplied.'
}

frame_filter = FrameFilter(
    ethertype=0x0800,
    src_mac='00:11:22:33:44:55',
    dst_mac=None,
    vlan_tagged=False,
    vlanid=None,
    pcp=None,
    src_ipv4=[IPv4AddressEntry('192.168.1.100')],
    dst_ipv4=None,
    src_ipv6=None,
    dst_ipv6=None,
    protocol='tcp',
    src_port=None,
    dst_port=None
)

print("SUCCESS")
sys.exit(0)