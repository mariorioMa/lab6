#!/usr/bin/env python3

import time
import threading
from random import randint

import switchyard
from switchyard.lib.address import *
from switchyard.lib.packet import *
from switchyard.lib.userlib import *


class Middlebox:
    def __init__(
            self,
            net: switchyard.llnetbase.LLNetBase,
            dropRate="0.19"
    ):
        self.net = net
        self.dropRate = float(dropRate)

    def handle_packet(self, recv: switchyard.llnetbase.ReceivedPacket):
        _, fromIface, packet = recv
        ip_header = packet.get_header(IPv4)
        eth_header = packet.get_header(Ethernet)
        if fromIface == self.intf0: # Received from blaster
            if randint(1, 100) > self.dropRate * 100 : # 满⾜丢包率，随机丢包
                eth_header.src = self.intf1.ethaddr
                eth_header.dst = blastee_eth
                self.net.send_packet(self.intf1, packet)
        elif fromIface == self.intf1: # Received from blastee
            eth_header.src = self.intf0.ethaddr
            eth_header.dst = blaster_eth
            self.net.send_packet(self.intf0, packet)

        # if fromIface == self.intf1:
        #     log_debug("Received from blaster")
        #     '''
        #     Received data packet
        #     Should I drop it?
        #     If not, modify headers & send to blastee
        #     '''
        #     self.net.send_packet("middlebox-eth1", packet)
        # elif fromIface == "middlebox-eth1":
        #     log_debug("Received from blastee")
        #     '''
        #     Received ACK
        #     Modify headers & send to blaster. Not dropping ACK packets!
        #     net.send_packet("middlebox-eth0", pkt)
        #     '''
        else:
            log_debug("Oops :))")

    def start(self):
        '''A running daemon of the router.
        Receive packets until the end of time.
        '''
        while True:
            try:
                recv = self.net.recv_packet(timeout=1.0)
            except NoPackets:
                continue
            except Shutdown:
                break

            self.handle_packet(recv)

        self.shutdown()

    def shutdown(self):
        self.net.shutdown()


def main(net, **kwargs):
    middlebox = Middlebox(net, **kwargs)
    middlebox.start()
