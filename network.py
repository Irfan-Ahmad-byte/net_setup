"""
    A script that will take a NetworkX JSON description file with assigned link ports and host
    IP and MAC addresses and create the network it within Mininet.  It also takes the IP address
    of a remote controller.  
    
    This version of NetRunner sets the OpenFlow switch DPID directly based on
    the switch name. Switch names must be short (less than 8 characters) ASCII
    character sequences.
    
    usage: sudo python NetRunner2.py -f net_file_name -ip remote_controller_ip_address
"""
import argparse
import json
from mininet.cli import CLI
from mininet.log import lg
from mininet.node import RemoteController
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.link import TCLink
from networkx.readwrite import json_graph

# make butes into long
# source http://stackoverflow.com/questions/25259947/convert-variable-sized-byte-array-to-a-integer-long
def to_int(bytes):
  return int(bytes.encode('hex'), 16)
  
# make into hex
def clean_hex(n):
    hxstr = hex(n)
    plainstr = hxstr.split("0x")[1]
    return plainstr.split("L")[0]

class cutomTopo(Topo):
    """ create a custom topology"""
    def __init__(self, **opts):
        listenPort = 6653
        Topo.__init__(self, **opts)
        fl = open('network.json')
        graph = json.load(fl)
        fl.close()
        nodes = graph['nodes']
        node_names = {}
        for node in nodes: # node name as unicode str
            this_node = node[node]
            if this_node['type'] == 'switch':
                # datapath id as ascii and to hex
                our_dpid = clean_hex(to_int(node['id'].encode('ascii'))) 
                print ("Node: {} dpid: {}".format(node, our_dpid))
                switch = self.addSwitch(node['id'].encode('ascii'), listenPort=listenPort, 
                    dpid=our_dpid)
                listenPort += 1
                node_names[node['id'].encode('ascii')] = switch
            else:
                # The following line also sets MAC and IP addresses
                host = self.addHost(node['id'].encode('ascii'), **this_node)
                node_names[node['id'].encode('ascii')] = host
        edges = graph['links']
        for edge in edges:
            delay = str(edge['weight']) + "ms"
            cp = edge['capacity']
            self.addLink(edge['source'],edge['target'],port1=edge['ports'][0], port2=edge['ports'][1],
                         delay=delay, bw=cp)
    # @staticmethod
    # def from_file(filename):
    #     """Creates a Mininet topology from a given JSON filename."""
    #     f = open(filename)
    #     tmp_graph = json_graph.node_link_graph(json.load(f))
    #     f.close()
    #     print(tmp_graph.nodes(data=True))
    #     #print(tmp_graph.links())
    #     #exit()
    #     return GraphTopoFixedAddrPorts(tmp_graph)


topos = {'customTopo': ( lambda: customTopo() )}
