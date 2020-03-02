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

from qtpy.QtCore import QObject, Slot, Signal, Qt
from qtpy.QtNetwork import QTcpServer, QHostAddress, QTcpSocket
from qtpy.QtWidgets import QVBoxLayout, QLabel
from zeroconf import IPVersion, ServiceInfo, Zeroconf

from vidify.player import PlayerBase
from vidify.gui import Res, Fonts


class Client(QObject):
    """
    The client object is used by the external player to hold information
    about a connection.
    """

    finish = Signal(object)

    def __init__(self, sock: QTcpSocket) -> None:
        super().__init__()
        self.socket = sock
        self.address = self.socket.peerAddress().toString()
        self.socket.connected.connect(self.on_connected)
        self.socket.disconnected.connect(self.on_disconnected)
        self.socket.readyRead.connect(self.on_recv)
        logging.info("[client:%s] connected", self.address)

    @Slot()
    def on_connected(self):
        logging.info("[client:%s] event", self.address)

    @Slot()
    def on_disconnected(self):
        logging.info("[client:%s] disconnected", self.address)
        self.finish.emit(self)

    @Slot()
    def on_recv(self):
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


class ExternalPlayer(PlayerBase):
    """
    The external player acts as a server that sends information about the
    videos to other sources.
    """

    # External players require a YouTube URL rather than the direct URL,
    # so that they comply with YouTube's Terms Of Service.
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

    # Prefixes for the labels shown in the layout
    _LABEL_PREFIXES = {
        'url': '<b>URL:</b> ',
        'relative_pos': '<b>Last relative position change:</b> ',
        'absolute_pos': '<b>Last absolute position change:</b> ',
        'is_playing': '<b>Is it playing?:</b> ',
        'clients': '<b>Connected clients:</b> '
    }

    def __init__(self, api_name: str) -> None:
        """
        This initializes both the player widget and the TCP server.
        """

        super().__init__()
        # If the port is set to zero, it's chosen automatically. This avoids
        # conflicts when the port is already being used.
        self.port = 0
        self._timestamp = 0
        self._api_name = api_name
        self._media = None
        self._clients = []

        # The player itself contains a label to show messages.
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)
        self.title = QLabel("External player")
        self.title.setStyleSheet("padding: 30px; color: white")
        self.title.setFont(Fonts.title)
        self.layout.addWidget(self.title)
        self.log_layout = QVBoxLayout()
        self.layout.addLayout(self.log_layout)
        # There's a label for each attribute, so they are initialized
        # programatically, and will be updated later.
        self.labels = {}
        for key, prefix in self._LABEL_PREFIXES.items():
            self.labels[key] = QLabel(prefix + '?')
            self.labels[key].setStyleSheet("padding: 20px; color: white")
            self.labels[key].setWordWrap(True)
            self.labels[key].setFont(Fonts.bigtext)
            self.labels[key].setAlignment(Qt.AlignHCenter)
            self.log_layout.addWidget(self.labels[key])

        # Initializing the TCP server
        self._server = QTcpServer()
        self._server.newConnection.connect(self.on_new_connection)
        self.start_server()

    def __del__(self) -> None:
        try:
            self._server.close()
            self.unregister_service()
        except:
            pass

    def start_server(self) -> None:
        """
        Starts to wait for new connections asynchronously, and registers
        the service so that clients can find Vidify.
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
        """
        When a new client connects to this server, it's added to the current
        clients list until it disconnects.
        """

        while self._server.hasPendingConnections():
            logging.info("Accepting connection number %d", len(self._clients))
            client = Client(self._server.nextPendingConnection())
            self._clients.append(client)
            client.finish.connect(self.drop_connection)
            self.update_label('clients', len(self._clients))

    @Slot(object)
    def drop_connection(self, client: Client) -> None:
        """
        Callback for whenever a client disconnects.
        """

        self._clients.remove(client)
        self.update_label('clients', len(self._clients))

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
        # The name can't have '.', because it's a special character used as
        # a separator, and some NSD clients can't handle names with it.
        system = f"{platform.system()}, {platform.node()}".replace('.', '_')

        self.info = ServiceInfo(
            self.SERVICE_TYPE,
            f"{self.SERVICE_NAME} - {system}.{self.SERVICE_TYPE}",
            addresses=[socket.inet_aton(self.address)],
            port=self.port,
            properties=desc)

        logging.info("Registering Vidify service")
        self.zeroconf = Zeroconf(ip_version=self.IP_VERSION)
        self.zeroconf.register_service(self.info)

    def unregister_service(self) -> None:
        self.zeroconf.unregister_service(self.info)
        self.zeroconf.close()

    def send_message(self, url: str, absolute_pos: int = None,
                     relative_pos: int = None, is_playing: bool = None
                     ) -> None:
        """
        Sends a message with the structure defined at the top of this module.
        """

        data = {}
        # The URL shall only be null when the video couldn't be found.
        # Otherwise, it won't be included in the message.
        if url is not None:
            data['url'] = None if url == Res.default_video else url
        # The absolute position has priority over the relative.
        if absolute_pos is not None:
            data['absolute_pos'] = absolute_pos
        elif relative_pos is not None:
            data['relative_pos'] = relative_pos
        if is_playing is not None:
            data['is_playing'] = is_playing
        dump = json.dumps(data).encode('utf-8')
        logging.info("Sending message: %s", dump)

        for client in self._clients:
            logging.info("Sent to %s", client.address)
            client.socket.write(dump)

        # The label refresh is done in a separate method at the end to send
        # the TCP packet as soon as possible. This part isn't important.
        for key, val in data.items():
            self.update_label(key, val)

    def update_label(self, key: str, val: any) -> None:
        """
        Updating the labels in the widget, using a consistent syntax.
        """

        self.labels[key].setText(f"{self._LABEL_PREFIXES[key]}{val}")

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
