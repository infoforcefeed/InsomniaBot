import logging
import select
import socket


class SocketProxy(object):
    
    def __init__(self, server_host, server_port, proxy_host='0.0.0.0', proxy_port='8080'):

        self.server_host = server_host
        self.server_port = int(server_port)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.proxy_host = proxy_host
        self.proxy_port = int(proxy_port)
        self.proxy_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.proxy_conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.proxy_conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.pipes = []

    def connect(self):
        "Connects to the server"
        self.server.connect((self.server_host, self.server_port))

    def listen(self):
        "Waits for a connection"
        self.proxy_conn.bind((self.proxy_host, self.proxy_port))
        self.proxy_conn.listen(1)
        self.proxy_conn.accept()
        self.proxy, addr = self.proxy_conn.accept()
        logging.info('{} connected'.format(addr))

    def proxy_data(self, sender, receiver):
        receiver.send(sender.recv(4096))

    def run(self):
        "Waits for a connection to the proxy, then connects to the server, then proxies data"

        self.listen()
        self.connect()

        while True:
            # Wait for one of the sockets to be readable
            sockets = (self.server, self.proxy)
            readables, _, errors = select.select(sockets, (), sockets, 30)

            for readable in readables:
                if readable is self.server:
                    self.proxy_data(self.server, self.proxy)
                else:
                    self.proxy_data(self.proxy, self.server)


class SocketPlumbing(SocketProxy):
    "Now with pipes!"

    def add_pipe(self, pipe):
        self.pipes.append(pipe)

    def feed_pipes(self, data, direction):
        for pipe in self.pipes:
            data = pipe.recieve(data, direction)
        return data

    def proxy_data(self, sender, receiver):
        data = sender.recv(4096)
        if sender is self.server:
            direction = 'inbound'
        if sender is self.proxy:
            direction = 'outbound'
        data = self.feed_pipes(data, direction)
        receiver.send(data)


class Pipe(object):
    "Can be hooked up to a SocketPlumbing"

    def attach_pipe(self, proxy):
        self.proxy = proxy

    def send_inbound(self, data):
        self.proxy.send(data, 'inbound')

    def send_outbound(self, data):
        self.proxy.send(data, 'outbound')

    def recieve_inbound(self, data):
        return data

    def recieve_outbound(self, data):
        return data

    def recieve(self, data, direction):
        if direction == 'inbound':
            return self.recieve_inbound(data)
        if direction == 'outbound':
            return self.recieve_outbound(data)


def main(proxy_class):

    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser(description='Proxy a socket connection')
    parser.add_argument('host')
    parser.add_argument('port')
    args = parser.parse_args()

    # Setup logging to stdout
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())

    # Start proxy
    logging.info('Starting proxy to connect to {} on port {}'.format(args.host, args.port))
    proxy = proxy_class(args.host, args.port)
    proxy.run()

if __name__ == '__main__':
    main(SocketProxy)
