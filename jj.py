import json

fl = open('network.json')
fl = json.load(fl)

print(fl['nodes'][1]['ip'])