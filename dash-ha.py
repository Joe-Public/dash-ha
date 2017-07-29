from scapy.all import DHCP, sniff
import yaml
import os
from requests import post


class Config:
    def __init__(self, config_path):
        dict = yaml.load(open(config_path))

        api_config = dict['home_assistant']
        self.host = api_config['host']
        self.port = str(api_config.get('port', 8123))
        self.password = api_config.get('api_password', '')

        self.buttons = {}
        for b in dict['buttons']:
            self.buttons[b['mac']] = b['event']


class ApiClient:
    def __init__(self, host, port, password):
        self.host = host
        self.port = port
        self.password = password

        self.endpoint = 'http://' + host + ':' + port + '/api/events/'

        headers = {'content-type': 'application/json'}
        if len(password) > 0:
            headers['x-ha-access'] = password

        self.headers = headers

    def trigger(self, event):
        response = post(self.endpoint + event, headers=self.headers)
        return response.text


class Handler:
    def __init__(self, client, buttons):
        self.client = client
        self.buttons = buttons

    def handle(self, pkt):
        if pkt[DHCP].options[0] == ('message-type', 3):
            print "Found DHCP Discover from: " + pkt.src
            if pkt.src in self.buttons.keys():
                event = self.buttons.get(pkt.src)
                print "Triggering event: " + event
                print client.trigger(event)


if __name__ == '__main__':
    current_path = os.path.dirname(os.path.realpath(__file__))
    config = Config(current_path + '/config.yaml')

    client = ApiClient(config.host, config.port, config.password)
    handler = Handler(client, config.buttons)
    sniff(prn=handler.handle,
          filter="udp and src host 0.0.0.0 and dst port 67",
          store=0,
          count=0)
