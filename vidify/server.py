import time
import json
import socket
import logging
import platform

from qtpy.QtCore import QObject, Slot
from qtpy.QtNetwork import QTcpServer, QHostAddress, QTcpSocket
from zeroconf import IPVersion, ServiceInfo, Zeroconf


class Client(QObject):
    def __init__(self, socket: QTcpSocket) -> None:
        super().__init__()
        self.socket = socket
        self.address = self.socket.peerAddress().toString()
        self.socket.connected.connect(self.on_connected)
        self.socket.disconnected.connect(self.on_disconnected)
        self.socket.readyRead.connect(self.on_readyRead)
        logging.info("[client:%s] connected", self.address)

    @Slot()
    def on_connected(self):
        logging.info("[client:%s] event", self.address)

    @Slot()
    def on_disconnected(self):
        logging.info("[client:%s] disconnected", self.address)

    @Slot()
    def on_readyRead(self):
        """
        Assuming the client sent a message encoded with JSON
        """

        msg = self.socket.readAll()
        try:
            data = json.loads(msg)
        except json.decoder.JSONDecodeError as e:
            logging.info("[client:%s] sent invalid message (%s). Original: %s",
                         self.address, str(e), msg)
        else:
            logging.info("[client:%s] sent: %s", self.address, data)


class Server(QObject):
    """
    The server object handles asynchronously the connection with a client.
    """

    # The name should be something like Vidify + system specs.
    # This part should also check that there aren't services with the same
    # name already.
    SERVICE_NAME = "Vidify"

    # The service type includes the protocols used, like this:
    # "_<protocol>._<transportlayer>".
    # For now, the data is transmitted with TCP, so this is enough.
    SERVICE_TYPE = "_http._tcp.local."

    # Trying to use both IPv4 and IPv6
    IP_VERSION = IPVersion.All

    def __init__(self, api_name: str) -> None:
        """
        This also initializes the TCP server.
        """

        super().__init__()
        self._api_name = api_name
        # If the port is set to zero, it's chosen automatically. This avoids
        # conflicts when the port is already being used.
        self.port = 0

        # Initializing the TCP server
        self._server = QTcpServer()
        self._server.newConnection.connect(self.on_new_connection)

    def start(self) -> None:
        """
        Starts to wait for new connections asynchronously.
        """
        if self._server.listen(QHostAddress.Any, self.port):
            # Updating the port to the one that's actually being used.
            self.port = self._server.serverPort()
            logging.info("Server is listening on port %d", self.port)
            # Now that the port is known, the Vidify service can be
            # registered.
            self.register_service()
        else:
            logging.info("Server couldn't wake up")

    @Slot()
    def on_new_connection(self) -> None:
        while self._server.hasPendingConnections():
            logging.info("Accepting incomming connection")
            self.client = Client(self._server.nextPendingConnection())

    def register_service(self) -> None:
        """
        Registers a service so that it can be detected with the Network
        Service Discovery.
        """

        # Obtaining the local address where the server is running, so that
        # clients in the same network can connect to it.
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 1))
        self.address = s.getsockname()[0]
        logging.info("Using address %s", self.address)

        # Other useful attributes for the connection.
        desc = {
            'api': self._api_name,
            'system': platform.platform()
        }

        self.info = ServiceInfo(
            self.SERVICE_TYPE,
            f"{self.SERVICE_NAME}.{self.SERVICE_TYPE}",
            addresses=[socket.inet_aton(self.address)],
            port=self.port,
            properties=desc,
            server="ash-2.local."  # TODO: what is this?
        )

        self.zeroconf = Zeroconf(ip_version=self.IP_VERSION)
        logging.info("Registering Vidify service")
        self.zeroconf.register_service(self.info)

    def __del__(self) -> None:
        self._server.close()
        self.unregister()

    def unregister(self) -> None:
        self.zeroconf.unregister_service(self.info)
        self.zeroconf.close()
