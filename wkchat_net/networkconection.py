import socket
import select
import define

class NetworkConnection:
    def __init__(self):
        self._listen_max_num = define.SERVER_MAX_LISTEN_PORT
        self._server_address = (define.SERVER_IP, define.SERVER_PORT)
        self._listen_socket = None
        self._select_timeout = define.SERVER_SELECT_TIMEOUT

        self._read_fds = []
        self._write_fds = []

        self.__init_listen_socket()

    def __del__(self):
        self.__unint_listen_socket()

    def __init_listen_socket(self):
        self._listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 设置退出后，立刻释放端口占用，避免重启后端口被占用
        self._listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self._listen_socket.bind(self._server_address)
        self._listen_socket.listen(self._listen_max_num)
        # 设置非阻塞
        self._listen_socket.setblocking(False)
        # 加入侦听队列
        self.add_read_fd(self._listen_socket)

    def __unint_listen_socket(self):
        if self._listen_socket:
            self._listen_socket.close()

    def add_read_fd(self, fd: socket.socket):
        if fd not in self._read_fds:
            self._read_fds.append(fd)

    def remove_read_fd(self, fd: socket.socket):
        if fd in self._read_fds:
            self._read_fds.remove(fd)

    def add_write_fd(self, fd: socket.socket):
        if fd not in self._write_fds:
            self._write_fds.append(fd)

    def remove_write_fd(self, fd: socket.socket):
        if fd in self._write_fds:
            self._write_fds.remove(fd)

    def update_write_fds(self, fds: list):
        self._write_fds = fds

    def is_server_listen_fd(self, fd: socket.socket):
        return fd is self._listen_socket

    def is_enbale_select_fds(self):
        return not self._listen_socket is None

    def select_fds(self):
        return select.select(self._read_fds,
                             self._write_fds,
                             self._read_fds,
                             self._select_timeout)