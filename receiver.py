###############################################################################
# receiver.py
# Name: Debanik Purkayastha
# JHED ID: dpurkay1
###############################################################################

import sys
import socket
import time
import random

from util import *

def receiver(receiver_port, window_size):
    """TODO: Listen on socket and print received message to sys.stdout"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('127.0.0.1', receiver_port))

    recv_pkts = []
    expected_ack = 0
    acked_pkts = set()
    connection_initiated = 0
    connection_end = 1
    
    while True:
        # receive packet
        pkt, address = s.recvfrom(2048)
        pkt_header = PacketHeader(pkt[:16])
        msg = pkt[16:16+pkt_header.length]

        # verify checksum
        pkt_checksum = pkt_header.checksum
        pkt_header.checksum = 0
        computed_checksum = compute_checksum(pkt_header / msg)
        if pkt_checksum != computed_checksum:
            print "checksums not match"
            continue

        # print payload
        if pkt_header.type == 0 and connection_initiated == 0: # START PACKET
            ack_pkt_header = PacketHeader(type=3, seq_num=pkt_header.seq_num, length=0)
            ack_pkt_header.checksum = compute_checksum(ack_pkt_header)
            ack_pkt = ack_pkt_header
            s.sendto(str(ack_pkt), ('127.0.0.1', address[1]))
            connection_initiated = 1
            connection_end = 0

        elif pkt_header.type == 2 and connection_initiated == 1: # DATA PACKET
            expected_ack = pkt_header.seq_num
            if (pkt_header.seq_num < expected_ack + window_size):
                if (pkt_header.seq_num not in acked_pkts):
                    recv_pkts.append((pkt_header, pkt))
                recv_pkts.sort(key=lambda x: x[0].seq_num, reverse=False)
                ack_pkt_header = PacketHeader(type=3, seq_num=pkt_header.seq_num, length=0)
                ack_pkt_header.checksum = compute_checksum(ack_pkt_header)
                ack_pkt = ack_pkt_header
                acked_pkts.add(ack_pkt_header.seq_num)
                s.sendto(str(ack_pkt), ('127.0.0.1', address[1]))

        elif pkt_header.type == 3 and connection_initiated == 1: # END PACKET
            connection_initiated = 0
            connection_end = 1
            break

    for pkt_hdr in recv_pkts:
        pkt = pkt_hdr[1]
        pkt_header = pkt_hdr[0]
        msg = pkt[16:16+pkt_header.length]  
        sys.stdout.write(msg)



def main():
    """Parse command-line argument and call receiver function """
    if len(sys.argv) != 3:
        sys.exit("Usage: python receiver.py [Receiver Port] [Window Size]")
    receiver_port = int(sys.argv[1])
    window_size = int(sys.argv[2])
    receiver(receiver_port, window_size)

if __name__ == "__main__":
    main()
