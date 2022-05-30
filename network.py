import argparse
import json
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.log import lg
from mininet.node import RemoteController
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.link import TCLink

# make bytes into long
# source http://stackoverflow.com/questions/25259947/convert-variable-sized-byte-array-to-a-integer-long
def to_int(bytes):
  return int(bytes.encode('hex'), 16)
  
# make into hex
def clean_hex(n):
    hxstr = hex(n)
    plainstr = hxstr.split("0x")[1]
    return plainstr.split("L")[0]

class customTopo(Topo):
    """ create a custom topology"""
    def __init__(self,graph, **opts):
        listenPort = 6653
        Topo.__init__(self, **opts)
        nodes = graph['nodes']
        node_names = {}
        for node in nodes: # node name as unicode str
            if node['type'] == 'switch':
                # datapath id as ascii and to hex
                our_dpid = node['id'].encode('ascii')
                our_dpid = our_dpid.hex()
                switch = self.addSwitch(node['id'], listenPort=listenPort, 
                    dpid=our_dpid)
                listenPort += 1
                node_names[node['id'].encode('ascii')] = switch
            else:
                host = self.addHost(node['id'], mac=node['mac'], ip=node['ip'])
                node_names[node['id'].encode('ascii')] = host
        edges = graph['links']
        for edge in edges:
            delay = str(edge['weight'])+'ms'
            ports = list(edge['ports'].keys())
            p1 = ports[0]
            p2 = ports[1]
            self.addLink(edge['source'],edge['target'],port1=edge['ports'][p1], port2=edge['ports'][p2],
                         delay=delay)

topos = {'customTopo': ( lambda: customTopo() )}

if __name__ == '__main__':
    fl = "network.json"  # You can put your default file here
    remoteIP = "192.168.100.6"      # Put your default remote IP here
    # Using the nice Python argparse library to take in optional arguments
    # for file name and remote controller IP address
    fl = open('network.json')
    graph = json.load(fl)
    fl.close()
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--fl", help="network graph file name")
    parser.add_argument("-ip", "--remote_ip", help="IP address of remote controller")
    args = parser.parse_args()
    if not args.fl:
        print ("fl not specified using: {}".format(fl))
    else:
        fl = args.fl
    if not args.remote_ip:
        print ("remote controller IP not specified using: {}".format(remoteIP))
    else:
        remoteIP = args.remote_ip
    topo = customTopo(graph)
    lg.setLogLevel('info')
    network = Mininet(controller=RemoteController, autoStaticArp=True, link=TCLink)
    network.addController(controller=RemoteController, ip=remoteIP)
    network.buildFromTopo(topo=topo)
    network.start()
    CLI(network)
    network.stop()