.PHONY: all

image:
	docker build -t uyorum/rpi-dash-ha -f Dockerfile-rpi .

push:
	docker push uyorum/rpi-dash-ha
