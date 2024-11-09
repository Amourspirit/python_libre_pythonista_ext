from __future__ import annotations
from typing import Any, Dict, Tuple, TYPE_CHECKING
import socket
import struct
import threading
import json


_SOCKET_TIMEOUT_SEC = 10

if TYPE_CHECKING:
    from ....___lo_pip___.oxt_logger.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger.oxt_logger import OxtLogger


class SocketManager:
    """
    SocketManager is a class responsible for managing socket connections, including creating server sockets, accepting client connections, sending messages, receiving data, and closing sockets.
    It ensures thread safety using a lock and logs various actions and errors.

    Methods:
        __init__(log: OxtLogger):
            Initializes the SocketManager with a logger, a socket pool, and a lock.
        create_server_socket() -> Tuple[socket.socket, int]:
        accept_client(server_socket: socket.socket, process_id: str) -> socket.socket:
        send_message(message: Dict[str, Any], process_id: str) -> None:
        receive_all(length: int, process_id: str) -> bytes:
        close_socket(process_id: str) -> None:
    """

    def __init__(self):
        """
        Initializes the editor with a logger, a socket pool, and a lock.


        Attributes:
            _socket_pool (Dict[str, socket.socket]): A dictionary to store socket connections.
            log (OxtLogger): The logger instance.
            lock (threading.Lock): A lock to ensure thread safety.
            socket_timeout_sec (int): The timeout period for socket operations. Default is 10 seconds.
        """
        global _SOCKET_TIMEOUT_SEC
        self.socket_timeout_sec = _SOCKET_TIMEOUT_SEC
        self._socket_pool: Dict[str, socket.socket] = {}
        self.log = OxtLogger(log_name=self.__class__.__name__)
        self.lock = threading.Lock()

    def create_server_socket(self) -> Tuple[socket.socket, int]:
        """
        Creates a server socket bound to an available port on localhost.

        Returns:
            Tuple[socket.socket, int]: A tuple containing the server socket object and the port number it is bound to.
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("localhost", 0))  # Bind to an available port
        host, port = server_socket.getsockname()
        server_socket.listen(1)
        server_socket.settimeout(self.socket_timeout_sec)  # Set a timeout of 10 seconds
        return server_socket, port

    def accept_client(
        self, server_socket: socket.socket, process_id: str
    ) -> socket.socket:
        """
        Accepts a client connection on the given server socket and associates it with a process ID.

        Args:
            server_socket (socket.socket): The server socket to accept the client connection on.
            process_id (str): The ID of the process to associate with the client connection.

        Returns:
            socket.socket: The client socket that was accepted.

        Raises:
            socket.timeout: If no client connects within the specified timeout period.
        """
        try:
            client_socket, _ = server_socket.accept()
            with self.lock:
                self._socket_pool[process_id] = client_socket
            self.log.debug(f"Client connected to subprocess {process_id}")
            return client_socket
        except socket.timeout:
            self.log.error(
                f"Accept timed out. No client connected within {_SOCKET_TIMEOUT_SEC} seconds."
            )
            server_socket.close()
            raise

    def send_message(self, message: Dict[str, Any], process_id: str) -> None:
        """
        Sends a JSON-encoded message to a client process via a socket.

        Args:
            message (Dict[str, Any]): The message to be sent, represented as a dictionary.
            process_id (str): The identifier of the client process to which the message will be sent.

        Returns:
            None: This method does not return anything.

        Raises:
            None: This method does not raise any exceptions.

        Logs:
            Logs an error if the process_id is not found in the socket pool.
            Logs the message being sent and the target process_id at debug level.
            Logs an exception if an error occurs while sending the message.
        """

        with self.lock:
            try:
                if process_id not in self._socket_pool:
                    self.log.error(
                        f"send_message() Process {process_id} not found in socket pool"
                    )
                    return
                sock = self._socket_pool[process_id]
                json_message = json.dumps(message)
                message_bytes = json_message.encode()
                message_length = struct.pack("!I", len(message_bytes))
                self.log.debug(
                    f"Sending message to client: {message} to process {process_id}"
                )
                sock.sendall(message_length + message_bytes)
            except Exception:
                self.log.exception("Error sending message")

    def receive_all(self, length: int, process_id: str) -> bytes:
        """
        Receives a specified number of bytes from a socket associated with a given process ID.

        Args:
            length (int): The number of bytes to receive.
            process_id (str): The ID of the process whose socket will be used to receive data.

        Returns:
            bytes: The received data.

        Raises:
            ConnectionResetError: If the connection is closed prematurely.
        """

        data = b""
        with self.lock:
            if process_id not in self._socket_pool:
                return data
            sock = self._socket_pool[process_id]
        while len(data) < length:
            more = sock.recv(length - len(data))
            if not more:
                raise ConnectionResetError("Connection closed prematurely")
            data += more
        return data

    def close_socket(self, process_id: str) -> None:
        """
        Closes and removes the socket associated with the given process ID.

        Args:
            process_id (str): The ID of the process whose socket needs to be closed.
        Returns:
            None: This method does not return anything.
        """

        with self.lock:
            if process_id in self._socket_pool:
                self._socket_pool[process_id].close()
                del self._socket_pool[process_id]
