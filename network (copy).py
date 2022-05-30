import json

# make bytes into long
# source http://stackoverflow.com/questions/25259947/convert-variable-sized-byte-array-to-a-integer-long
def to_int(bytes):
  return int(bytes.encode('hex'), 16)
  
# make into hex
def clean_hex(n):
    hxstr = hex(n)
    plainstr = hxstr.split("0x")[1]
    return plainstr.split("L")[0]

class customTopo():
    """ create a custom topology"""
    def __init__(self):
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
                switch = self.addSwitch(node['id'].encode('ascii'), listenPort=listenPort, 
                    dpid=our_dpid)
                listenPort += 1
                node_names[node['id'].encode('ascii')] = switch
            else:
                host = self.addHost(node['id'].encode('ascii'), **this_node)
                node_names[node['id'].encode('ascii')] = host
        edges = graph['links']
        for edge in edges:
            delay = str(edge['weight']) + "ms"
            cp = edge['capacity']
            self.addLink(edge['source'],edge['target'],port1=edge['ports'][0], port2=edge['ports'][1],
                         delay=delay, bw=cp)
        print(node_names)

topo= customTopo()
