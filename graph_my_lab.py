#!/usr/bin/python3

from pyvis.network import Network
import networkx as nx
import sys
import ipaddress
import json


#print ('Number of arguments:', len(sys.argv), 'arguments.')
#print ('Argument List:', str(sys.argv))
if len(sys.argv) < 2:
    print('usage: {} kathara_lab_DIR/!'.format(sys.argv[0]))
    quit()
DIR = sys.argv[1]
domain_map = dict()
hosts = list()
routers = list()
domains = list()
ifaces = dict()
domain_network_ip = dict()

def parse_lab_conf(line):
    parts = line.split('=')
    name_if = parts[0][:-1].split('[')
    name = name_if[0]
    iface = 'eth' + name_if[1]
    domain = parts[1]
    #print('{}[{}] => {}'.format(name,iface,domain))
    return [domain, name, iface]


G = nx.Graph()

with open(DIR + "/lab.conf", 'r') as file:
    for line in file.read().split('\n'):
        if line == '':
            continue
        
        domain, name, iface = parse_lab_conf(line)
        if domain not in domain_map:
            domain_map[domain] = list()
        domain_map[domain].append(name)

        if name not in hosts:
            if(name.startswith('r')):
                routers.append(name)
            if(name.startswith('pc') or name.startswith('h')):
                hosts.append(name)
        
        if domain not in domains:
            domains.append(domain)

        if name not in ifaces:
          ifaces[name] = dict()
          
        ifaces[name][iface] = dict()
        ifaces[name][iface]['domain'] = domain

#print(ifaces)
#print(domain_map)
#print('hosts: ', hosts)
#print('domains: ',domains)

for host in hosts + routers:
  with open(DIR + "/" + host + ".startup", 'r') as f:
    for line in f.read().split('\n'):
      if not line.startswith('ifconfig'):
        continue
      _, iface, ip, _, netmask = line.split(' ')
      #print(iface,ip,netmask)
      interface = ipaddress.IPv4Interface(ip + '/' + netmask)
      ifaces[host][iface]['ip'] = ip
      ifaces[host][iface]['netmask'] = netmask
      ifaces[host][iface]['beautiful_ip'] = str(interface)
      #print(interface.network)
      network_ip = str(interface.network)
      domain = ifaces[host][iface]['domain']
      if domain not in domain_network_ip:
        domain_network_ip[domain] = network_ip
      else:
        if domain_network_ip[domain] != network_ip:
          print('network ip override! check al the connected interfaces!')
          quit()
#print(domain_network_ip)

#options = {'color' : 'blue', 'shape':'square', 'group':['a', 'b']}
#options = {'color' : 'blue', 'shape':'square'}
options = {'shape' : 'image', 'image' : 'assets/host_1.png', 'size' : '20'}
colored_hosts = map(lambda node: (node, options), hosts)
colored_hosts = list(colored_hosts)
G.add_nodes_from(colored_hosts)

#options = {'color' : 'red'}
#options = {'color' : 'red', 'shape' : 'image', 'image' : 'assets/router_red.png', 'size' : '50'}
options = {'shape' : 'image', 'image' : 'assets/router_red.png', 'size' : '25'}
colored_routers = map(lambda node: (node, options), routers)
colored_routers = list(colored_routers)
G.add_nodes_from(colored_routers)

#options = {'color' : 'green', 'shape':'diamond'}
options = {'shape' : 'image', 'image' : 'assets/cloud_1.png', 'size' : '20'}
colored_domains = map(lambda node: (node, options), domains)
colored_domains = list(colored_domains)
G.add_nodes_from(colored_domains)
for domain, net_ip in domain_network_ip.items():
  G.nodes[domain]['label'] = domain + '\n' + net_ip
if 'INTERNET' in G.nodes:
  G.nodes['INTERNET']['image'] = 'assets/internet_1.png'
  G.nodes['INTERNET']['size'] = '30'
  G.nodes['INTERNET']['label'] = 'INTERNET'


for host, host_ifaces in ifaces.items():
  for interface, params in host_ifaces.items():
    domain = params['domain']
    ip = params['ip']
    #print(host,interface,ip,' -> ', domain)
    G.add_edge(host, domain, label = interface + '\n' + ip)

print(json.dumps(ifaces))

options = """{
  "nodes": {
    "font": {
      "size": 15
    },
    "size": 70
  },
  "edges": {
    "color": {
      "inherit": false
    },
    "smooth": false
  },
  "layout": {
    "hierarchical": {
      "enabled": false
    }
  },
  "interaction": {
    "navigationButtons": true
  },
  "physics": {
    "enabled": false,
    "minVelocity": 0.75,
    "solver": "hierarchicalRepulsion"
  }
}"""

net = Network(width=1280, height=720, notebook=True)
net.from_nx(G)
#net.show_buttons()
net.set_options(options)
net.show("graph.html")



