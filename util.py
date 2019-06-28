import binascii

from scapy.all import Packet
from scapy.all import IntField
from scapy.all import SignedIntField

class PacketHeader(Packet):
    name = "PacketHeader"
    fields_desc = [
        IntField("type", 0),
        IntField("seq_num", 0),
        IntField("length", 0),
        SignedIntField("checksum", 0),
    ]

def compute_checksum(pkt):
    return binascii.crc32(str(pkt))