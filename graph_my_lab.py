#!/usr/bin/python3

from pyvis.network import Network
import networkx as nx
import sys
import ipaddress
import json

#--TODO-- Add better args parser
if len(sys.argv) < 2:
    print('usage: {} kathara_lab_DIR/!'.format(sys.argv[0]))
    quit()

DIR = sys.argv[1]
ifaces = dict()
domain_map = dict()
images = {
  'internet':'assets/internet_1.png',
  'router': 'assets/router_red.png',
  'network': 'assets/cloud_1.png',
  'host': 'assets/host_1.png',
  'unknown_device': 'assets/host_2.png'
}

G = nx.Graph()

def parse_lab_conf(line):
    parts = line.split('=')
    name_if = parts[0][:-1].split('[')
    name = name_if[0]
    iface = 'eth' + name_if[1]
    domain = parts[1]
    return [domain, name, iface]
  
def parse_startup_line(line):
    items = line.split(' ')
    interface = items[1]
    if len(items) <= 3:
      return [interface, ipaddress.IPv4Interface(items[2])]
    else:
      return [interface, ipaddress.IPv4Interface(items[2] + '/' + items[4])]

    

with open(DIR + "/lab.conf", 'r') as file:
    for line in file.read().split('\n'):
        if line == '':
            continue
        
        domain, name, iface = parse_lab_conf(line)
        domain_map[domain] = 'UNDEFINED'

        if not (name.startswith('pc') or name.startswith('r') or name.startswith('h')):
          print("{} found: Please use either pcx or hx or rx as your host names!".format(name))
          quit()

        if name not in ifaces:
          ifaces[name] = dict()
          
        ifaces[name][iface] = dict()
        ifaces[name][iface]['domain'] = domain

for asset in ifaces:
  with open(DIR + "/" + asset + ".startup", 'r') as f:
    for line in f.read().split('\n'):
      if not line.startswith('ifconfig'):
        continue
      iface, ip = parse_startup_line(line)
      ifaces[asset][iface]['ip'] = str(ip.ip)
      ifaces[asset][iface]['netmask'] = str(ip.netmask)
      network_ip = str(ip.network)
      domain = ifaces[asset][iface]['domain']
      #--TODO--create a domain.conf file for better error correction 
      if domain_map[domain] == 'UNDEFINED':
        domain_map[domain] = network_ip
      elif domain_map[domain] != network_ip:
          print('network ip override! check interfaces connected to [{}] domain!'.format(domain))
          quit()

for asset in ifaces:
  G.add_node(asset)
  G.nodes[asset]['shape'] = 'image'
  if asset.startswith('r'):
    G.nodes[asset]['image'] = images['router']
    G.nodes[asset]['size'] = 25
  elif asset.startswith('h') or asset.startswith('pc'):
    G.nodes[asset]['image'] = images['host']
    G.nodes[asset]['size'] = 20
  else:
    G.nodes[asset]['image'] = images['unknown_device']
    G.nodes[asset]['size'] = 20


for domain, net_ip in domain_map.items():
  G.add_node(domain)
  G.nodes[domain]['label'] = domain + '\n' + net_ip
  G.nodes[domain]['image'] = images['network']
  G.nodes[domain]['shape'] = 'image'
  G.nodes[domain]['size'] = 20

if 'INTERNET' in G.nodes:
  G.nodes['INTERNET']['image'] = images['internet']
  G.nodes['INTERNET']['size'] = '30'
  G.nodes['INTERNET']['label'] = 'INTERNET'


for host, host_ifaces in ifaces.items():
  for interface, params in host_ifaces.items():
    domain = params['domain']
    ip = params['ip']
    G.add_edge(host, domain, label = interface + '\n' + ip)

#print(json.dumps(ifaces))
#print(json.dumps(domain_map))

options = """{
  "edges": {
    "color": {
      "inherit": false
    },
    "smooth": true
  },
  "interaction": {
    "navigationButtons": true
  },
  "physics": {
    "enabled": false
  }
}"""

net = Network(width=1280, height=720, notebook=True)
net.from_nx(G)
#net.show_buttons()
net.set_options(options)
net.show("graph.html")

