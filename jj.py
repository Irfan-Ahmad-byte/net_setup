import json

fl = open('network.json')
fl = json.load(fl)
p = list(fl['links'][1]['ports'].keys())
p1 = p[0]
print(fl['links'][1]['ports'][p1])