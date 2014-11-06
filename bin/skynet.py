#!/usr/bin/env python

class AnalyzerContainer:
    def __init__(self, name, receive_port=4999, send_port=5000):
        self.name = name
        self.receive_port = receive_port
        self.send_port = send_port
        self.code = ""

class Skynet:
    def initialize_container(container):
        return container

    def register_new_port(container, port):
        return port


# start analyzer, bind analyzer to an internal random port on the host
docker run analyzer:latest -d -p 127:0.0.1:$external_port:5671 --port $external_port

# copy analyzer code to container
docker exec cp analysis.py 

# register new port with HAproxy

# do we do this with the stats socket?
# http://cbonte.github.io/haproxy-dconv/configuration-1.5.html#9.2
# http://www.mgoff.in/2010/04/18/haproxy-reloading-your-config-with-minimal-service-impact/
register_new_port



