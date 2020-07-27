import socket
import logging

LOGGER = logging.getLogger(__name__)


class MayaClient(object):
    """
    """
    PORT = 7221
    BUFFER_SIZE = 4096

    def __init__(self):
        self.port: int = MayaClient.port
        self.maya_socket: socket.socket = None

    def connect(self, port: int = -1):
        if port >= 0:
            self.port = port
        try:
            self.maya_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.maya_socket.connect("localhost", self.port)
        except ConnectionRefusedError:
            LOGGER.error(f"Failed to connect to port {self.port}", exc_info=1)
            return False

        return True

    def disconnect(self):
        try:
            self.maya_socket.close()
        except BaseException:
            LOGGER.error(f"Failed to close connection on port {self.port}", exc_info=1)
            return False

        return True

    def send(self, command: str):
        try:
            self.maya_socket.sendall(command.encode())
        except Exception:
            LOGGER.error(f"Failed to send command {command}")
            return None

        return self.recv()

    def recv(self):
        try:
            data = self.maya_socket.recv(MayaClient.BUFFER_SIZE)
        except Exception:
            LOGGER.error("Failed to send recv request", exc_info=1)
            return None

        return data.decode().replace("\x00", "")

    # Commands
    def echo(self, text: str):
        cmd = f"eval(\"'{text}'\")"

        return self.send(cmd)


if __name__ == "__main__":
    pass
