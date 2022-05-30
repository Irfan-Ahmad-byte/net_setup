import json
from mininet.net import Mininet
from mininet.topo import Topo


class customTopo(Topo):
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
