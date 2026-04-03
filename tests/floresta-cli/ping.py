# SPDX-License-Identifier: MIT OR Apache-2.0

"""
A test that creates a florestad and a bitcoind node, and connects them. We then
send a ping to bitcoind and check if bitcoind receives it, by calling
`getpeerinfo` and checking that we've received a ping from floresta.
"""

import time
from test_framework import FlorestaTestFramework
from test_framework.node import NodeType


class PingTest(FlorestaTestFramework):
    expected_chain = "regtest"

    def set_test_params(self):
        self.florestad = self.add_node_default_args(variant=NodeType.FLORESTAD)
        self.bitcoind = self.add_node_default_args(variant=NodeType.BITCOIND)

    def run_test(self):
        # Start the nodes
        self.run_node(self.florestad)
        self.run_node(self.bitcoind)

        # Connect floresta to bitcoind
        self.connect_nodes(self.florestad, self.bitcoind)

        # Record the current ping byte counter as a baseline.
        peer_info = self.bitcoind.rpc.get_peerinfo()
        initial_ping_bytes = peer_info[0]["bytesrecv_per_msg"].get("ping", 0)

        # Send a ping to bitcoind
        self.log("Sending ping to bitcoind...")
        self.florestad.rpc.ping()

        # Check that bitcoind received at least one additional ping.
        # Depending on timing, bitcoind may already have ping traffic before this test ping.
        final_ping_bytes = initial_ping_bytes
        timeout = time.time() + 10
        while time.time() < timeout:
            peer_info = self.bitcoind.rpc.get_peerinfo()
            final_ping_bytes = peer_info[0]["bytesrecv_per_msg"].get("ping", 0)
            if final_ping_bytes > initial_ping_bytes:
                break
            time.sleep(0.25)

        self.assertTrue(final_ping_bytes > initial_ping_bytes)


if __name__ == "__main__":
    PingTest().main()
