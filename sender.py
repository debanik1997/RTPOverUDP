###############################################################################
# sender.py
# Name: Debanik Purkayastha
# JHED ID: dpurkay1
###############################################################################

import sys
import socket
import random
import time
import threading

# from threading import Thread
from util import *

def sender(receiver_ip, receiver_port, window_size):
    """TODO: Open socket and send message from sys.stdin"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setblocking(False)

    # INITIATE CONNECTION   
    connection_established = 0 
    while (connection_established == 0):
        try:
            seq_num = random.randint(1, 100000)
            start_pkt_header = PacketHeader(type=0, seq_num=seq_num, length=0)
            start_pkt_header.checksum = compute_checksum(start_pkt_header)
            start_pkt = start_pkt_header
            s.sendto(str(start_pkt), (receiver_ip, receiver_port)) 
            pkt, address = s.recvfrom(2048)
            pkt_header = PacketHeader(pkt[:16])
            if (pkt_header.type == 3 and pkt_header.seq_num == seq_num):
                connection_established = 1
        except:
            pass

    # SEND DATA
    # CREATE PACKETS
    pkts = []
    pkt_headers = []
    current_seq_num = 0
    while(1):
        data = sys.stdin.read(1472 - 248)
        if(data == ''):
            break
        pkt_header = PacketHeader(type=2, seq_num=current_seq_num, length=len(data))
        pkt_header.checksum = compute_checksum(pkt_header / data)
        pkt_headers.append(pkt_header)
        pkt = pkt_header / data
        pkts.append(pkt)
        current_seq_num = current_seq_num + 1
    total_packets = len(pkts)

    # START SENDING
    window_start = 0
    window_end = window_size - 1
    in_flight = -1
    acked_pkts = []
    in_flight_pkts = set([])
    while(len(acked_pkts) != total_packets): # SEND CORRECT PACKETS FROM WINDOW
        for i in range(window_size):
            pkt_num = i + window_start
            if (not (pkt_num in acked_pkts) and not (pkt_num in in_flight_pkts) and pkt_num < total_packets):
                s.sendto(str(pkts[pkt_num]), (receiver_ip, receiver_port))
                in_flight_pkts.add(pkt_num)

        # INITIALIZE TIMERS
        pkt_start_times = {}
        for i in range(window_size):
            if (not (i + window_start) in pkt_start_times.keys()):
                pkt_start_times[i+window_start] = time.time()
        did_window_move = 0
        retransmit_necessary = 0

        while (1): # LISTEN FOR ACKS
            time_elapsed = {}
            for i in range(window_size):
                time_elapsed[i + window_start] = time.time() - pkt_start_times[i+window_start]

            expired_timers = {}
            for i in range(window_size):
                if (time_elapsed[i+window_start] >= 1 and not (i+window_start) in acked_pkts):
                    expired_timers[i+window_start] = 1

            # CHECK FOR RETRANSMISSION
            if (len(expired_timers) != 0):
                retransmit_necessary = 1
                break

            try:                
                recv_pkt, address = s.recvfrom(2048)
                recv_pkt_header = PacketHeader(recv_pkt[:16])
                recv_pkt_checksum = recv_pkt_header.checksum
                recv_pkt_header.checksum = 0
                computed_checksum = compute_checksum(recv_pkt_header)
                if recv_pkt_checksum != computed_checksum:
                    print "checksums not match"
                    continue

                recv = recv_pkt_header.seq_num
                if not (recv in acked_pkts):
                    acked_pkts.append(recv)
                    in_flight_pkts.remove(recv)
                    acked_pkts.sort()
                m = 0
                for p in acked_pkts:
                    if p == m:
                        m+=1
                    else:
                        break

                # WINDOW MOVED
                if (m > window_start):
                    for t in pkt_start_times.keys():
                        if (t < m):
                            del pkt_start_times[t]

                    window_start = m
                    window_end = m + window_size - 1

                    for i in range(window_size):
                        if (not (i + window_start) in pkt_start_times.keys()):
                            pkt_start_times[i+window_start] = time.time()
                    break
            except:
                pass

        # RETRANSMIT
        if (retransmit_necessary):
            for i in expired_timers.keys():
                print("retransmit_necessary", i)
                if (i < total_packets):
                    in_flight_pkts.remove(i)


    # Send END
    seq_num = random.randint(1, 100000)
    end_pkt_header = PacketHeader(type=3, seq_num=seq_num, length=0)
    end_pkt_header.checksum = compute_checksum(end_pkt_header)
    end_pkt = end_pkt_header
    s.sendto(str(end_pkt), (receiver_ip, receiver_port)) 


def main():
    """Parse command-line arguments and call sender function """
    if len(sys.argv) != 4:
        sys.exit("Usage: python sender.py [Receiver IP] [Receiver Port] [Window Size] < [message]")
    receiver_ip = sys.argv[1]
    receiver_port = int(sys.argv[2])
    window_size = int(sys.argv[3])
    sender(receiver_ip, receiver_port, window_size)

if __name__ == "__main__":
    main()
