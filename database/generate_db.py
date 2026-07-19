"""
generate_db.py
--------------
One-off generator script that builds database/commands.json,
database/aliases.json and database/categories.json from a curated,
hand-verified list of Cisco CLI commands.

Run:
    python3 generate_db.py

This script is NOT part of the runtime bot. It exists so the database
can be regenerated / extended in a structured, consistent way instead
of hand-editing a huge JSON blob.
"""

import json
from pathlib import Path

HERE = Path(__file__).parent

# NA = command not applicable / not available on that platform
NA = "Not supported on this platform"


def rec(
    id_,
    title,
    category,
    aliases,
    ios,
    ios_xe,
    ios_xr,
    nx_os,
    syntax,
    example,
    purpose,
    sample_output,
    notes,
    privilege="Privileged EXEC (enable)",
    config_mode="No (this is a show/operational command)",
    related=None,
    references=None,
):
    return {
        "id": id_,
        "title": title,
        "category": category,
        "aliases": sorted(set(aliases)),
        "description": purpose,
        "ios": ios,
        "ios_xe": ios_xe,
        "ios_xr": ios_xr,
        "nx_os": nx_os,
        "syntax": syntax,
        "example": example,
        "sample_output": sample_output,
        "notes": notes,
        "privilege_level": privilege,
        "configuration_mode": config_mode,
        "related_commands": related or [],
        "references": references
        or ["https://www.cisco.com/c/en/us/support/docs/ios-nx-os-software.html"],
    }


CATEGORIES = [
    "Interfaces", "Routing", "BGP", "OSPF", "ISIS", "MPLS", "LDP", "RSVP",
    "Segment Routing", "EVPN", "VXLAN", "QoS", "ACL", "NAT", "VRF", "AAA",
    "Radius", "Tacacs", "HSRP", "VRRP", "GLBP", "PIM", "IGMP", "SNMP",
    "NetFlow", "Telemetry", "Logging", "Debug", "Security", "L2 Switching",
    "STP", "RSTP", "MST", "VLAN", "EtherChannel", "LACP", "UDLD", "CDP",
    "LLDP", "IPv4", "IPv6", "DHCP", "DNS", "NTP", "Syslog", "IP SLA",
    "Policy Based Routing", "Multicast",
]

COMMANDS = []

# ---------------------------------------------------------------- IPv4/ARP
COMMANDS.append(rec(
    "arp_table", "Show ARP Table", "IPv4",
    ["arp", "arp table", "ip arp", "show arp", "show arp table",
     "نمایش arp", "جدول arp", "میخوام arp بگیرم", "چطور arp رو ببینم"],
    ios="show ip arp", ios_xe="show ip arp", ios_xr="show arp", nx_os="show ip arp",
    syntax="show ip arp [vrf <vrf-name>] [<interface>] [<ip-address>]",
    example="show ip arp GigabitEthernet0/1",
    purpose="Displays the IPv4 ARP (Address Resolution Protocol) cache, mapping IP addresses to MAC addresses.",
    sample_output=(
        "Protocol  Address          Age (min)  Hardware Addr   Type   Interface\n"
        "Internet  10.0.0.1                -   0011.2233.4455  ARPA   GigabitEthernet0/1\n"
        "Internet  10.0.0.2               12   0011.2233.4466  ARPA   GigabitEthernet0/1"
    ),
    notes="On IOS-XR the keyword 'ip' is dropped: 'show arp'. Age '-' means the entry is for the local interface.",
    related=["show mac address-table", "show ip interface brief", "clear ip arp"],
))

COMMANDS.append(rec(
    "ip_int_brief", "Show IP Interface Brief", "IPv4",
    ["show ip int brief", "sh ip int br", "interface status", "interface summary",
     "وضعیت اینترفیس ها", "نمایش اینترفیس"],
    ios="show ip interface brief", ios_xe="show ip interface brief",
    ios_xr="show ipv4 interface brief", nx_os="show ip interface brief",
    syntax="show ip interface brief [<interface>]",
    example="show ip interface brief",
    purpose="Provides a condensed summary of IP address, interface status and protocol status for all interfaces.",
    sample_output=(
        "Interface              IP-Address      OK? Method Status                Protocol\n"
        "GigabitEthernet0/0     10.1.1.1        YES manual up                    up\n"
        "GigabitEthernet0/1     unassigned      YES unset  administratively down down"
    ),
    notes="IOS-XR uses 'show ipv4 interface brief' instead of 'show ip interface brief'.",
    related=["show interfaces", "show interfaces status"],
))

COMMANDS.append(rec(
    "show_interfaces", "Show Interfaces (detailed)", "Interfaces",
    ["show interfaces", "sh int", "interface detail", "interface counters",
     "جزئیات اینترفیس", "نمایش پورت"],
    ios="show interfaces", ios_xe="show interfaces", ios_xr="show interfaces",
    nx_os="show interface",
    syntax="show interfaces [<interface>]",
    example="show interfaces GigabitEthernet0/1",
    purpose="Displays detailed statistics for interfaces: line/protocol state, MTU, bandwidth, duplex, drops, errors, input/output rate.",
    sample_output=(
        "GigabitEthernet0/1 is up, line protocol is up\n"
        "  Hardware is iGbE, address is 0011.2233.4477\n"
        "  MTU 1500 bytes, BW 1000000 Kbit/sec, DLY 10 usec\n"
        "  5 minute input rate 1200 bits/sec, 2 packets/sec"
    ),
    notes="NX-OS uses the singular form 'show interface' (also accepts 'show interfaces').",
    related=["show ip interface brief", "show interfaces status", "show interfaces counters"],
))

COMMANDS.append(rec(
    "int_status", "Show Interfaces Status", "Interfaces",
    ["show interfaces status", "int status", "port status", "sh int status"],
    ios="show interfaces status", ios_xe="show interfaces status",
    ios_xr=NA, nx_os="show interface status",
    syntax="show interfaces status [err-disabled]",
    example="show interfaces status err-disabled",
    purpose="Compact table of switch port status, VLAN, duplex, speed and type — very useful for a fast overview.",
    sample_output=(
        "Port      Name               Status       Vlan       Duplex  Speed Type\n"
        "Gi1/0/1                      connected    10         a-full  a-1000 10/100/1000BaseTX"
    ),
    notes="This is a switching (Catalyst / Nexus) command; not present on IOS-XR routers.",
    related=["show ip interface brief", "show vlan brief"],
))

COMMANDS.append(rec(
    "clear_arp", "Clear ARP Cache", "IPv4",
    ["clear arp", "clear arp cache", "پاک کردن arp", "ریست arp"],
    ios="clear ip arp", ios_xe="clear ip arp", ios_xr="clear arp",
    nx_os="clear ip arp",
    syntax="clear ip arp [<ip-address>] [vrf <vrf-name>]",
    example="clear ip arp",
    purpose="Clears dynamic entries from the ARP cache, forcing re-resolution.",
    sample_output="(no output on success)",
    notes="Use with caution on production routers with many hosts — it causes a burst of ARP requests.",
    config_mode="No (privileged EXEC action command)",
    related=["show arp"],
))

# ---------------------------------------------------------------- IPv6
COMMANDS.append(rec(
    "show_ipv6_int_brief", "Show IPv6 Interface Brief", "IPv6",
    ["show ipv6 interface brief", "ipv6 int brief", "ipv6 status",
     "نمایش ipv6", "وضعیت ipv6"],
    ios="show ipv6 interface brief", ios_xe="show ipv6 interface brief",
    ios_xr="show ipv6 interface brief", nx_os="show ipv6 interface brief",
    syntax="show ipv6 interface brief [<interface>]",
    example="show ipv6 interface brief",
    purpose="Summarizes IPv6 addressing and interface state.",
    sample_output=(
        "GigabitEthernet0/1    [up/up]\n"
        "    fe80::211:22ff:fe33:4477\n"
        "    2001:db8::1"
    ),
    notes="Identical syntax across all four platforms.",
    related=["show ipv6 route", "show ipv6 neighbors"],
))

COMMANDS.append(rec(
    "show_ipv6_neighbors", "Show IPv6 Neighbors", "IPv6",
    ["show ipv6 neighbors", "ipv6 arp", "ipv6 neighbor table", "نمایش neighbor ipv6"],
    ios="show ipv6 neighbors", ios_xe="show ipv6 neighbors",
    ios_xr="show ipv6 neighbors", nx_os="show ipv6 neighbor",
    syntax="show ipv6 neighbors [<interface>]",
    example="show ipv6 neighbors",
    purpose="Displays the IPv6 Neighbor Discovery cache — the IPv6 equivalent of the ARP table.",
    sample_output=(
        "IPv6 Address                     Age  Link-layer Addr  State  Interface\n"
        "2001:db8::2                      0    0011.2233.4488   REACH  Gi0/1"
    ),
    notes="NX-OS uses singular 'show ipv6 neighbor'.",
    related=["show ipv6 interface brief"],
))

COMMANDS.append(rec(
    "show_ipv6_route", "Show IPv6 Route Table", "IPv6",
    ["show ipv6 route", "ipv6 routing table", "مسیریابی ipv6"],
    ios="show ipv6 route", ios_xe="show ipv6 route",
    ios_xr="show route ipv6", nx_os="show ipv6 route",
    syntax="show ipv6 route [<prefix>]",
    example="show ipv6 route 2001:db8::/32",
    purpose="Displays the IPv6 routing table.",
    sample_output="B   2001:db8::/32 [200/0]\n     via 2001:db8:100::1, GigabitEthernet0/1",
    notes="IOS-XR inverts the keyword order: 'show route ipv6' rather than 'show ipv6 route'.",
    related=["show ipv6 interface brief"],
))

# ---------------------------------------------------------------- Routing / RIB
COMMANDS.append(rec(
    "show_ip_route", "Show IP Routing Table", "Routing",
    ["show ip route", "routing table", "sh ip route", "نمایش جدول مسیریابی",
     "روت تیبل"],
    ios="show ip route", ios_xe="show ip route", ios_xr="show route",
    nx_os="show ip route",
    syntax="show ip route [vrf <name>] [<prefix>]",
    example="show ip route 10.0.0.0",
    purpose="Displays the IPv4 RIB — best paths installed for forwarding, with the owning protocol and administrative distance/metric.",
    sample_output=(
        "B    10.0.0.0/24 [20/0] via 192.0.2.1, 00:12:34\n"
        "O    10.1.0.0/24 [110/20] via 192.0.2.5, 00:05:00"
    ),
    notes="IOS-XR shortens the command to 'show route'.",
    related=["show ip protocols", "show ip cef"],
))

COMMANDS.append(rec(
    "show_ip_route_summary", "Show IP Route Summary", "Routing",
    ["show ip route summary", "route count", "خلاصه جدول مسیریابی"],
    ios="show ip route summary", ios_xe="show ip route summary",
    ios_xr="show route summary", nx_os="show ip route summary",
    syntax="show ip route summary [vrf <name>]",
    example="show ip route summary",
    purpose="Shows a per-protocol count of routes in the RIB — quick way to gauge table size and protocol contribution.",
    sample_output=(
        "Route Source    Networks    Subnets\n"
        "connected       0           4\n"
        "bgp 65001       0           184320"
    ),
    notes="Useful before/after a maintenance window to confirm route counts match expectations.",
    related=["show ip route"],
))

COMMANDS.append(rec(
    "show_ip_protocols", "Show IP Routing Protocols", "Routing",
    ["show ip protocols", "active routing protocols", "پروتکل های روتینگ فعال"],
    ios="show ip protocols", ios_xe="show ip protocols",
    ios_xr="show protocols ipv4", nx_os="show ip protocols",
    syntax="show ip protocols",
    example="show ip protocols",
    purpose="Lists all IP routing protocols currently running along with their timers, filters and networks advertised.",
    sample_output="Routing Protocol is \"bgp 65001\"\n  Sending updates every 0 seconds",
    notes="Handy first command to run when you inherit an unfamiliar router.",
    related=["show ip route"],
))

COMMANDS.append(rec(
    "ip_cef", "Show IP CEF Table", "Routing",
    ["show ip cef", "cef table", "cisco express forwarding"],
    ios="show ip cef", ios_xe="show ip cef", ios_xr="show cef",
    nx_os="show ip cef",
    syntax="show ip cef [<prefix>] [detail]",
    example="show ip cef 10.0.0.0/24 detail",
    purpose="Displays the Cisco Express Forwarding table — the actual hardware/software forwarding information base used for packet switching.",
    sample_output="10.0.0.0/24\n  nexthop 192.0.2.1 GigabitEthernet0/1",
    notes="On IOS-XR the equivalent is simply 'show cef'.",
    related=["show ip route"],
))

COMMANDS.append(rec(
    "static_route_config", "Configure a Static Route", "Routing",
    ["static route", "ip route config", "افزودن static route", "کانفیگ static route"],
    ios="ip route <prefix> <mask> <next-hop>",
    ios_xe="ip route <prefix> <mask> <next-hop>",
    ios_xr="router static\n address-family ipv4 unicast\n  <prefix>/<mask-len> <next-hop>",
    nx_os="ip route <prefix>/<mask-len> <next-hop>",
    syntax="ip route <destination-network> <subnet-mask> {<next-hop-ip> | <exit-interface>} [<AD>]",
    example="ip route 10.10.10.0 255.255.255.0 192.0.2.1",
    purpose="Creates a manually configured static route in the RIB.",
    sample_output="(no output; verify with 'show ip route static')",
    notes="IOS-XR requires entering the 'router static' configuration submode first; NX-OS uses CIDR notation directly on the ip route line.",
    privilege="Privileged EXEC + Global Configuration",
    config_mode="Yes (global configuration mode / router static submode on XR)",
    related=["show ip route"],
))

# ---------------------------------------------------------------- BGP
COMMANDS.append(rec(
    "bgp_summary", "Show BGP Summary", "BGP",
    ["show ip bgp summary", "bgp summary", "bgp neighbors summary",
     "خلاصه bgp", "چطور bgp neighbor رو ببینم", "bgp neighbor"],
    ios="show ip bgp summary", ios_xe="show ip bgp summary",
    ios_xr="show bgp summary", nx_os="show ip bgp summary",
    syntax="show ip bgp summary [vrf <name>]",
    example="show ip bgp summary",
    purpose="Displays the state of all BGP neighbors: uptime, prefixes received, and session state (Idle/Active/Established).",
    sample_output=(
        "Neighbor        V   AS  MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd\n"
        "192.0.2.1       4  65001  10234   10200     5501    0    0 3d02h        184320"
    ),
    notes="On IOS-XR use 'show bgp summary' (address-family aware — add 'show bgp ipv4 unicast summary' for explicit AFI/SAFI).",
    related=["show bgp neighbors", "show ip bgp"],
))

COMMANDS.append(rec(
    "bgp_neighbors", "Show BGP Neighbor Detail", "BGP",
    ["show ip bgp neighbors", "bgp neighbor detail", "جزئیات bgp neighbor"],
    ios="show ip bgp neighbors <ip>", ios_xe="show ip bgp neighbors <ip>",
    ios_xr="show bgp neighbors <ip>", nx_os="show ip bgp neighbors <ip>",
    syntax="show ip bgp neighbors [<neighbor-ip>]",
    example="show ip bgp neighbors 192.0.2.1",
    purpose="Detailed BGP neighbor session information: capabilities negotiated, hold/keepalive timers, message statistics, address-families.",
    sample_output="BGP neighbor is 192.0.2.1, remote AS 65001, external link\n  BGP state = Established, up for 3d02h",
    notes="Very useful for troubleshooting flapping or stuck-in-Active sessions.",
    related=["show ip bgp summary"],
))

COMMANDS.append(rec(
    "bgp_table", "Show BGP Table", "BGP",
    ["show ip bgp", "bgp table", "جدول bgp"],
    ios="show ip bgp", ios_xe="show ip bgp", ios_xr="show bgp",
    nx_os="show ip bgp",
    syntax="show ip bgp [<prefix>]",
    example="show ip bgp 10.0.0.0/24",
    purpose="Displays the BGP table (Adj-RIB / Loc-RIB) with all learned paths, AS-path, next-hop and best-path indication.",
    sample_output="*>  10.0.0.0/24     192.0.2.1     0     0 65001 65002 i",
    notes="Add 'longer-prefixes' to see all more-specifics of a given supernet.",
    related=["show ip bgp summary", "show ip route"],
))

COMMANDS.append(rec(
    "bgp_config_neighbor", "Configure a BGP Neighbor", "BGP",
    ["bgp neighbor config", "add bgp peer", "کانفیگ bgp neighbor", "افزودن پیر bgp"],
    ios="router bgp <local-as>\n neighbor <ip> remote-as <remote-as>",
    ios_xe="router bgp <local-as>\n neighbor <ip> remote-as <remote-as>",
    ios_xr="router bgp <local-as>\n neighbor <ip>\n  remote-as <remote-as>",
    nx_os="router bgp <local-as>\n neighbor <ip> remote-as <remote-as>",
    syntax="router bgp <as-number> / neighbor <ip-address> remote-as <as-number>",
    example="router bgp 65001\n neighbor 192.0.2.1 remote-as 65002",
    purpose="Establishes a new eBGP or iBGP peering relationship.",
    sample_output="(no output; verify with 'show bgp summary')",
    notes="On NX-OS/IOS-XR you must also enter the address-family (e.g. 'address-family ipv4 unicast') under the neighbor before it exchanges routes.",
    privilege="Privileged EXEC + Global Configuration",
    config_mode="Yes (router bgp submode)",
    related=["show ip bgp summary"],
))

COMMANDS.append(rec(
    "bgp_route_map", "Apply Route-map to BGP Neighbor", "BGP",
    ["bgp route-map", "route-map bgp", "فیلتر bgp با route-map"],
    ios="neighbor <ip> route-map <name> {in|out}",
    ios_xe="neighbor <ip> route-map <name> {in|out}",
    ios_xr="neighbor <ip>\n address-family ipv4 unicast\n  route-policy <name> {in|out}",
    nx_os="neighbor <ip>\n address-family ipv4 unicast\n  route-map <name> {in|out}",
    syntax="neighbor <ip-address> route-map <map-name> {in|out}",
    example="neighbor 192.0.2.1 route-map FILTER-IN in",
    purpose="Applies inbound or outbound routing policy (filtering/manipulation) to a BGP neighbor.",
    sample_output="(no output; verify with 'show route-map' and 'show ip bgp neighbors <ip> routes')",
    notes="IOS-XR uses RPL (Routing Policy Language, 'route-policy') instead of classic route-maps.",
    config_mode="Yes (router bgp / neighbor submode)",
    related=["bgp_config_neighbor"],
))

COMMANDS.append(rec(
    "bgp_clear_soft", "Clear/Reset BGP Session", "BGP",
    ["clear bgp", "reset bgp neighbor", "bgp soft reset", "ریست bgp"],
    ios="clear ip bgp <ip> soft", ios_xe="clear ip bgp <ip> soft",
    ios_xr="clear bgp <ip> soft", nx_os="clear ip bgp <ip> soft",
    syntax="clear ip bgp {<ip-address> | *} [soft [in|out]]",
    example="clear ip bgp 192.0.2.1 soft in",
    purpose="Refreshes BGP routing information with a peer without tearing down the TCP session (soft reset), or forces a hard reset if 'soft' is omitted.",
    sample_output="(no output on success)",
    notes="Prefer soft reset in production; a hard clear tears down the session and can cause a brief black-hole.",
    config_mode="No (privileged EXEC action command)",
    related=["bgp_summary"],
))

# ---------------------------------------------------------------- OSPF
COMMANDS.append(rec(
    "ospf_neighbor", "Show OSPF Neighbors", "OSPF",
    ["show ip ospf neighbor", "ospf neighbor", "ospf neighbors",
     "همسایه های ospf", "چگونه ospf neighbor را ببینم"],
    ios="show ip ospf neighbor", ios_xe="show ip ospf neighbor",
    ios_xr="show ospf neighbor", nx_os="show ip ospf neighbor",
    syntax="show ip ospf neighbor [<interface>] [detail]",
    example="show ip ospf neighbor",
    purpose="Displays OSPF adjacency state with each neighbor (Down/Init/2-Way/Full etc.).",
    sample_output=(
        "Neighbor ID     Pri   State           Dead Time   Address         Interface\n"
        "10.0.0.2          1   FULL/BDR        00:00:38    10.0.0.2        Gi0/1"
    ),
    notes="A neighbor stuck in 2-Way on a broadcast segment is normal for DROTHER routers; stuck in Exstart usually indicates an MTU mismatch.",
    related=["show ip ospf interface", "show ip protocols"],
))

COMMANDS.append(rec(
    "ospf_database", "Show OSPF Database", "OSPF",
    ["show ip ospf database", "ospf lsdb", "ospf database", "دیتابیس ospf"],
    ios="show ip ospf database", ios_xe="show ip ospf database",
    ios_xr="show ospf database", nx_os="show ip ospf database",
    syntax="show ip ospf database [router|network|summary|external] [<link-state-id>]",
    example="show ip ospf database router",
    purpose="Displays the OSPF Link-State Database (LSDB) contents by LSA type.",
    sample_output="OSPF Router with ID (10.0.0.1) (Process ID 1)\n\n Router Link States (Area 0)",
    notes="Use to confirm all routers in an area have an identical LSDB (a common cause of routing loops is a torn/desynced LSDB).",
    related=["ospf_neighbor"],
))

COMMANDS.append(rec(
    "ospf_interface", "Show OSPF Interface", "OSPF",
    ["show ip ospf interface", "ospf interface", "اینترفیس ospf"],
    ios="show ip ospf interface", ios_xe="show ip ospf interface",
    ios_xr="show ospf interface", nx_os="show ip ospf interface",
    syntax="show ip ospf interface [<interface>]",
    example="show ip ospf interface GigabitEthernet0/1",
    purpose="Shows per-interface OSPF parameters: area, cost, network type, timers, DR/BDR.",
    sample_output="GigabitEthernet0/1 is up, line protocol is up\n  Internet address 10.0.0.1/24, Area 0",
    notes="Check that Hello/Dead timers match on both sides of a link if a neighbor won't form.",
    related=["ospf_neighbor"],
))

COMMANDS.append(rec(
    "ospf_config", "Configure OSPF Process", "OSPF",
    ["ospf config", "enable ospf", "کانفیگ ospf", "فعال کردن ospf"],
    ios="router ospf <process-id>\n network <ip> <wildcard> area <area-id>",
    ios_xe="router ospf <process-id>\n network <ip> <wildcard> area <area-id>",
    ios_xr="router ospf <process-name>\n area <area-id>\n  interface <name>",
    nx_os="feature ospf\nrouter ospf <tag>\ninterface <name>\n ip router ospf <tag> area <area-id>",
    syntax="router ospf <process-id> / network <network> <wildcard-mask> area <area-id>",
    example="router ospf 1\n network 10.0.0.0 0.0.0.255 area 0",
    purpose="Enables the OSPF process and assigns interfaces/networks to an area.",
    sample_output="(no output; verify with 'show ip ospf neighbor')",
    notes="NX-OS requires 'feature ospf' first, and assigns interfaces to OSPF directly under the interface config rather than with a 'network' statement.",
    config_mode="Yes",
    related=["ospf_neighbor"],
))

# ---------------------------------------------------------------- ISIS
COMMANDS.append(rec(
    "isis_neighbor", "Show ISIS Neighbors", "ISIS",
    ["show isis neighbors", "isis neighbor", "همسایه های isis"],
    ios="show clns neighbors", ios_xe="show isis neighbors",
    ios_xr="show isis neighbors", nx_os="show isis adjacency",
    syntax="show isis neighbors [detail]",
    example="show isis neighbors detail",
    purpose="Displays IS-IS adjacency state (level, state, holdtime) with neighboring routers.",
    sample_output="System Id      Type Interface     IP Address      State Holdtime CircId\nR2               L1  Gi0/1         10.0.0.2         UP    24      02",
    notes="Classic IOS uses the legacy CLNS-based command 'show clns neighbors'; IOS-XE/XR use 'show isis neighbors'. NX-OS uses 'show isis adjacency'.",
    related=["show isis database"],
))

COMMANDS.append(rec(
    "isis_database", "Show ISIS Database", "ISIS",
    ["show isis database", "isis lsdb", "دیتابیس isis"],
    ios="show isis database", ios_xe="show isis database",
    ios_xr="show isis database", nx_os="show isis database",
    syntax="show isis database [detail]",
    example="show isis database detail",
    purpose="Displays the IS-IS Link State Database (LSPs received from all routers in the area/level).",
    sample_output="IS-IS Level-1 Link State Database\nLSPID     LSP Seq Num  LSP Checksum  LSP Holdtime",
    notes="Consistent syntax across all four platforms.",
    related=["isis_neighbor"],
))

# ---------------------------------------------------------------- MPLS / LDP / RSVP / SR
COMMANDS.append(rec(
    "mpls_interfaces", "Show MPLS Interfaces", "MPLS",
    ["show mpls interfaces", "mpls interface", "اینترفیس های mpls"],
    ios="show mpls interfaces", ios_xe="show mpls interfaces",
    ios_xr="show mpls interfaces", nx_os="show mpls interfaces",
    syntax="show mpls interfaces [<interface>]",
    example="show mpls interfaces",
    purpose="Lists interfaces that have MPLS (LDP/TE) enabled and their operational status.",
    sample_output="Interface              IP            Tunnel   BGP Static Operational\nGigabitEthernet0/1     Yes(ldp)      No       No  No        Yes",
    notes="Same syntax on all platforms.",
    related=["show mpls ldp neighbor", "show mpls forwarding-table"],
))

COMMANDS.append(rec(
    "mpls_forwarding", "Show MPLS Forwarding Table", "MPLS",
    ["show mpls forwarding-table", "mpls lfib", "جدول forwarding mpls"],
    ios="show mpls forwarding-table", ios_xe="show mpls forwarding-table",
    ios_xr="show mpls forwarding", nx_os="show mpls forwarding-table",
    syntax="show mpls forwarding-table [<prefix>]",
    example="show mpls forwarding-table 10.0.0.0",
    purpose="Displays the Label Forwarding Information Base (LFIB) — incoming/outgoing labels and next hop per prefix.",
    sample_output="Local  Outgoing    Prefix           Bytes Label   Outgoing   Next Hop\nLabel  Label       or Tunnel Id     Switched      interface\n16     Pop Label   10.0.0.0/24      1234          Gi0/1      192.0.2.1",
    notes="IOS-XR shortens this to 'show mpls forwarding'.",
    related=["mpls_interfaces"],
))

COMMANDS.append(rec(
    "ldp_neighbor", "Show MPLS LDP Neighbors", "LDP",
    ["show mpls ldp neighbor", "ldp neighbor", "همسایه های ldp"],
    ios="show mpls ldp neighbor", ios_xe="show mpls ldp neighbor",
    ios_xr="show mpls ldp neighbor", nx_os="show mpls ldp neighbor",
    syntax="show mpls ldp neighbor [<ip-address>]",
    example="show mpls ldp neighbor",
    purpose="Shows the state of LDP sessions with directly/indirectly connected LDP peers.",
    sample_output="Peer LDP Ident: 10.0.0.2:0; Local LDP Ident 10.0.0.1:0\n    TCP connection: 10.0.0.2.646 - 10.0.0.1.11021\n    State: Oper; Msgs sent/rcvd: 120/118",
    notes="Same syntax across platforms.",
    related=["mpls_interfaces"],
))

COMMANDS.append(rec(
    "ldp_bindings", "Show MPLS LDP Bindings", "LDP",
    ["show mpls ldp bindings", "ldp label bindings", "بایندینگ ldp"],
    ios="show mpls ldp bindings", ios_xe="show mpls ldp bindings",
    ios_xr="show mpls ldp bindings", nx_os="show mpls ldp bindings",
    syntax="show mpls ldp bindings [<prefix>]",
    example="show mpls ldp bindings 10.0.0.0 24",
    purpose="Displays the local and remote label bindings learned/advertised via LDP for each prefix.",
    sample_output="  10.0.0.0/24, rev 4\n        local binding:  label: 16\n        remote binding: lsr: 10.0.0.2:0, label: 22",
    notes="Compare local vs remote binding to troubleshoot label mismatches.",
    related=["ldp_neighbor"],
))

COMMANDS.append(rec(
    "rsvp_neighbor", "Show RSVP Neighbors", "RSVP",
    ["show ip rsvp neighbor", "rsvp neighbor", "همسایه rsvp"],
    ios="show ip rsvp neighbor", ios_xe="show ip rsvp neighbor",
    ios_xr="show rsvp neighbor", nx_os="show ip rsvp neighbor",
    syntax="show ip rsvp neighbor",
    example="show ip rsvp neighbor",
    purpose="Displays RSVP-TE neighbor adjacency state, used by MPLS Traffic Engineering.",
    sample_output="Neighbor         RSVP  Encapsulation\n10.0.0.2         Y     ip",
    notes="On IOS-XR drop the 'ip' keyword: 'show rsvp neighbor'.",
    related=["rsvp_tunnels"],
))

COMMANDS.append(rec(
    "rsvp_tunnels", "Show MPLS Traffic Engineering Tunnels", "RSVP",
    ["show mpls traffic-eng tunnels", "te tunnels", "تانل های te"],
    ios="show mpls traffic-eng tunnels", ios_xe="show mpls traffic-eng tunnels",
    ios_xr="show mpls traffic-eng tunnels", nx_os=NA,
    syntax="show mpls traffic-eng tunnels [brief]",
    example="show mpls traffic-eng tunnels brief",
    purpose="Displays state, bandwidth and path of RSVP-signaled MPLS-TE tunnels.",
    sample_output="Signalling Summary:\n    LSP Tunnels Process:              Running\n    Tunnel0    10.0.0.1   10.0.0.5   up     up     0        10:15:23",
    notes="MPLS-TE is not supported in the same form on NX-OS (data center platform).",
    related=["rsvp_neighbor"],
))

COMMANDS.append(rec(
    "segment_routing_isis", "Show Segment Routing (ISIS) Info", "Segment Routing",
    ["show isis segment-routing", "segment routing isis", "sr isis"],
    ios=NA, ios_xe="show isis segment-routing label table",
    ios_xr="show isis segment-routing label table", nx_os=NA,
    syntax="show isis segment-routing label table",
    example="show isis segment-routing label table",
    purpose="Displays Segment Routing (SR-MPLS) SID-to-label bindings learned via IS-IS.",
    sample_output="Label   Prefix           Level\n16001   10.0.0.1/32      L1",
    notes="Segment Routing display commands are only present on IOS-XE/XR platforms that support SR-MPLS; not on classic IOS.",
    related=["mpls_forwarding"],
))

COMMANDS.append(rec(
    "sr_te_policy", "Show Segment Routing Traffic Engineering Policy", "Segment Routing",
    ["show segment-routing traffic-eng policy", "sr-te policy", "پالیسی srte"],
    ios=NA, ios_xe="show segment-routing traffic-eng policy",
    ios_xr="show segment-routing traffic-eng policy", nx_os=NA,
    syntax="show segment-routing traffic-eng policy [name <policy-name>]",
    example="show segment-routing traffic-eng policy",
    purpose="Displays configured SR-TE policies, their candidate paths and the resulting SID list programmed into forwarding.",
    sample_output="Name: POLICY1  Status: Admin: up  Operational: up\n  Candidate-paths:\n    Preference: 100",
    notes="SR-TE is an IOS-XE/IOS-XR feature not present on classic IOS or NX-OS.",
    related=["segment_routing_isis"],
))

# ---------------------------------------------------------------- EVPN / VXLAN
COMMANDS.append(rec(
    "evpn_summary", "Show EVPN Summary", "EVPN",
    ["show bgp l2vpn evpn summary", "evpn summary", "خلاصه evpn"],
    ios=NA, ios_xe="show bgp l2vpn evpn summary",
    ios_xr="show bgp l2vpn evpn summary", nx_os="show bgp l2vpn evpn summary",
    syntax="show bgp l2vpn evpn summary",
    example="show bgp l2vpn evpn summary",
    purpose="Shows BGP EVPN address-family neighbor summary — used for EVPN-VXLAN control plane troubleshooting.",
    sample_output="Neighbor        V   AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down State/PfxRcd\n10.0.0.2        4 65001    5023    5010     102    0    0 2d04h        50",
    notes="Requires 'feature bgp' and 'feature nv overlay' on NX-OS, or the l2vpn evpn address-family activated on IOS-XE/XR.",
    related=["evpn_mac_ip"],
))

COMMANDS.append(rec(
    "evpn_mac_ip", "Show EVPN MAC-IP Table", "EVPN",
    ["show l2route evpn mac-ip", "evpn mac table", "جدول mac evpn"],
    ios=NA, ios_xe="show l2vpn evpn mac", ios_xr="show l2vpn mac-all",
    nx_os="show l2route evpn mac-ip all",
    syntax="show l2route evpn mac-ip all",
    example="show l2route evpn mac-ip all",
    purpose="Displays MAC and MAC-IP routes learned/advertised via EVPN Type-2 routes.",
    sample_output="Topo ID  Mac Address    Prod   Flags        Seq No  Next-Hops\n30       0011.2233.44aa L      Local       0       N/A",
    notes="Command name differs meaningfully per vendor OS in EVPN — always confirm against the exact software train, since EVPN CLI evolves quickly.",
    related=["evpn_summary"],
))

COMMANDS.append(rec(
    "vxlan_vni", "Show VXLAN VNI/Interfaces", "VXLAN",
    ["show nve vni", "vxlan vni", "vni های vxlan"],
    ios=NA, ios_xe="show nve vni", ios_xr="show vxlan vni", nx_os="show nve vni",
    syntax="show nve vni",
    example="show nve vni",
    purpose="Displays configured VXLAN Network Identifiers (VNIs) and their associated NVE interface state.",
    sample_output="Interface VNI      Multicast-group VNI State  Type Mode BD    cfg\nnve1      10001    n/a             Up     L2   CP   10    CLI",
    notes="Requires 'feature nv overlay' and 'feature vn-segment-vlan-based' on NX-OS.",
    related=["vxlan_peers"],
))

COMMANDS.append(rec(
    "vxlan_peers", "Show VXLAN NVE Peers", "VXLAN",
    ["show nve peers", "vxlan peers", "پیرهای vxlan"],
    ios=NA, ios_xe="show nve peers", ios_xr="show vxlan bridge-domain",
    nx_os="show nve peers",
    syntax="show nve peers",
    example="show nve peers",
    purpose="Shows remote VTEP (VXLAN Tunnel Endpoint) peers and their reachability/state.",
    sample_output="Interface Peer-IP        State LearnType Uptime   Router-Mac\nnve1      10.0.0.2       Up    CP        02:15:33 n/a",
    notes="Peer state 'Up' confirms the underlay reachability + control-plane peering is healthy.",
    related=["vxlan_vni"],
))

# ---------------------------------------------------------------- QoS
COMMANDS.append(rec(
    "qos_policy_map", "Show Policy-Map (QoS)", "QoS",
    ["show policy-map", "qos policy", "پالیسی qos"],
    ios="show policy-map interface <interface>",
    ios_xe="show policy-map interface <interface>",
    ios_xr="show policy-map interface <interface>",
    nx_os="show policy-map interface <interface>",
    syntax="show policy-map interface <interface> [input|output]",
    example="show policy-map interface GigabitEthernet0/1",
    purpose="Displays QoS policy-map statistics applied to an interface: matched classes, queue drops, byte/packet counters.",
    sample_output="Service-policy output: QOS-OUT\n  Class-map: VOICE (match-any)\n    10 packets, 1024 bytes",
    notes="Same syntax across all four platforms (MQC — Modular QoS CLI).",
    related=["qos_class_map"],
))

COMMANDS.append(rec(
    "qos_class_map", "Show Class-Map (QoS)", "QoS",
    ["show class-map", "qos class", "کلاس qos"],
    ios="show class-map", ios_xe="show class-map", ios_xr="show class-map",
    nx_os="show class-map",
    syntax="show class-map [<class-map-name>]",
    example="show class-map VOICE",
    purpose="Displays the match criteria configured within a QoS class-map.",
    sample_output="Class Map match-any VOICE (id 2)\n  Match  dscp ef (46)",
    notes="Used together with 'show policy-map' to fully audit a QoS deployment.",
    related=["qos_policy_map"],
))

# ---------------------------------------------------------------- ACL
COMMANDS.append(rec(
    "show_access_lists", "Show Access Lists", "ACL",
    ["show access-lists", "show ip access-list", "acl لیست", "نمایش acl"],
    ios="show access-lists", ios_xe="show access-lists",
    ios_xr="show access-lists", nx_os="show ip access-lists",
    syntax="show access-lists [<acl-name-or-number>]",
    example="show access-lists 101",
    purpose="Displays configured ACLs and per-entry match (hit) counters.",
    sample_output="Standard IP access list 10\n    10 permit 10.0.0.0, wildcard bits 0.0.0.255 (2 matches)",
    notes="NX-OS requires the address-family: 'show ip access-lists' (IPv4) or 'show ipv6 access-lists'.",
    related=["acl_config"],
))

COMMANDS.append(rec(
    "acl_config", "Configure an Extended ACL", "ACL",
    ["extended access-list config", "کانفیگ acl", "ساخت acl"],
    ios="ip access-list extended <name>\n permit tcp any any eq 443",
    ios_xe="ip access-list extended <name>\n permit tcp any any eq 443",
    ios_xr="ipv4 access-list <name>\n 10 permit tcp any any eq 443",
    nx_os="ip access-list <name>\n permit tcp any any eq 443",
    syntax="ip access-list extended <name> / permit|deny <protocol> <source> <destination> [operator port]",
    example="ip access-list extended WEB-ONLY\n permit tcp any any eq 443",
    purpose="Creates a named/numbered extended ACL to permit or deny traffic based on L3/L4 criteria.",
    sample_output="(no output; verify with 'show access-lists')",
    notes="IOS-XR ACL entries are explicitly sequence-numbered ('10 permit ...'); classic IOS auto-assigns sequence numbers.",
    config_mode="Yes",
    related=["show_access_lists"],
))

# ---------------------------------------------------------------- NAT
COMMANDS.append(rec(
    "nat_translations", "Show NAT Translations", "NAT",
    ["show ip nat translations", "nat table", "جدول nat"],
    ios="show ip nat translations", ios_xe="show ip nat translations",
    ios_xr="show nat44 translations", nx_os="show nat translations",
    syntax="show ip nat translations [verbose]",
    example="show ip nat translations verbose",
    purpose="Displays active NAT translation entries: inside local/global and outside local/global address pairs.",
    sample_output="Pro Inside global   Inside local     Outside local    Outside global\ntcp 203.0.113.5:1024 10.0.0.5:1024  198.51.100.9:443 198.51.100.9:443",
    notes="IOS-XR uses the NAT44-specific keyword 'show nat44 translations'.",
    related=["nat_statistics"],
))

COMMANDS.append(rec(
    "nat_statistics", "Show NAT Statistics", "NAT",
    ["show ip nat statistics", "nat stats", "آمار nat"],
    ios="show ip nat statistics", ios_xe="show ip nat statistics",
    ios_xr="show nat44 statistics", nx_os="show nat statistics",
    syntax="show ip nat statistics",
    example="show ip nat statistics",
    purpose="Shows aggregate NAT counters: active translations, hits/misses, pool usage.",
    sample_output="Total active translations: 152 (0 static, 152 dynamic; 152 extended)\nHits: 102934  Misses: 12",
    notes="A high 'Misses' count with an exhausted pool usually indicates the NAT pool needs to be expanded.",
    related=["nat_translations"],
))

# ---------------------------------------------------------------- VRF
COMMANDS.append(rec(
    "show_vrf", "Show VRF", "VRF",
    ["show vrf", "vrf list", "لیست vrf"],
    ios="show vrf", ios_xe="show vrf", ios_xr="show vrf all",
    nx_os="show vrf",
    syntax="show vrf [<vrf-name>]",
    example="show vrf CUSTOMER-A",
    purpose="Lists configured VRFs (Virtual Routing and Forwarding instances) and their Route Distinguisher / interfaces.",
    sample_output="Name             Default RD          Protocols   Interfaces\nCUSTOMER-A       65001:100           ipv4        Gi0/1.100",
    notes="IOS-XR requires the 'all' keyword to list every VRF: 'show vrf all'.",
    related=["show ip route"],
))

COMMANDS.append(rec(
    "vrf_config", "Configure a VRF", "VRF",
    ["vrf definition", "ساخت vrf", "کانفیگ vrf"],
    ios="vrf definition <name>\n rd <asn>:<id>\n address-family ipv4\n exit-address-family",
    ios_xe="vrf definition <name>\n rd <asn>:<id>\n address-family ipv4\n exit-address-family",
    ios_xr="vrf <name>\n address-family ipv4 unicast",
    nx_os="vrf context <name>\n rd <asn>:<id>",
    syntax="vrf definition <name> / rd <route-distinguisher> / address-family ipv4",
    example="vrf definition CUSTOMER-A\n rd 65001:100\n address-family ipv4\n exit-address-family",
    purpose="Creates a VRF and assigns it a Route Distinguisher, isolating a routing/forwarding table for multi-tenant or MPLS L3VPN designs.",
    sample_output="(no output; verify with 'show vrf')",
    notes="NX-OS keyword is 'vrf context' rather than 'vrf definition'.",
    config_mode="Yes",
    related=["show_vrf"],
))

# ---------------------------------------------------------------- AAA / Radius / Tacacs
COMMANDS.append(rec(
    "aaa_config", "Enable AAA New-Model", "AAA",
    ["aaa new-model", "فعال کردن aaa", "کانفیگ aaa"],
    ios="aaa new-model", ios_xe="aaa new-model",
    ios_xr="aaa authentication login default group tacacs+ local",
    nx_os="feature tacacs+\naaa authentication login default group tacacs+",
    syntax="aaa new-model",
    example="aaa new-model",
    purpose="Enables the AAA (Authentication, Authorization, Accounting) subsystem, required before any TACACS+/RADIUS configuration takes effect.",
    sample_output="(no output)",
    notes="IOS-XR does not use a separate 'aaa new-model' toggle; AAA method-lists are configured directly. NX-OS requires enabling the relevant 'feature' first.",
    config_mode="Yes",
    related=["radius_server", "tacacs_server"],
))

COMMANDS.append(rec(
    "radius_server", "Configure a RADIUS Server", "Radius",
    ["radius server config", "افزودن radius", "کانفیگ radius"],
    ios="radius server <name>\n address ipv4 <ip> auth-port 1812 acct-port 1813\n key <secret>",
    ios_xe="radius server <name>\n address ipv4 <ip> auth-port 1812 acct-port 1813\n key <secret>",
    ios_xr="radius-server host <ip> auth-port 1812 acct-port 1813\n key <secret>",
    nx_os="feature radius\nradius-server host <ip> key <secret> authentication accounting",
    syntax="radius server <name> / address ipv4 <ip> auth-port <port> acct-port <port> / key <secret>",
    example="radius server ISE-01\n address ipv4 10.0.0.50 auth-port 1812 acct-port 1813\n key MySecretKey",
    purpose="Defines a RADIUS server used for authentication/authorization/accounting.",
    sample_output="(no output; verify with 'show radius server-group all' or 'test aaa')",
    notes="NX-OS requires 'feature radius' to be enabled first.",
    config_mode="Yes",
    related=["aaa_config"],
))

COMMANDS.append(rec(
    "tacacs_server", "Configure a TACACS+ Server", "Tacacs",
    ["tacacs server config", "افزودن tacacs", "کانفیگ tacacs"],
    ios="tacacs server <name>\n address ipv4 <ip>\n key <secret>",
    ios_xe="tacacs server <name>\n address ipv4 <ip>\n key <secret>",
    ios_xr="tacacs-server host <ip>\n key <secret>",
    nx_os="feature tacacs+\ntacacs-server host <ip> key <secret>",
    syntax="tacacs server <name> / address ipv4 <ip> / key <secret>",
    example="tacacs server TACACS-01\n address ipv4 10.0.0.60\n key MySecretKey",
    purpose="Defines a TACACS+ server, typically used for device administration AAA (command authorization/accounting).",
    sample_output="(no output; verify with 'show tacacs')",
    notes="NX-OS requires 'feature tacacs+' first.",
    config_mode="Yes",
    related=["aaa_config"],
))

# ---------------------------------------------------------------- FHRP: HSRP/VRRP/GLBP
COMMANDS.append(rec(
    "hsrp_status", "Show HSRP Status", "HSRP",
    ["show standby", "hsrp status", "وضعیت hsrp"],
    ios="show standby brief", ios_xe="show standby brief",
    ios_xr="show hsrp", nx_os="show hsrp brief",
    syntax="show standby brief",
    example="show standby brief",
    purpose="Displays HSRP (Hot Standby Router Protocol) group state: Active/Standby role, priority, virtual IP.",
    sample_output="Interface  Grp  Pri P State   Active          Standby         Virtual IP\nGi0/1      10   110  Active  local           10.0.0.2        10.0.0.254",
    notes="IOS-XR uses the protocol name directly: 'show hsrp' (no 'standby' keyword, since 'standby' is IOS/IOS-XE specific CLI naming).",
    related=["vrrp_status"],
))

COMMANDS.append(rec(
    "vrrp_status", "Show VRRP Status", "VRRP",
    ["show vrrp", "vrrp status", "وضعیت vrrp"],
    ios="show vrrp brief", ios_xe="show vrrp brief",
    ios_xr="show vrrp", nx_os="show vrrp brief",
    syntax="show vrrp brief",
    example="show vrrp brief",
    purpose="Displays VRRP (Virtual Router Redundancy Protocol) group state — the open-standard equivalent of HSRP.",
    sample_output="Interface  Grp  Pri  Time  Own Pre State    Master addr     Group addr\nGi0/1      10   100  3609  Y   Y   Master   10.0.0.1        10.0.0.254",
    notes="Same syntax family across platforms; VRRP is standards-based (RFC 5798) so behaviour is consistent.",
    related=["hsrp_status"],
))

COMMANDS.append(rec(
    "glbp_status", "Show GLBP Status", "GLBP",
    ["show glbp", "glbp status", "وضعیت glbp"],
    ios="show glbp brief", ios_xe="show glbp brief",
    ios_xr=NA, nx_os="show glbp brief",
    syntax="show glbp brief",
    example="show glbp brief",
    purpose="Displays GLBP (Gateway Load Balancing Protocol) group and AVF/AVG state, allowing active-active first-hop load balancing.",
    sample_output="Interface  Grp  Fwd Pri State    Address         Active router   Standby router\nGi0/1      10   -   100 Active   10.0.0.254      local           10.0.0.2",
    notes="GLBP is a Cisco-proprietary protocol; it is not available on IOS-XR.",
    related=["hsrp_status"],
))

# ---------------------------------------------------------------- Multicast: PIM / IGMP
COMMANDS.append(rec(
    "pim_neighbor", "Show PIM Neighbors", "PIM",
    ["show ip pim neighbor", "pim neighbor", "همسایه pim"],
    ios="show ip pim neighbor", ios_xe="show ip pim neighbor",
    ios_xr="show pim neighbor", nx_os="show ip pim neighbor",
    syntax="show ip pim neighbor [<interface>]",
    example="show ip pim neighbor",
    purpose="Displays PIM (Protocol Independent Multicast) neighbor adjacency and DR (Designated Router) role per interface.",
    sample_output="Neighbor Address  Interface        Uptime/Expires   Ver  DR Prio/Mode\n10.0.0.2          GigabitEthernet0/1  3d02h/00:01:30  v2   1 / DR S P G",
    notes="Same core syntax minus the 'ip' keyword on IOS-XR.",
    related=["pim_mroute"],
))

COMMANDS.append(rec(
    "pim_mroute", "Show IP Multicast Routing Table", "PIM",
    ["show ip mroute", "mroute table", "جدول multicast"],
    ios="show ip mroute", ios_xe="show ip mroute", ios_xr="show mrib route",
    nx_os="show ip mroute",
    syntax="show ip mroute [<group-address>]",
    example="show ip mroute 239.1.1.1",
    purpose="Displays the multicast routing table: (S,G) and (*,G) entries, incoming/outgoing interface lists.",
    sample_output="(*, 239.1.1.1), 00:10:23/stopped, RP 10.0.0.9, flags: S\n  Incoming interface: Gi0/1\n  Outgoing interface list: Gi0/2, Forward/Sparse",
    notes="IOS-XR uses the MRIB (Multicast RIB) view: 'show mrib route'.",
    related=["pim_neighbor"],
))

COMMANDS.append(rec(
    "igmp_groups", "Show IGMP Groups", "IGMP",
    ["show ip igmp groups", "igmp groups", "گروه های igmp"],
    ios="show ip igmp groups", ios_xe="show ip igmp groups",
    ios_xr="show igmp groups", nx_os="show ip igmp groups",
    syntax="show ip igmp groups [<interface>]",
    example="show ip igmp groups",
    purpose="Displays multicast group membership learned via IGMP on each interface.",
    sample_output="IGMP Connected Group Membership\nGroup Address    Interface   Uptime    Expires   Last Reporter\n239.1.1.1        Gi0/1       00:10:00  00:02:30  10.0.0.5",
    notes="Consistent with the PIM naming convention (drop 'ip' on XR).",
    related=["pim_mroute"],
))

# ---------------------------------------------------------------- SNMP / NetFlow / Telemetry / Logging / Debug
COMMANDS.append(rec(
    "snmp_config", "Configure SNMP Community", "SNMP",
    ["snmp-server community", "کانفیگ snmp", "افزودن community snmp"],
    ios="snmp-server community <string> RO",
    ios_xe="snmp-server community <string> RO",
    ios_xr="snmp-server community <string> RO",
    nx_os="snmp-server community <string> ro",
    syntax="snmp-server community <community-string> {RO|RW}",
    example="snmp-server community MyReadOnly RO",
    purpose="Configures an SNMPv2c community string for read-only (RO) or read-write (RW) polling access.",
    sample_output="(no output; verify with 'show snmp community' or 'show running-config | include snmp')",
    notes="Prefer SNMPv3 with authentication/encryption for production; plain community strings are sent in clear text.",
    config_mode="Yes",
    related=["snmp_status"],
))

COMMANDS.append(rec(
    "snmp_status", "Show SNMP Status", "SNMP",
    ["show snmp", "snmp status", "وضعیت snmp"],
    ios="show snmp", ios_xe="show snmp", ios_xr="show snmp",
    nx_os="show snmp",
    syntax="show snmp",
    example="show snmp",
    purpose="Displays SNMP engine statistics: packets in/out, errors, and whether the agent is enabled.",
    sample_output="Chassis: 12345678\n123742 SNMP packets input",
    notes="Identical across all four platforms.",
    related=["snmp_config"],
))

COMMANDS.append(rec(
    "netflow_config", "Configure NetFlow / Flexible NetFlow", "NetFlow",
    ["ip flow-export", "netflow config", "کانفیگ netflow"],
    ios="ip flow-export destination <ip> <port>\ninterface <name>\n ip flow ingress",
    ios_xe="flow exporter <name>\n destination <ip>\n transport udp <port>",
    ios_xr="flow exporter-map <name>\n destination <ip>\n transport udp <port>",
    nx_os="feature netflow\nflow exporter <name>\n destination <ip> use-vrf default",
    syntax="flow exporter <name> / destination <ip> / transport udp <port>",
    example="flow exporter NF-COLLECTOR\n destination 10.0.0.100\n transport udp 2055",
    purpose="Configures NetFlow/Flexible NetFlow export of traffic flow records to a collector for visibility and capacity planning.",
    sample_output="(no output; verify with 'show flow exporter' / 'show flow monitor')",
    notes="Classic IOS uses the legacy 'ip flow-export' syntax; IOS-XE/XR/NX-OS use the newer Flexible NetFlow exporter-map model.",
    config_mode="Yes",
    related=["netflow_show"],
))

COMMANDS.append(rec(
    "netflow_show", "Show NetFlow Statistics", "NetFlow",
    ["show flow monitor", "netflow stats", "آمار netflow"],
    ios="show ip cache flow", ios_xe="show flow monitor",
    ios_xr="show flow monitor", nx_os="show flow monitor",
    syntax="show flow monitor [<name>] statistics",
    example="show flow monitor FLOW-MON-1 statistics",
    purpose="Displays exported flow statistics and cache utilization for NetFlow monitors.",
    sample_output="Cache type:                             Normal\nCache size:                             4096\nCurrent entries:                        152",
    notes="Legacy classic IOS uses the older 'show ip cache flow' command from original NetFlow (not Flexible NetFlow).",
    related=["netflow_config"],
))

COMMANDS.append(rec(
    "telemetry_config", "Configure Model-Driven Telemetry", "Telemetry",
    ["telemetry model-driven", "streaming telemetry", "کانفیگ تلمتری"],
    ios=NA, ios_xe="telemetry ietf subscription <id>\n encoding encode-kvgpb\n receiver ip address <ip> <port>",
    ios_xr="telemetry model-driven\n sensor-group <name>\n subscription <name>",
    nx_os="feature telemetry\ntelemetry\n destination-group <name>\n  ip address <ip> port <port>",
    syntax="telemetry model-driven / sensor-group <name> / subscription <name>",
    example="telemetry model-driven\n sensor-group SG1\n  sensor-path Cisco-IOS-XR-infra-statsd-oper:infra-statistics",
    purpose="Configures streaming (model-driven) telemetry, pushing YANG-modeled operational data to a collector in near real-time — a modern alternative to SNMP polling.",
    sample_output="(no output; verify with 'show telemetry model-driven subscription')",
    notes="Not available on legacy classic IOS; requires an XE/XR/NX-OS train with YANG/gRPC or gNMI support.",
    config_mode="Yes",
    related=["snmp_config"],
))

COMMANDS.append(rec(
    "logging_config", "Configure Syslog Logging Host", "Logging",
    ["logging host", "syslog config", "کانفیگ syslog"],
    ios="logging host <ip>", ios_xe="logging host <ip>",
    ios_xr="logging <ip>", nx_os="logging server <ip>",
    syntax="logging host <ip-address>",
    example="logging host 10.0.0.200",
    purpose="Configures a remote syslog server that will receive log messages generated by the device.",
    sample_output="(no output; verify with 'show logging')",
    notes="IOS-XR drops the 'host' keyword ('logging <ip>'); NX-OS uses 'logging server <ip>'.",
    config_mode="Yes",
    related=["show_logging"],
))

COMMANDS.append(rec(
    "show_logging", "Show Logging Buffer", "Logging",
    ["show logging", "log buffer", "بافر لاگ"],
    ios="show logging", ios_xe="show logging", ios_xr="show logging",
    nx_os="show logging log",
    syntax="show logging [| include <pattern>]",
    example="show logging | include %LINK",
    purpose="Displays the local logging buffer contents — the internal history of syslog messages generated by the device.",
    sample_output="000123: *Jul 19 08:00:00.123: %LINK-3-UPDOWN: Interface GigabitEthernet0/1, changed state to up",
    notes="NX-OS distinguishes 'show logging log' (the buffer) from 'show logging' (config summary).",
    related=["logging_config"],
))

COMMANDS.append(rec(
    "debug_ip_packet", "Debug IP Packet", "Debug",
    ["debug ip packet", "دیباگ پکت", "دیباگ ip"],
    ios="debug ip packet [<acl>]", ios_xe="debug ip packet [<acl>]",
    ios_xr="debug ipv4 packet", nx_os="debug ip packet",
    syntax="debug ip packet [<access-list>] [detail]",
    example="debug ip packet 101 detail",
    purpose="Enables real-time debugging of IP packets process-switched by the router, optionally filtered by an ACL.",
    sample_output="IP: s=10.0.0.5 (Gi0/1), d=10.0.0.9, len 100, rcvd 3",
    notes="Extremely CPU-intensive on production routers — always scope with an ACL and disable immediately after ('undebug all') once done.",
    config_mode="No (privileged EXEC debug command)",
    related=["show_logging"],
))

COMMANDS.append(rec(
    "debug_bgp_events", "Debug BGP Events", "Debug",
    ["debug ip bgp", "دیباگ bgp", "debug bgp events"],
    ios="debug ip bgp events", ios_xe="debug ip bgp events",
    ios_xr="debug bgp process", nx_os="debug ip bgp",
    syntax="debug ip bgp events",
    example="debug ip bgp events",
    purpose="Enables debugging of BGP finite-state-machine events — session establishment, teardown, and error notifications.",
    sample_output="BGP: 192.0.2.1 went from Idle to Active",
    notes="On a router with many peers this can generate a large volume of output; consider 'debug ip bgp <neighbor> events' to scope it, where supported.",
    config_mode="No (privileged EXEC debug command)",
    related=["bgp_summary"],
))

# ---------------------------------------------------------------- Security
COMMANDS.append(rec(
    "port_security", "Configure Port Security", "Security",
    ["switchport port-security", "امنیت پورت", "کانفیگ port security"],
    ios="interface <name>\n switchport port-security\n switchport port-security maximum 1",
    ios_xe="interface <name>\n switchport port-security\n switchport port-security maximum 1",
    ios_xr=NA,
    nx_os="interface <name>\n switchport port-security\n switchport port-security maximum 1",
    syntax="interface <name> / switchport port-security / switchport port-security maximum <n>",
    example="interface GigabitEthernet1/0/1\n switchport port-security\n switchport port-security maximum 1",
    purpose="Restricts the number/identity of MAC addresses allowed on a switchport, mitigating MAC-flooding and rogue-device attacks.",
    sample_output="(no output; verify with 'show port-security interface <name>')",
    notes="Port-security is an L2 switching feature; not applicable on IOS-XR (used on pure routing platforms).",
    config_mode="Yes",
    related=["show_mac_address_table"],
))

COMMANDS.append(rec(
    "dhcp_snooping", "Configure DHCP Snooping", "Security",
    ["ip dhcp snooping", "دی اچ سی پی اسنوپینگ", "کانفیگ dhcp snooping"],
    ios="ip dhcp snooping\nip dhcp snooping vlan <vlan-id>",
    ios_xe="ip dhcp snooping\nip dhcp snooping vlan <vlan-id>",
    ios_xr=NA,
    nx_os="feature dhcp\nip dhcp snooping\nip dhcp snooping vlan <vlan-id>",
    syntax="ip dhcp snooping / ip dhcp snooping vlan <vlan-id>",
    example="ip dhcp snooping\nip dhcp snooping vlan 10",
    purpose="Enables DHCP Snooping, a Layer 2 security feature that filters untrusted DHCP messages and builds a binding table to prevent rogue DHCP servers.",
    sample_output="(no output; verify with 'show ip dhcp snooping')",
    notes="NX-OS requires 'feature dhcp' before DHCP snooping commands become available.",
    config_mode="Yes",
    related=["dhcp_show_binding"],
))

COMMANDS.append(rec(
    "cpu_utilization", "Show CPU Utilization", "Security",
    ["show processes cpu", "cpu usage", "مصرف cpu"],
    ios="show processes cpu sorted", ios_xe="show processes cpu sorted",
    ios_xr="show processes cpu", nx_os="show processes cpu sort",
    syntax="show processes cpu [sorted|sort]",
    example="show processes cpu sorted",
    purpose="Displays per-process CPU utilization — the first command to run when a device becomes sluggish or drops packets under load.",
    sample_output="CPU utilization for five seconds: 23%/5%; one minute: 20%; five minutes: 18%\n PID Runtime(ms) Invoked  uSecs  5Sec  1Min  5Min TTY Process",
    notes="NX-OS spells the sort keyword without the trailing 'ed': 'sort' instead of 'sorted'.",
    related=["memory_utilization"],
))

COMMANDS.append(rec(
    "memory_utilization", "Show Memory Utilization", "Security",
    ["show processes memory", "memory usage", "مصرف حافظه"],
    ios="show processes memory sorted", ios_xe="show processes memory sorted",
    ios_xr="show processes memory", nx_os="show processes memory sort",
    syntax="show processes memory [sorted|sort]",
    example="show processes memory sorted",
    purpose="Displays per-process memory allocation — useful for diagnosing memory leaks or exhaustion.",
    sample_output="Total: 4294967296, Used: 1073741824, Free: 3221225472\n PID  TTY  Allocated  Freed  Holding  Getbufs  Retbufs  Process",
    notes="Compare 'Holding' across polls over time to spot a leaking process.",
    related=["cpu_utilization"],
))

# ---------------------------------------------------------------- L2 Switching / STP family / VLAN / EtherChannel / LACP / UDLD / CDP / LLDP
COMMANDS.append(rec(
    "show_mac_address_table", "Show MAC Address Table", "L2 Switching",
    ["show mac address-table", "mac table", "جدول مک", "نمایش جدول مک"],
    ios="show mac address-table", ios_xe="show mac address-table",
    ios_xr="show l2vpn forwarding mac-address", nx_os="show mac address-table",
    syntax="show mac address-table [dynamic|static] [vlan <id>] [interface <name>]",
    example="show mac address-table vlan 10",
    purpose="Displays the L2 forwarding table mapping learned MAC addresses to VLAN and switchport.",
    sample_output="Vlan    Mac Address       Type        Ports\n10      0011.2233.44aa    DYNAMIC     Gi1/0/1",
    notes="IOS-XR routers are not L2 switches by default — the closest equivalent is the L2VPN forwarding MAC table, only relevant if L2VPN/bridging is configured.",
    related=["show_vlan_brief"],
))

COMMANDS.append(rec(
    "show_vlan_brief", "Show VLAN Brief", "VLAN",
    ["show vlan brief", "vlan list", "لیست vlan"],
    ios="show vlan brief", ios_xe="show vlan brief", ios_xr=NA,
    nx_os="show vlan brief",
    syntax="show vlan brief",
    example="show vlan brief",
    purpose="Lists all configured VLANs, their state, and assigned ports.",
    sample_output="VLAN Name          Status    Ports\n10   USERS         active    Gi1/0/1, Gi1/0/2",
    notes="Not applicable to IOS-XR (pure L3 routing platform, no native VLAN database).",
    related=["show_mac_address_table"],
))

COMMANDS.append(rec(
    "vlan_config", "Create a VLAN", "VLAN",
    ["vlan database config", "ساخت vlan", "کانفیگ vlan"],
    ios="vlan <id>\n name <name>",
    ios_xe="vlan <id>\n name <name>",
    ios_xr=NA,
    nx_os="vlan <id>\n name <name>",
    syntax="vlan <vlan-id> / name <vlan-name>",
    example="vlan 10\n name USERS",
    purpose="Creates a VLAN and assigns it a descriptive name in the VLAN database.",
    sample_output="(no output; verify with 'show vlan brief')",
    notes="Not applicable on IOS-XR.",
    config_mode="Yes",
    related=["show_vlan_brief"],
))

COMMANDS.append(rec(
    "stp_status", "Show Spanning-Tree Status", "STP",
    ["show spanning-tree", "stp status", "وضعیت stp"],
    ios="show spanning-tree", ios_xe="show spanning-tree",
    ios_xr=NA, nx_os="show spanning-tree",
    syntax="show spanning-tree [vlan <id>]",
    example="show spanning-tree vlan 10",
    purpose="Displays Spanning Tree Protocol topology: root bridge election, port roles (Root/Designated/Blocking) and states.",
    sample_output="VLAN0010\n  Spanning tree enabled protocol rstp\n  Root ID    Priority    32778",
    notes="Not applicable on IOS-XR routers, which don't run classic STP.",
    related=["show_vlan_brief"],
))

COMMANDS.append(rec(
    "rstp_config", "Enable Rapid-PVST (RSTP)", "RSTP",
    ["spanning-tree mode rapid-pvst", "فعال کردن rstp"],
    ios="spanning-tree mode rapid-pvst", ios_xe="spanning-tree mode rapid-pvst",
    ios_xr=NA, nx_os="spanning-tree mode rapid-pvst",
    syntax="spanning-tree mode rapid-pvst",
    example="spanning-tree mode rapid-pvst",
    purpose="Switches the spanning-tree algorithm from legacy 802.1D STP to Rapid-PVST+ (802.1w per-VLAN), which converges in seconds instead of ~50s.",
    sample_output="(no output; verify with 'show spanning-tree summary')",
    notes="Rapid-PVST+ is Cisco's per-VLAN implementation of 802.1w.",
    config_mode="Yes",
    related=["stp_status"],
))

COMMANDS.append(rec(
    "mst_config", "Configure MST (Multiple Spanning Tree)", "MST",
    ["spanning-tree mst configuration", "کانفیگ mst"],
    ios="spanning-tree mst configuration\n name <region-name>\n revision <n>\n instance 1 vlan 1-100",
    ios_xe="spanning-tree mst configuration\n name <region-name>\n revision <n>\n instance 1 vlan 1-100",
    ios_xr=NA,
    nx_os="spanning-tree mst configuration\n name <region-name>\n revision <n>\n instance 1 vlan 1-100",
    syntax="spanning-tree mst configuration / name <region> / revision <n> / instance <id> vlan <range>",
    example="spanning-tree mst configuration\n name REGION1\n revision 1\n instance 1 vlan 1-100",
    purpose="Configures Multiple Spanning Tree (802.1s), mapping VLAN ranges to STP instances to reduce the number of STP topologies computed.",
    sample_output="(no output; verify with 'show spanning-tree mst configuration')",
    notes="All switches in the same MST region must have an identical name/revision/VLAN-to-instance mapping or they form separate regions.",
    config_mode="Yes",
    related=["stp_status"],
))

COMMANDS.append(rec(
    "etherchannel_summary", "Show EtherChannel Summary", "EtherChannel",
    ["show etherchannel summary", "port-channel summary", "خلاصه port channel"],
    ios="show etherchannel summary", ios_xe="show etherchannel summary",
    ios_xr="show bundle", nx_os="show port-channel summary",
    syntax="show etherchannel summary",
    example="show etherchannel summary",
    purpose="Displays EtherChannel/port-channel bundle status and member-port state (Bndl/Susp/Down/etc).",
    sample_output="Group  Port-channel  Protocol   Ports\n1      Po1(SU)       LACP       Gi0/1(P) Gi0/2(P)",
    notes="NX-OS uses 'show port-channel summary'; IOS-XR uses 'show bundle' (its bundle-interface abstraction).",
    related=["lacp_neighbor"],
))

COMMANDS.append(rec(
    "etherchannel_config", "Configure an EtherChannel (LACP)", "EtherChannel",
    ["port-channel config lacp", "کانفیگ port channel", "ساخت port channel"],
    ios="interface range Gi0/1 - 2\n channel-group 1 mode active",
    ios_xe="interface range Gi0/1 - 2\n channel-group 1 mode active",
    ios_xr="interface Bundle-Ether1\ninterface Gi0/0/0/1\n bundle id 1 mode active",
    nx_os="interface eth1/1-2\n channel-group 1 mode active",
    syntax="interface <range> / channel-group <n> mode {active|passive|on}",
    example="interface range GigabitEthernet0/1 - 2\n channel-group 1 mode active",
    purpose="Bundles multiple physical links into a single logical LACP EtherChannel for redundancy and increased bandwidth.",
    sample_output="(no output; verify with 'show etherchannel summary')",
    notes="IOS-XR uses the 'Bundle-Ether' interface abstraction and 'bundle id' under each member interface rather than 'channel-group'.",
    config_mode="Yes",
    related=["etherchannel_summary"],
))

COMMANDS.append(rec(
    "lacp_neighbor", "Show LACP Neighbor", "LACP",
    ["show lacp neighbor", "lacp neighbor", "همسایه lacp"],
    ios="show lacp neighbor", ios_xe="show lacp neighbor",
    ios_xr="show lacp", nx_os="show lacp neighbor",
    syntax="show lacp neighbor [<port-channel-id>]",
    example="show lacp neighbor",
    purpose="Displays LACP partner (neighbor) system ID, port priority and state flags for each bundled link.",
    sample_output="Flags:  S - Device is requesting Slow LACPDUs\nChannel group 1 neighbors\n  Port     Flags   State   LACP port Priority",
    notes="IOS-XR's bundle CLI consolidates this info under 'show lacp'.",
    related=["etherchannel_summary"],
))

COMMANDS.append(rec(
    "udld_status", "Show UDLD Status", "UDLD",
    ["show udld", "udld status", "وضعیت udld"],
    ios="show udld", ios_xe="show udld", ios_xr=NA, nx_os="show udld",
    syntax="show udld [<interface>]",
    example="show udld GigabitEthernet0/1",
    purpose="Displays UDLD (Unidirectional Link Detection) status — detects and disables links where traffic flows in only one direction (e.g. broken fiber pair).",
    sample_output="Interface Gi0/1\n---\nPort enable administrative configuration setting: Enabled\nCurrent bidirectional state: Bidirectional",
    notes="UDLD is a Cisco proprietary L2 feature typically used on switching platforms, not on IOS-XR routers.",
    related=["cdp_neighbor"],
))

COMMANDS.append(rec(
    "cdp_neighbor", "Show CDP Neighbors", "CDP",
    ["show cdp neighbors", "cdp neighbor", "همسایه cdp"],
    ios="show cdp neighbors detail", ios_xe="show cdp neighbors detail",
    ios_xr="show cdp neighbors detail", nx_os="show cdp neighbors detail",
    syntax="show cdp neighbors [detail]",
    example="show cdp neighbors detail",
    purpose="Displays directly connected Cisco devices discovered via CDP (Cisco Discovery Protocol) — device ID, platform, and port.",
    sample_output="Device ID: SW2\n  Platform: cisco WS-C3850-24T, Capabilities: Switch IGMP\n  Interface: GigabitEthernet0/1, Port ID: GigabitEthernet1/0/1",
    notes="Consistent syntax across all four platforms.",
    related=["lldp_neighbor"],
))

COMMANDS.append(rec(
    "lldp_neighbor", "Show LLDP Neighbors", "LLDP",
    ["show lldp neighbors", "lldp neighbor", "همسایه lldp"],
    ios="show lldp neighbors detail", ios_xe="show lldp neighbors detail",
    ios_xr="show lldp neighbors detail", nx_os="show lldp neighbors detail",
    syntax="show lldp neighbors [detail]",
    example="show lldp neighbors detail",
    purpose="Displays directly connected devices discovered via LLDP (vendor-neutral equivalent of CDP), useful in multi-vendor environments.",
    sample_output="Chassis id: 0011.2233.4499\nPort id: Gi1/0/1\nSystem Name: SW2",
    notes="Prefer LLDP over CDP when peering with non-Cisco equipment.",
    related=["cdp_neighbor"],
))

# ---------------------------------------------------------------- DHCP / DNS / NTP / Syslog / IP SLA / PBR / Multicast extra
COMMANDS.append(rec(
    "dhcp_show_binding", "Show DHCP Bindings", "DHCP",
    ["show ip dhcp binding", "dhcp binding", "بایندینگ dhcp"],
    ios="show ip dhcp binding", ios_xe="show ip dhcp binding",
    ios_xr="show dhcp ipv4 binding", nx_os="show ip dhcp binding",
    syntax="show ip dhcp binding [<ip-address>]",
    example="show ip dhcp binding",
    purpose="Displays active DHCP lease bindings when the router/switch is acting as a DHCP server.",
    sample_output="IP address       Client-ID/         Lease expiration        Type\n10.0.0.50         0100.1122.3344      Jul 20 2026 08:00 AM  Automatic",
    notes="IOS-XR requires the address-family: 'show dhcp ipv4 binding'.",
    related=["dhcp_pool_config"],
))

COMMANDS.append(rec(
    "dhcp_pool_config", "Configure a DHCP Pool", "DHCP",
    ["ip dhcp pool", "کانفیگ dhcp pool", "ساخت dhcp pool"],
    ios="ip dhcp pool <name>\n network <network> <mask>\n default-router <gw>\n dns-server <dns>",
    ios_xe="ip dhcp pool <name>\n network <network> <mask>\n default-router <gw>\n dns-server <dns>",
    ios_xr="dhcp ipv4\n pool <name>\n  network <network>/<len>\n  dns-server <dns>\n  default-router <gw>",
    nx_os="feature dhcp\nip dhcp pool <name>\n network <network> <mask>",
    syntax="ip dhcp pool <name> / network <network> <mask> / default-router <gw>",
    example="ip dhcp pool USERS\n network 10.0.0.0 255.255.255.0\n default-router 10.0.0.1\n dns-server 8.8.8.8",
    purpose="Configures the router as a local DHCP server for a subnet, defining the address pool, default gateway and DNS servers to hand out.",
    sample_output="(no output; verify with 'show ip dhcp binding')",
    notes="NX-OS requires 'feature dhcp' first; IOS-XR nests the pool inside a 'dhcp ipv4' top-level block.",
    config_mode="Yes",
    related=["dhcp_show_binding"],
))

COMMANDS.append(rec(
    "dns_config", "Configure DNS Resolution", "DNS",
    ["ip name-server", "کانفیگ dns", "افزودن dns سرور"],
    ios="ip domain lookup\nip name-server <dns-ip>",
    ios_xe="ip domain lookup\nip name-server <dns-ip>",
    ios_xr="domain lookup\ndomain name-server <dns-ip>",
    nx_os="ip domain-lookup\nip name-server <dns-ip>",
    syntax="ip name-server <dns-ip> [<dns-ip2> ...]",
    example="ip name-server 8.8.8.8 1.1.1.1",
    purpose="Configures upstream DNS servers the device itself uses for hostname resolution (e.g. for ping/traceroute by name).",
    sample_output="(no output; verify with 'show hosts' or 'show running-config | include name-server')",
    notes="IOS-XR spells the enable keyword 'domain lookup' (no 'ip' prefix).",
    config_mode="Yes",
    related=["show_hosts"],
))

COMMANDS.append(rec(
    "show_hosts", "Show DNS Host Cache", "DNS",
    ["show hosts", "dns cache", "کش dns"],
    ios="show hosts", ios_xe="show hosts", ios_xr="show hosts",
    nx_os="show hosts",
    syntax="show hosts",
    example="show hosts",
    purpose="Displays the local hostname-to-IP cache, including static host entries and cached DNS lookups.",
    sample_output="Host              Flags      Age Type   Address(es)\nrouter2.local     (perm, OK) 0   IP     10.0.0.2",
    notes="Consistent syntax on all four platforms.",
    related=["dns_config"],
))

COMMANDS.append(rec(
    "ntp_config", "Configure NTP", "NTP",
    ["ntp server", "کانفیگ ntp", "افزودن ntp سرور"],
    ios="ntp server <ip>", ios_xe="ntp server <ip>",
    ios_xr="ntp server <ip>", nx_os="ntp server <ip> use-vrf default",
    syntax="ntp server <ip-address> [prefer]",
    example="ntp server 132.163.97.1 prefer",
    purpose="Configures an upstream NTP time source to synchronize the device clock — critical for accurate logging/troubleshooting correlation.",
    sample_output="(no output; verify with 'show ntp status' / 'show ntp associations')",
    notes="NX-OS requires an explicit VRF context for NTP: 'use-vrf default' (or a named VRF) if not using the management VRF.",
    config_mode="Yes",
    related=["ntp_status"],
))

COMMANDS.append(rec(
    "ntp_status", "Show NTP Status", "NTP",
    ["show ntp status", "ntp status", "وضعیت ntp"],
    ios="show ntp status", ios_xe="show ntp status",
    ios_xr="show ntp status", nx_os="show ntp peer-status",
    syntax="show ntp status",
    example="show ntp status",
    purpose="Displays whether the local clock is synchronized, the reference clock, stratum and offset.",
    sample_output="Clock is synchronized, stratum 3, reference is 132.163.97.1\nnominal freq is 250.0000 Hz, actual freq is 249.9997 Hz",
    notes="NX-OS uses 'show ntp peer-status' rather than 'show ntp status'.",
    related=["ntp_config"],
))

COMMANDS.append(rec(
    "ip_sla_config", "Configure IP SLA", "IP SLA",
    ["ip sla monitor", "کانفیگ ip sla", "تست ping دوره ای"],
    ios="ip sla 1\n icmp-echo <dest-ip>\n frequency 30\nip sla schedule 1 life forever start-time now",
    ios_xe="ip sla 1\n icmp-echo <dest-ip>\n frequency 30\nip sla schedule 1 life forever start-time now",
    ios_xr="ipsla\n operation 1\n  type icmp echo\n   destination address <dest-ip>",
    nx_os="feature sla sender\nip sla 1\n icmp-echo <dest-ip>\n frequency 30",
    syntax="ip sla <id> / icmp-echo <destination-ip> / frequency <seconds>",
    example="ip sla 1\n icmp-echo 10.0.0.9\n frequency 30\nip sla schedule 1 life forever start-time now",
    purpose="Configures IP SLA to continuously measure reachability/latency/jitter to a target, often paired with tracking objects for failover.",
    sample_output="(no output; verify with 'show ip sla statistics')",
    notes="NX-OS requires 'feature sla sender'; IOS-XR uses a distinctly different 'ipsla' operation syntax.",
    config_mode="Yes",
    related=["ip_sla_show"],
))

COMMANDS.append(rec(
    "ip_sla_show", "Show IP SLA Statistics", "IP SLA",
    ["show ip sla statistics", "sla stats", "آمار sla"],
    ios="show ip sla statistics", ios_xe="show ip sla statistics",
    ios_xr="show ipsla statistics", nx_os="show ip sla statistics",
    syntax="show ip sla statistics [<id>]",
    example="show ip sla statistics 1",
    purpose="Displays the latest round-trip-time/reachability results recorded by an IP SLA operation.",
    sample_output="Round Trip Time (RTT) for Index 1\n        Latest RTT: 2 ms\nReturn Code: OK",
    notes="IOS-XR spells the command without a space: 'show ipsla statistics'.",
    related=["ip_sla_config"],
))

COMMANDS.append(rec(
    "pbr_config", "Configure Policy-Based Routing (PBR)", "Policy Based Routing",
    ["route-map pbr", "کانفیگ pbr", "مسیریابی مبتنی بر پالیسی"],
    ios="route-map PBR permit 10\n match ip address 101\n set ip next-hop <ip>\ninterface <name>\n ip policy route-map PBR",
    ios_xe="route-map PBR permit 10\n match ip address 101\n set ip next-hop <ip>\ninterface <name>\n ip policy route-map PBR",
    ios_xr="route-policy PBR\n if destination in (10.0.0.0/24) then\n  set next-hop <ip>\n endif\ninterface <name>\n ipv4 policy route-map PBR",
    nx_os="route-map PBR permit 10\n match ip address 101\n set ip next-hop <ip>\ninterface <name>\n ip policy route-map PBR",
    syntax="route-map <name> permit <seq> / match ip address <acl> / set ip next-hop <ip> then apply under interface with 'ip policy route-map'",
    example="route-map PBR permit 10\n match ip address 101\n set ip next-hop 10.0.0.9\ninterface GigabitEthernet0/1\n ip policy route-map PBR",
    purpose="Forces traffic matching specific criteria to take a different next-hop/path than the routing table would normally select.",
    sample_output="(no output; verify with 'show route-map' and 'show ip policy')",
    notes="IOS-XR uses RPL (route-policy) with an if/then/endif syntax rather than classic route-maps.",
    config_mode="Yes",
    related=["show_access_lists"],
))

COMMANDS.append(rec(
    "show_ip_policy", "Show IP Policy (PBR) Bindings", "Policy Based Routing",
    ["show ip policy", "pbr status", "وضعیت pbr"],
    ios="show ip policy", ios_xe="show ip policy",
    ios_xr="show route-policy", nx_os="show ip policy",
    syntax="show ip policy",
    example="show ip policy",
    purpose="Lists which interfaces have a PBR route-map applied.",
    sample_output="Interface      Route map\nGi0/1          PBR",
    notes="IOS-XR equivalent is 'show route-policy' which lists RPL policy definitions rather than interface bindings directly.",
    related=["pbr_config"],
))

# ---------------------------------------------------------------- Extra Multicast / misc rounding out to 100+
COMMANDS.append(rec(
    "pim_rp_mapping", "Show PIM RP Mapping", "Multicast",
    ["show ip pim rp mapping", "rp mapping", "نگاشت rp"],
    ios="show ip pim rp mapping", ios_xe="show ip pim rp mapping",
    ios_xr="show pim rp mapping", nx_os="show ip pim rp mapping",
    syntax="show ip pim rp mapping",
    example="show ip pim rp mapping",
    purpose="Displays the Rendezvous Point (RP) to multicast group mapping, learned via static config, Auto-RP, or BSR.",
    sample_output="PIM Group-to-RP Mappings\nGroup(s) 224.0.0.0/4\n  RP 10.0.0.9 (?), v2\n    Info source: Static",
    notes="Critical command when multicast traffic isn't forwarding — a missing/incorrect RP mapping is the #1 cause.",
    related=["pim_neighbor", "pim_mroute"],
))

COMMANDS.append(rec(
    "igmp_snooping", "Show IGMP Snooping", "Multicast",
    ["show ip igmp snooping", "igmp snooping", "اسنوپینگ igmp"],
    ios="show ip igmp snooping", ios_xe="show ip igmp snooping",
    ios_xr=NA, nx_os="show ip igmp snooping",
    syntax="show ip igmp snooping [vlan <id>]",
    example="show ip igmp snooping vlan 10",
    purpose="Displays IGMP snooping state per VLAN — an L2 optimization that prunes multicast flooding to only ports with interested receivers.",
    sample_output="Vlan  IGMP snooping  Querier    v1 v2 v3   Report suppression  Immediate Leave\n10    Enabled        Non-Querier ---- Yes ----   Enabled              Disabled",
    notes="This is an L2 switching feature; not present on IOS-XR routers.",
    related=["igmp_groups"],
))

COMMANDS.append(rec(
    "show_version", "Show Version", "Interfaces",
    ["show version", "sh ver", "ورژن دستگاه", "مشخصات دستگاه"],
    ios="show version", ios_xe="show version", ios_xr="show version",
    nx_os="show version",
    syntax="show version",
    example="show version",
    purpose="Displays hardware model, software version/train, uptime, and installed feature licenses — the standard first command on any device.",
    sample_output="Cisco IOS XE Software, Version 17.09.04a\nROM: IOS-XE ROMMON\nUptime is 45 days, 3 hours, 12 minutes",
    notes="Consistent core syntax across all platforms, though output formatting differs significantly per OS family.",
    related=["show_running_config"],
))

COMMANDS.append(rec(
    "show_running_config", "Show Running Configuration", "Interfaces",
    ["show running-config", "sh run", "کانفیگ فعلی", "نمایش running config"],
    ios="show running-config", ios_xe="show running-config",
    ios_xr="show running-config", nx_os="show running-config",
    syntax="show running-config [<section-keyword>]",
    example="show running-config interface GigabitEthernet0/1",
    purpose="Displays the active configuration currently running in memory (as opposed to the saved startup-config).",
    sample_output="Building configuration...\n!\nhostname ROUTER1\n!\ninterface GigabitEthernet0/1",
    notes="On IOS-XR, running-config is generated from the committed configuration database, not edited directly in real time.",
    related=["show_version"],
))

COMMANDS.append(rec(
    "save_config", "Save Running Configuration", "Interfaces",
    ["write memory", "copy running-config startup-config", "ذخیره کانفیگ", "سیو کردن کانفیگ"],
    ios="write memory", ios_xe="write memory", ios_xr="commit",
    nx_os="copy running-config startup-config",
    syntax="write memory  (or)  copy running-config startup-config",
    example="write memory",
    purpose="Persists the running configuration to non-volatile memory so it survives a reload.",
    sample_output="Building configuration...\n[OK]",
    notes="IOS-XR uses a transactional model: configuration changes must be explicitly 'commit'ted, and are persistent once committed (no separate save step needed).",
    config_mode="No (privileged EXEC action command; IOS-XR: config mode 'commit')",
    related=["show_running_config"],
))

COMMANDS.append(rec(
    "reload_device", "Reload the Device", "Interfaces",
    ["reload", "ریست دستگاه", "ریلود کردن روتر"],
    ios="reload", ios_xe="reload", ios_xr="reload",
    nx_os="reload",
    syntax="reload [in <hh:mm> | at <hh:mm>] [reason <text>]",
    example="reload in 30",
    purpose="Reboots the device, optionally scheduled for a later time — commonly used with a safety timer during risky changes.",
    sample_output="System configuration has been modified. Save? [yes/no]:\nProceed with reload? [confirm]",
    notes="Always schedule a 'reload in <n>' safety-net before making risky remote changes, and cancel it with 'reload cancel' once you confirm connectivity.",
    config_mode="No (privileged EXEC action command)",
    related=["save_config"],
))

COMMANDS.append(rec(
    "ping_cmd", "Ping", "IPv4",
    ["ping", "پینگ", "تست پینگ"],
    ios="ping <ip>", ios_xe="ping <ip>", ios_xr="ping <ip>",
    nx_os="ping <ip>",
    syntax="ping [vrf <name>] <destination> [source <ip>] [repeat <n>] [size <bytes>]",
    example="ping 8.8.8.8 source GigabitEthernet0/1 repeat 100",
    purpose="Sends ICMP echo requests to test basic IP reachability and measure round-trip time.",
    sample_output="Sending 5, 100-byte ICMP Echos to 8.8.8.8, timeout is 2 seconds:\n!!!!!\nSuccess rate is 100 percent (5/5), round-trip min/avg/max = 1/2/4 ms",
    notes="Extended ping (typing 'ping' with no arguments) lets you set source interface, VRF, packet size and repeat count interactively.",
    config_mode="No",
    related=["traceroute_cmd"],
))

COMMANDS.append(rec(
    "traceroute_cmd", "Traceroute", "IPv4",
    ["traceroute", "tracert", "ترسیم مسیر", "تریس روت"],
    ios="traceroute <ip>", ios_xe="traceroute <ip>", ios_xr="traceroute <ip>",
    nx_os="traceroute <ip>",
    syntax="traceroute [vrf <name>] <destination> [source <ip>]",
    example="traceroute 8.8.8.8 source GigabitEthernet0/1",
    purpose="Maps the hop-by-hop path packets take to a destination using incrementing TTL and ICMP time-exceeded replies.",
    sample_output="Tracing the route to 8.8.8.8\n  1 192.0.2.1 1 msec 0 msec 1 msec\n  2 198.51.100.1 5 msec 4 msec 5 msec",
    notes="A hop showing '* * *' can indicate an ICMP rate-limit/filter rather than an actual outage — verify with other tools before concluding a link is down.",
    config_mode="No",
    related=["ping_cmd"],
))

COMMANDS.append(rec(
    "show_processes", "Show Processes", "Debug",
    ["show processes", "لیست پروسس ها"],
    ios="show processes", ios_xe="show processes", ios_xr="show processes",
    nx_os="show processes",
    syntax="show processes",
    example="show processes",
    purpose="Lists all running processes on the device with their state, CPU and runtime — a broader view than 'show processes cpu'.",
    sample_output="PID QTy  PC  State   Runtime(ms)  Invoked  uSecs  Stacks TTY Process\n1   Lwe 1010203C Waiting  0  1  0  6000/6000 0  Chunk Manager",
    notes="Useful for confirming whether a specific protocol process (e.g. 'BGP Router', 'OSPF Router') is running at all.",
    related=["cpu_utilization"],
))

COMMANDS.append(rec(
    "show_inventory", "Show Hardware Inventory", "Interfaces",
    ["show inventory", "اجزای سخت افزاری", "اینونتوری"],
    ios="show inventory", ios_xe="show inventory", ios_xr="show inventory",
    nx_os="show inventory",
    syntax="show inventory",
    example="show inventory",
    purpose="Lists all hardware components (chassis, line cards, PSUs, SFPs) with PIDs, serial numbers and descriptions — commonly needed for RMA/warranty requests.",
    sample_output="NAME: \"Chassis\", DESCR: \"Cisco ASR1001-X Chassis\"\nPID: ASR1001-X, VID: V07, SN: FXS1234A1BC",
    notes="Always include the full 'show inventory' output when opening a Cisco TAC hardware case.",
    related=["show_version"],
))

COMMANDS.append(rec(
    "show_env", "Show Environment (Power/Temp/Fan)", "Interfaces",
    ["show environment", "دما و پاور دستگاه", "وضعیت فن و برق"],
    ios="show environment all", ios_xe="show environment all",
    ios_xr="show environment", nx_os="show environment",
    syntax="show environment [all]",
    example="show environment all",
    purpose="Displays chassis environmental sensors: power supply status, fan status, and temperature readings.",
    sample_output="SYSTEM TEMPERATURES\nSensor      Location  Reading(°C) Status\nInlet       Chassis   28          OK",
    notes="A common first check for random reloads that turn out to be thermal shutdowns or a failed power supply.",
    related=["show_inventory"],
))

print(f"Total commands defined: {len(COMMANDS)}")
assert len(COMMANDS) >= 100, "Need at least 100 commands per spec"

# ---- Write commands.json -------------------------------------------------
with open(HERE / "commands.json", "w", encoding="utf-8") as f:
    json.dump({"commands": COMMANDS}, f, ensure_ascii=False, indent=2)

# ---- Write categories.json -------------------------------------------------
with open(HERE / "categories.json", "w", encoding="utf-8") as f:
    json.dump({"categories": CATEGORIES}, f, ensure_ascii=False, indent=2)

# ---- Write aliases.json (flat alias -> command id index, for reference/debug)
alias_index = {}
for c in COMMANDS:
    for a in c["aliases"]:
        alias_index.setdefault(a.lower(), []).append(c["id"])

with open(HERE / "aliases.json", "w", encoding="utf-8") as f:
    json.dump({"aliases": alias_index}, f, ensure_ascii=False, indent=2)

print("Wrote commands.json, categories.json, aliases.json")
