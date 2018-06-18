# dash-ha
Integrate Amazon Dash Button and Home Assistant

## Configuration
### config.yaml

``` yaml
home_assistant:
  api_endpoint: 'http://127.0.0.1:8123/api'
  api_password: ''
  verify_cert: false
buttons:
  - mac: XX:XX:XX:XX:XX:XX
    event: dash_button_nescafe
  - mac: YY:YY:YY:YY:YY:YY
    event: dash_button_evian
```

### Home Assistant

``` yaml
automation:
  - alias: Toggle ceiling light
    trigger:
      platform: event
      event_type: dash_button_nescafe
    action:
      service: homeassistant.toggle
      entity_id: light.livingroom_light
```

## Run in Docker
There is [RasPi-compatible Docker image](https://hub.docker.com/r/uyorum/rpi-dash-ha/)

``` shell
$ docker run -d --name dash --restart=always --net=host -v /path/to/config.yaml:/config.yaml:ro uyorum/rpi-dash-ha
```
