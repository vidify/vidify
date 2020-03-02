"""
The defined object model for the external API is:

{
    url: 'https://youtube.com/...',
    relative_pos: -1200,
    absolute_pos: 4000,
    is_playing: true
}

`url` is a mandatory field that indicates in respect to what video the update
is being sent. The client will compare it to the currently playing video.
If it's the same, it will just update it. Otherwise, a new video will start
playing with the indicated properties.

The position field can be indicated as relative or absolute to the current
status to the video. If both are provided, the absolute position has
priority over the relative.
"""

import time
import json
import socket
import logging
import platform

from qtpy.QtCore import QObject, Slot, Signal
from qtpy.QtNetwork import QTcpServer, QHostAddress, QTcpSocket
from zeroconf import IPVersion, ServiceInfo, Zeroconf

from vidify.player import PlayerBase
from vidify.gui import Res


class ExternalPlayer(PlayerBase):
    """
    The server object handles asynchronously the connection with a client.
    """

    DIRECT_URL = False

    # The name should be something like Vidify + system specs.
    # This part should also check that there aren't services with the same
    # name already.
    SERVICE_NAME = "vidify"

    # The service type includes the protocols used, like this:
    # "_<protocol>._<transportlayer>".
    # For now, the data is transmitted with TCP, so this is enough.
    SERVICE_TYPE = "_vidify._tcp.local."

    # Trying to use both IPv4 and IPv6
    IP_VERSION = IPVersion.All

    def __init__(self, api_name: str) -> None:
        """
        This also initializes the TCP server.
        """

        super().__init__()
        # If the port is set to zero, it's chosen automatically. This avoids
        # conflicts when the port is already being used.
        self.port = 0
        self._timestamp = 0
        self._api_name = api_name
        self._media = None
        self._clients = []

        # Initializing the TCP server
        self._server = QTcpServer()
        self._server.newConnection.connect(self.on_new_connection)
        self.start()

    def __del__(self) -> None:
        try:
            self._server.close()
            self.unregister_service()
        except:
            pass

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
            logging.info("Accepting connection number %d", len(self._clients))
            client = Client(self._server.nextPendingConnection())
            self._clients.append(client)
            client.finish.connect(lambda: self._clients.remove(client))

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
            'api': self._api_name
        }

        # TODO: Make sure patform.system() doesn't return any '.'
        self.info = ServiceInfo(
            self.SERVICE_TYPE,
            f"{self.SERVICE_NAME} - {platform.system()}.{self.SERVICE_TYPE}",
            addresses=[socket.inet_aton(self.address)],
            port=self.port,
            properties=desc
        )

        self.zeroconf = Zeroconf(ip_version=self.IP_VERSION)
        logging.info("Registering Vidify service")
        self.zeroconf.register_service(self.info)

    def unregister_service(self) -> None:
        self.zeroconf.unregister_service(self.info)
        self.zeroconf.close()

    def send_message(self, url: str = None, relative_pos: int = None,
                     absolute_pos: int = None, is_playing: bool = None
                     ) -> None:
        data = {}
        if url is not None:
            data['url'] = None if url == Res.default_video else url
        if absolute_pos is not None:
            data['absolute_pos'] = absolute_pos
        if relative_pos is not None:
            data['relative_pos'] = relative_pos
        if is_playing is not None:
            data['is_playing'] = is_playing
        dump = json.dumps(data).encode('utf-8')
        logging.info("Sending message: %s", dump)

        for client in self._clients:
            logging.info("Sent to %s", client.address)
            client.socket.write(dump)

    def start_video(self, media: str, is_playing: bool = True) -> None:
        self._timestamp = time.time()
        self._media = media
        self.send_message(media, is_playing=is_playing)

    @property
    def position(self) -> bool:
        return time.time() - self._timestamp if self._timestamp != 0 else 0

    def set_position(self, ms: int, relative: bool = False) -> None:
        if self._media is None:
            return

        if relative:
            self.send_message(self._media, relative_pos=ms)
        else:
            self.send_message(self._media, absolute_pos=ms)

    @property
    def pause(self) -> bool:
        raise NotImplementedError

    @pause.setter
    def pause(self, do_pause: bool) -> bool:
        self.send_message(self._media, is_playing=not do_pause)


class Client(QObject):
    finish = Signal(object)

    def __init__(self, sock: QTcpSocket) -> None:
        super().__init__()
        self.socket = sock
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
        self.finish.emit(self)

    @Slot()
    def on_readyRead(self):
        """
        Assuming the client sent a message encoded with JSON
        """

        msg = self.socket.readAll().data().decode('utf-8')
        try:
            data = json.loads(msg)
        except json.decoder.JSONDecodeError as e:
            logging.info("[client:%s] sent invalid message (%s). Original: %s",
                         self.address, str(e), msg)
        else:
            logging.info("[client:%s] sent: %s", self.address, data)
