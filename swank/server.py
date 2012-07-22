import logging
import socket

from protocol import SwankProtocol


# Python 3 support
try:
    import SocketServer as socketserver
except ImportError:
    import socketserver


logging.basicConfig(level=logging.DEBUG,
                    format='%(name)s: %(message)s')


HEADER_LENGTH = 6


class SwankServerRequestHandler(socketserver.BaseRequestHandler):
    """Request handler for the SwankServer.

    Handle protocol requests from swank client by dispatching received
    data to SwankProtocol.dispatch and returns to the client whatever
    it replies.

    """

    def __init__(self, request, client_address, server):
        self.logger = logging.getLogger('SwankServerRequestHandler')
        socketserver.BaseRequestHandler.__init__(
            self, request, client_address, server)

    def handle(self):
        self.logger.debug('handle')
        protocol = SwankProtocol(self.server.socket)
        while True:
            try:
                length = int(self.request.recv(HEADER_LENGTH), 16)
                data = self.request.recv(length)
                self.logger.debug('recv()->"%s"', data)
                ret = protocol.dispatch(data)
                self.logger.debug('send()->"%s"', ret)
                self.request.send(ret)
            except socket.timeout as e:
                self.logger.error('Socket error', e)
                break


class SwankServer(socketserver.TCPServer):
    """Good ol' TCPServer using SwankServerRequestHandler as handler."""

    def __init__(self, server_address, handler_class=SwankServerRequestHandler):
        self.logger = logging.getLogger('SwankServer')
        socketserver.TCPServer.__init__(self, server_address, handler_class)
        self.logger.info('Serving on: {0} ({1})'.format(*self.server_address))


def serve(host="localhost", port=0):
    """Start a swank server on given port.

    If no port is provided then let the OS choose it.

    """
    server = SwankServer((host, port))
    logger = logging.getLogger('serve')
    server.serve_forever()


if __name__ == "__main__":
    import sys

    host = 'localhost'
    port = 0

    if sys.argv[1:]:
        server_address = sys.argv[1].split(":")
        if len(server_address) > 1:
            host, port = server_address
        else:
            host = server_address[0]

    serve(host, int(port))
