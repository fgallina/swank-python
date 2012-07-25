import logging
import socket

from protocol import SwankProtocol


# Python 3 support
try:
    import SocketServer as socketserver
except ImportError:
    import socketserver


__all__ = ['HEADER_LENGTH', 'SwankServerRequestHandler',
           'SwankServer', 'serve']


logging.basicConfig(level=logging.DEBUG)


HEADER_LENGTH = 6


class SwankServerRequestHandler(socketserver.BaseRequestHandler):
    """Request handler for the SwankServer.

    Handle protocol requests from swank client by dispatching received
    data to SwankProtocol.dispatch and returns to the client whatever
    it replies.

    """

    def __init__(self, request, client_address, server):
        self.logger = logging.getLogger('SwankServerRequestHandler')
        encodings = {
            "iso-latin-1-unix": "latin-1",
            "iso-utf-8-unix": "utf-8"
        }
        self.encoding = encodings.get(server.encoding, "utf-8")
        socketserver.BaseRequestHandler.__init__(
            self, request, client_address, server)

    def handle(self):
        self.logger.debug('handle')
        protocol = SwankProtocol(self.server.socket)
        first = True
        while True:
            try:
                raw = self.request.recv(HEADER_LENGTH)
                self.logger.debug('raw()->"%s"', raw)
                length = int(raw, 16)
                data = self.request.recv(length)
                self.logger.debug('recv()->"%s"', data)

                if first:
                    ret = protocol.indentation_update()
                    ret = ret.encode(self.encoding)
                    self.logger.debug('send()->"%s"', ret)
                    self.request.send(ret)

                data = data.decode(self.encoding)
                ret = protocol.dispatch(data)
                ret = ret.encode(self.encoding)
                self.logger.debug('send()->"%s"', ret)
                self.request.send(ret + "\n")
                first = False
            except socket.timeout as e:
                self.logger.error('Socket error', e)
                break


class SwankServer(socketserver.TCPServer):
    """Good ol' TCPServer using SwankServerRequestHandler as handler."""

    def __init__(self, server_address, handler_class=SwankServerRequestHandler,
                 port_filename=None, encoding="utf-8"):
        self.logger = logging.getLogger('SwankServer')
        self.port_filename = port_filename
        self.encoding = encoding
        socketserver.TCPServer.__init__(self, server_address, handler_class)
        ipaddr, port = self.server_address
        self.logger.info('Serving on: {0} ({1})'.format(ipaddr, port))
        if port_filename:
            with open(port_filename, 'w') as port_file:
                self.logger.debug('Writing port_file {0}'.format(port_filename))
                port_file.write("{0}".format(port))


def serve(ipaddr="127.0.0.1", port=0, port_filename=None, encoding="utf-8"):
    """Start a swank server on given port.

    If no port is provided then let the OS choose it.

    """
    server = SwankServer((ipaddr, port), port_filename=port_filename,
                         encoding=encoding)
    server.serve_forever()


if __name__ == "__main__":

    ipaddr = "127.0.0.1"
    port = 0
    encoding = "utf-8"

    try:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-a", "--ipaddr", help="bind address", default=ipaddr)
        parser.add_argument(
            "-p", "--port", type=int, help="port", default=port)
        parser.add_argument("-f", "--port-filename")
        parser.add_argument("-e", "--encoding", default=encoding)
        args = parser.parse_args()
    except ImportError:
        import optparse
        parser = optparse.OptionParser()
        parser.add_option(
            "-a", "--ipaddr", help="bind address", default=ipaddr)
        parser.add_option(
            "-p", "--port", type=int, help="port", default=port)
        parser.add_option("-f", "--port-filename")
        parser.add_option("-e", "--encoding", default=encoding)
        (args, _) = parser.parse_args()

    ipaddr = args.ipaddr
    port = args.port
    port_filename = args.port_filename
    encoding = args.encoding

    logger = logging.getLogger('start')
    logger.debug("%s", args)

    serve(ipaddr, int(port), port_filename, encoding)
