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
from typing import Tuple

from qtpy.QtCore import QObject, Slot, Signal, Qt
from qtpy.QtNetwork import QTcpServer, QHostAddress, QTcpSocket
from qtpy.QtWidgets import QVBoxLayout, QLabel
from zeroconf import IPVersion, ServiceInfo, Zeroconf

from vidify import CURRENT_PLATFORM
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
        self.socket.disconnected.connect(self.on_disconnected)
        self.socket.readyRead.connect(self.on_recv)

    def __repr__(self) -> None:
        return f"<Client with IP {self.address}>"

    @Slot()
    def on_disconnected(self):
        logging.info("%s disconnected", self)
        self.finish.emit(self)

    @Slot()
    def on_recv(self):
        """
        Assuming the client sent a message encoded with JSON.

        Currently unused, as the client doesn't send messages to the server.
        """

        msg = self.socket.readAll().data().decode('utf-8')
        try:
            data = json.loads(msg)
        except json.decoder.JSONDecodeError as e:
            logging.info("%s sent invalid message: %s. Original: %s",
                         self, str(e), msg)
        else:
            logging.info("%s sent: %s", self, data)


class ExternalPlayer(PlayerBase):
    """
    The external player acts as a server that sends information about the
    videos to other sources.

    It's used the same way as any other player, but it internally handles the
    connection to clients and sends them the data.

    It uses the Network Service Discovery (NSD) protocol to be visible by
    any other device, and so that they can connect to it.
    """

    # The external player requires a YouTube URL rather than the direct URL,
    # so that it complies with YouTube's Terms Of Service.
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
        self._time_delay = 0
        self._api_name = api_name
        self._clients = []
        # The external player saves the previous values so that they can be
        # sent to new connections.
        self._url = None
        self._is_playing = None

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
            self.labels[key] = QLabel(prefix + '-')
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
        logging.info("Closing the server and unregistering the service")
        try:
            self.unregister_service()
            self._server.close()
        except Exception:
            pass

    def start_server(self) -> None:
        """
        Starts to wait for new connections asynchronously, and registers
        the service so that clients can find Vidify.
        """

        if not self._server.listen(QHostAddress.Any, self.port):
            logging.info("Server couldn't wake up")
            return

        # Updating the port to the one that's actually being used.
        self.port = self._server.serverPort()
        logging.info("Server is listening on port %d", self.port)
        # Now that the port is known, the Vidify service can be
        # registered.
        self.register_service()

    @Slot()
    def on_new_connection(self) -> None:
        """
        When a new client connects to this server, it's added to the current
        clients list until it disconnects.
        """

        while self._server.hasPendingConnections():
            logging.info("Accepting connection number %d", len(self._clients))
            # Saving the client in the internal list
            client = Client(self._server.nextPendingConnection())
            client.finish.connect(self.drop_connection)
            self._clients.append(client)
            # Updating the GUI
            self.update_label('clients', len(self._clients))
            # Sending it the available data
            self.send_message([client], self._url, is_playing=self._is_playing)

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
        s.close()
        logging.info("Using address %s", self.address)

        # Other useful attributes for the connection.
        desc = {
            'os': CURRENT_PLATFORM.name,
            'api': self._api_name
        }
        # The name can't have '.', because it's a special character used as
        # a separator, and some NSD clients can't handle names with it.
        system = f"{platform.system()} {platform.node()}".replace('.', '_')
        full_name = f"{self.SERVICE_NAME} - {system}"
        # The name's maximum length is 64 bytes
        if len(full_name) >= 64:
            full_name = full_name[:60] + "..."

        self.info = ServiceInfo(
            self.SERVICE_TYPE,
            f"{full_name}.{self.SERVICE_TYPE}",
            addresses=[socket.inet_aton(self.address)],
            port=self.port,
            properties=desc)

        logging.info("Registering Vidify service")
        self.zeroconf = Zeroconf(ip_version=self.IP_VERSION)
        self.zeroconf.register_service(self.info)

    def unregister_service(self) -> None:
        self.zeroconf.unregister_service(self.info)
        self.zeroconf.close()

    def send_message(self, clients: Tuple[Client], url: str,
                     absolute_pos: int = None, relative_pos: int = None,
                     is_playing: bool = None) -> None:
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

        for c in clients:
            c.socket.write(dump)
            c.socket.flush()

        logging.info("Sent message '%s' to %s", dump, str(self._clients))

        # The label refresh is done in a separate method at the end to send
        # the TCP packet as soon as possible. This part isn't important.
        for key, val in data.items():
            self.update_label(key, val)

    def update_label(self, key: str, val: any) -> None:
        """
        Updating the labels in the widget, using a consistent syntax.
        """

        self.labels[key].setText(f"{self._LABEL_PREFIXES[key]}{val}")

    def start_video(self, url: str, is_playing: bool = True) -> None:
        """
        When a new video starts, every internal attribute about the song is
        resetted, including the position. The obtained information will be
        sent to the clients.
        """

        self._position = 0
        self._start_time = time.time()
        if not is_playing:
            self._pause_time = self._start_time

        self._url = url
        self._is_playing = is_playing
        self.send_message(self._clients, url, is_playing=is_playing)

    @property
    def position(self) -> int:
        """
        This will return the theoretical position of the external player in
        milliseconds.

        The player doesn't know the position of the clients, so it's
        simulated inside this class. It's a bit complicated, since there are
        four factors that can modify the position:
            * Changing the position manually (absolute)
            * Changing the position manually (relative)
            * Pausing a video: a timestamp of when the video was paused has to
            be saved in order to return the correct position when the player
            is still paused. After playing the video again, the position
            tracker (self._position) has to be updated.
            * The start of a new video: the position tracker starts at zero.
            If the video doesn't start playing
        """

        pos = self._start_time - self._position

        if self._is_playing:
            return int((time.time() - pos) * 1000)
        else:
            return int((self._pause_time - pos) * 1000)

    def seek(self, ms: int, relative: bool = False) -> None:
        """
        After sending the update to the clients, the internal position
        tracker has to be updated, too. The relative position will use the
        previous position value, and the absolute position will use the
        timestamp from when the previous video started playing.
        """

        # Checking for out-of-bounds access with negative values. In that
        # case, the position should be set to zero instead.
        if (relative and self.position + ms < 0) or (not relative and ms < 0):
            self.send_message(self._clients, self._url, absolute_pos=0)
            self._position = 0
            return

        if relative:
            self.send_message(self._clients, self._url, relative_pos=ms)
            self._position += ms / 1000
        else:
            self.send_message(self._clients, self._url, absolute_pos=ms)
            self._position = ms / 1000

    @property
    def pause(self) -> bool:
        return not self._is_playing

    @pause.setter
    def pause(self, do_pause: bool) -> bool:
        """
        Pausing the video also alters the player position. This means that
        when the video is paused, the timestamp is saved. That way, when the
        video starts playing again, it can be calculated, and while it's
        paused, the correct position will be returned.
        """

        if do_pause:
            self._pause_time = time.time()
        else:
            self._start_time += time.time() - self._pause_time

        self.send_message(self._clients, self._url, is_playing=not do_pause)
        self._is_playing = not do_pause
