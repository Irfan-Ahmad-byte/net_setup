"""
    A script that will take a NetworkX JSON description file with assigned link ports and host
    IP and MAC addresses and create the network it within Mininet.  It also takes the IP address
    of a remote controller.
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


class GraphTopoFixedAddrPorts(Topo):
    """ Creates a Mininet topology based on a NetworkX graph object where
        hosts have assigned MAC and IP addresses, links ends have assigned port
        numbers, bandwidth and delay. Where the delay comes from the link weight."""
    def __init__(self, graph, **opts):
        listenPort = 6634
        Topo.__init__(self, **opts)
        nodes = graph.nodes()
        node_names = {}
        for node in nodes:
            tmp_node = graph.node[node]
            if tmp_node['type'] == 'switch':
                switch = self.addSwitch(node.encode('ascii'), listenPort=listenPort)
                listenPort += 1
                node_names[node.encode('ascii')] = switch
            else:
                # The following line also sets MAC and IP addresses
                host = self.addHost(node.encode('ascii'), **tmp_node)
                node_names[node.encode('ascii')] = host
        edges = graph.edges()
        for edge in edges:
            props = graph.get_edge_data(edge[0], edge[1])
            delay = str(props['weight']) + "ms"
            bw = props['capacity']
            port1 = props['ports'][edge[0]]
            port2 = props['ports'][edge[1]]
            self.addLink(node_names[edge[0]],node_names[edge[1]],port1=port1, port2=port2,
                         delay=delay, bw=bw)
    @staticmethod
    def from_file(filename):
        """Creates a Mininet topology from a given JSON filename."""
        f = open(filename)
        tmp_graph = json_graph.node_link_graph(in_adjust_ports(json.load(f)))
        f.close()
        return GraphTopoFixedAddrPorts(tmp_graph)

# A small adjustment in port representation from the JSON needed prior
# to converting to NetworkX's internal format.
def in_adjust_ports(gnl_dict):
    """ Converts from ports {"srcPort": num1, "trgPort": num2} format to
        ports {"SrcNodeId": num1, "TrgNodeId": num2} format.
    """
    for link in gnl_dict["links"]:
        if "ports" in link:
            ports = link["ports"]
            new_ports = {
                gnl_dict['nodes'][link["source"]]['id']: ports["srcPort"],
                gnl_dict['nodes'][link["target"]]['id']: ports["trgPort"]}
            link["ports"] = new_ports
    return gnl_dict

if __name__ == '__main__':
    fname = "../samples/ExNetwithLoops1A.json"  # You can put your default file here
    remoteIP = "192.168.1.134"      # Put your default remote IP here
    # Using the nice Python argparse library to take in optional arguments
    # for file name and remote controller IP address
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--fname", help="network graph file name")
    parser.add_argument("-ip", "--remote_ip", help="IP address of remote controller")
    args = parser.parse_args()
    if not args.fname:
        print ("fname not specified using: {}".format(fname))
    else:
        fname = args.fname
    if not args.remote_ip:
        print ("remote controller IP not specified using: {}".format(remoteIP))
    else:
        remoteIP = args.remote_ip
    topo = GraphTopoFixedAddrPorts.from_file(fname)
    lg.setLogLevel('info')
    network = Mininet(controller=RemoteController, autoStaticArp=True, link=TCLink)
    network.addController(controller=RemoteController, ip=remoteIP)
    network.buildFromTopo(topo=topo)
    network.start()
    CLI(network)
    network.stop()
