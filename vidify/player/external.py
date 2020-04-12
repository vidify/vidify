"""
To read more details about the external player API, please check out:
https://vidify.org/wiki/the-external-player-protocol/
"""

import time
import json
import socket
import logging
import platform
from typing import List
from contextlib import suppress

from qtpy.QtCore import QObject, Slot, Signal, Qt
from qtpy.QtNetwork import QTcpServer, QHostAddress, QTcpSocket
from qtpy.QtWidgets import QVBoxLayout, QLabel
from zeroconf import IPVersion, ServiceInfo, Zeroconf

from vidify import CURRENT_PLATFORM
from vidify.player import PlayerBase
from vidify.gui import Res, Fonts
from vidify.version import __version__


class Client(QObject):
    """
    The client object is used by the external player to hold information
    about a connection.
    """

    # Emitted once the client has identified itself successfully
    confirmed = Signal(object)
    # Otherwise, this signal is emitted. It also contains the error message.
    confirm_fail = Signal(object, str)
    # Emitted when the connection with the client is dropped.
    done = Signal(object)

    def __init__(self, sock: QTcpSocket) -> None:
        super().__init__()
        self.id = None
        self._socket = sock
        self.address = self._socket.peerAddress().toString()
        self._socket.disconnected.connect(self.on_disconnected)
        self._socket.readyRead.connect(self.on_recv)

    def __repr__(self) -> str:
        return f"<Client at {self.address}>"

    def send(self, msg: bytes) -> None:
        self._socket.write(msg)

    def disconnect(self) -> None:
        """
        Manually disconnecting implies that the done signal won't be
        emitted.
        """

        self._socket.disconnected.disconnect(self.on_disconnected)
        self._socket.disconnectFromHost()

    @Slot()
    def on_disconnected(self) -> None:
        logging.info("%s disconnected", self)
        self.done.emit(self)

    @Slot()
    def on_recv(self) -> None:
        """
        The client will only send messages to identify itself.
        """

        msg = self._socket.readAll().data().decode('utf-8')
        try:
            data = json.loads(msg)
        except json.decoder.JSONDecodeError as e:
            logging.info("%s sent invalid message: %s. Original: %s",
                         self, str(e), msg)
        else:
            self.identify(data)

    def identify(self, data: dict) -> None:
        try:
            self.id = data['id']
        except KeyError:
            self.confirm_fail.emit(self, f"missing 'id' field")
            return
        else:
            self.confirmed.emit(self)


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

    _CONFIRM_MSG = json.dumps({'success': True}).encode('utf-8')

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
        self._pending = []
        # The external player saves the previous values so that they can be
        # sent to new connections.
        self._media = None
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
            font = Fonts.bigtext
            font.setBold(False)
            self.labels[key].setFont(font)
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
            'id': self.SERVICE_NAME,
            'version': __version__,
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

    @Slot()
    def on_new_connection(self) -> None:
        """
        When a new client connects to this server, it's added to the current
        clients list until it disconnects.
        """

        while self._server.hasPendingConnections():
            logging.info("Accepting connection number %d", len(self._clients))
            # The initial client state is pending, until the first message
            # is received.
            client = Client(self._server.nextPendingConnection())
            self._pending.append(client)
            client.confirmed.connect(self.on_confirmation)
            client.confirm_fail.connect(self.on_confirm_fail)
            client.done.connect(self.on_disconnect)

    @Slot(object)
    def on_confirmation(self, client: Client) -> None:
        """
        Method invoked once the client has identified itself, and the
        connection is assured to be compatible.
        """

        logging.info("Client %s confirmation successful", str(client))
        self._pending.remove(client)
        self._clients.append(client)
        # Sending it the reply and the available data
        client.send(self._CONFIRM_MSG)
        self.send_message([client], self._media, is_playing=self._is_playing)
        # The client won't confirm again
        client.confirmed.disconnect(self.on_confirmation)
        client.confirm_fail.disconnect(self.on_confirm_fail)
        # Updating the GUI
        self.update_label('clients', len(self._clients))

    @Slot(object, str)
    def on_confirm_fail(self, client: Client, msg: str) -> None:
        """
        If a client fails to identify itself, its connection is closed.
        """

        logging.info("Client %s confirmation failed: %s", str(client), msg)

        # Answering back
        reply = json.dumps({
            'success': False,
            'error_msg': msg
        }).encode('utf-8')
        client.send(reply)
        client.disconnect()

        # Cleaning up the client
        self._pending.remove(client)
        del client

    @Slot(object)
    def on_disconnect(self, client: Client) -> None:
        """
        Callback for whenever a client disconnects. It might not have been
        confirmed, so this attempts to remove the client from the pending
        and connected lists.
        """

        with suppress(ValueError):
            self._pending.remove(client)

        with suppress(ValueError):
            self._clients.remove(client)
            self.update_label('clients', len(self._clients))

        del client

    def send_message(self, clients: List[Client], url: str,
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
            c.send(dump)

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

    def start_video(self, media: str, is_playing: bool = True) -> None:
        """
        When a new video starts, every internal attribute about the song is
        resetted, including the position. The obtained information will be
        sent to the clients.
        """

        self._position = 0
        self._start_time = time.time()
        if not is_playing:
            self._pause_time = self._start_time

        self._media = media
        self._is_playing = is_playing
        self.send_message(self._clients, media, is_playing=is_playing)

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
            self.send_message(self._clients, self._media, absolute_pos=0)
            self._position = 0
            return

        if relative:
            self.send_message(self._clients, self._media, relative_pos=ms)
            self._position += ms / 1000
        else:
            self.send_message(self._clients, self._media, absolute_pos=ms)
            self._position = ms / 1000

    @property
    def pause(self) -> bool:
        return not self._is_playing

    @pause.setter
    def pause(self, do_pause: bool) -> None:
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

        self.send_message(self._clients, self._media, is_playing=not do_pause)
        self._is_playing = not do_pause
