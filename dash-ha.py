from scapy.all import DHCP, sniff
import yaml
import os
from requests import post

from requests.packages.urllib3 import disable_warnings
disable_warnings


class Config:
    def __init__(self, config_path):
        dict = yaml.load(open(config_path))

        api_config = dict['home_assistant']
        self.endpoint = api_config.get('api_endpoint', 'http://127.0.0.18123/api')
        self.password = api_config.get('api_password', '')

        verify_cert = api_config.get('verify_cert', 'true')
        if verify_cert in ['true', 'True', True]:
            self.verify_cert = True
        else:
            self.verify_cert = False

        self.buttons = {}
        for b in dict['buttons']:
            self.buttons[b['mac']] = b['event']


class ApiClient:
    def __init__(self, endpoint, password, verify):
        self.endpoint = endpoint + '/events/'

        headers = {'content-type': 'application/json'}
        if len(password) > 0:
            headers['x-ha-access'] = password

        self.headers = headers
        self.verify = verify

    def trigger(self, event):
        response = post(self.endpoint + event, headers=self.headers, verify=self.verify)
        return response.text


class Handler:
    def __init__(self, client, buttons):
        self.client = client
        self.buttons = buttons

    def handle(self, pkt):
        if pkt.haslayer(DHCP) and pkt[DHCP].options[0] == ('message-type', 3):
            print "Found DHCP Discover from: " + pkt.src
            if pkt.src in self.buttons.keys():
                event = self.buttons.get(pkt.src)
                print "Triggering event: " + event
                print client.trigger(event)


if __name__ == '__main__':
    current_path = os.path.dirname(os.path.realpath(__file__))
    config = Config(current_path + '/config.yaml')

    client = ApiClient(config.endpoint, config.password, config.verify_cert)
    handler = Handler(client, config.buttons)
    sniff(prn=handler.handle,
          filter="udp and src host 0.0.0.0 and dst port 67",
          store=0,
          count=0)
