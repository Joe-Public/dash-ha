from scapy.all import DHCP, sniff
import yaml
import os
from requests import post

path = os.path.dirname(os.path.realpath(__file__))
yaml_dict = yaml.load(open(path + '/config.yaml'))

config = yaml_dict['home_assistant']
host = config['host']
password = config.get('api_password', '')
port = str(config.get('port', 8123))

endpoint = 'http://' + host + ':' + port + '/api/events/'
headers = {'content-type': 'application/json'}
if len(password) > 0:
    headers['x-ha-access'] = password

buttons = {}
for b in yaml_dict['buttons']:
    buttons[b['mac']] = b['event']


def trigger(event):
    response = post(endpoint + event, headers=headers)
    return response.text


def handler(pkt):
    if pkt[DHCP].options[0] == ('message-type', 3):       # DHCP Request
        print "Found DHCP Discover from: " + pkt.src
        if pkt.src in buttons.keys():
            event = buttons.get(pkt.src)
            print "Triggering event: " + event
            print trigger(event)


sniff(prn=handler,
      filter="udp and src host 0.0.0.0 and dst port 67",
      store=0,
      count=0)
