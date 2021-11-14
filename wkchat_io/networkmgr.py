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

    def is_server_listen_fd(self, fd: socket.socket):
        return fd is self._listen_socket

    def is_enbale_select_fds(self):
        return not self._listen_socket is None

    def select_fds(self):
        return select.select(self._read_fds,
                             self._write_fds,
                             self._read_fds,
                             self._select_timeout)

class NetworkMgr:
    def __init__(self):
        self._netConnection = NetworkConnection()
        self._channel = None

        self._can_read_fds = []
        self._can_write_fds = []
        self._exception_fds = []

        self._mark_remove_channel_data_buff = []

    def __do_read_fds(self):
        for fd in self._can_read_fds:
            if self._netConnection.is_server_listen_fd(fd):
                client_socket, client_addr = fd.accept()
                print("新连接：", client_addr)
                client_socket.setblocking(False)
                # 创建一个添加新的socket
                self.__send_channel_data(client_socket, define.ADD_SER_FD, define.ADD_SER_FD_ID)
                # 监听socket读
                self._netConnection.add_read_fd(client_socket)
                self._netConnection
            else:
                try:
                    data = fd.recv(1024).decode("utf-8")
                    if data != "":
                        # 收到数据，监听写
                        self.__send_channel_data(fd, data, hash(data))
                        self._netConnection.add_write_fd(fd)
                    else:
                        # 客户端断开
                        self.__clear_exception_fd(fd)
                except Exception as e:
                    print(e)
                    self.__clear_exception_fd(fd)

    def __do_write_fds(self):
        for fd in self._can_write_fds:
            data_and_data_id = self._channel.get_recv_data(hash(fd))
            if not data_and_data_id or type(data_and_data_id) != dict:
                continue

            for data_id, data in data_and_data_id.items():
                try:
                    fd.send(data.encode("utf-8"))
                    self.__mark_remove_channel_data(hash(fd), data_id)
                    self.__send_channel_data(fd, define.MARKED_MSG_SEND_SUCESS, data_id)
                except Exception as e:
                    print(e)
                    self.__clear_exception_fd(fd)

    def __do_exception_fds(self):
        for fd in self._exception_fds:
            self.__clear_exception_fd(fd)

    def __clear_exception_fd(self, fd):
        self._netConnection.remove_read_fd(fd)
        self._netConnection.remove_write_fd(fd)
        self.__send_channel_data(fd, define.MARKED_MSG_SEND_FAIL, define.MARKED_MSG_SEND_ERROR_ID)
        self.__send_channel_data(fd, define.REMOVE_SER_FD, define.MARKED_MSG_SEND_ERROR_ID)
        self.__mark_remove_channel_data(fd, define.MARKED_MSG_SEND_ERROR_ID)
        fd.close()

    def __send_channel_data(self, fd: socket.socket, data: str, data_id):
        if self._channel:
            self._channel.send_data(hash(fd), data, data_id)

    def __mark_remove_channel_data(self, fd_id, data_id):
        self._mark_remove_channel_data_buff.append((fd_id, data_id))

    def __clear_channel_cache(self):
        if not self._channel:
            assert False
        for fd_id, data_id in self._mark_remove_channel_data_buff:
            self._channel.remove_recv_fd_data(fd_id, data_id)

    def set_channel(self, ch):
        self._channel = ch

    def network_select(self):
         if self._netConnection.is_enbale_select_fds():
            self._can_read_fds, self._can_write_fds, self._exception_fds = self._netConnection.select_fds()
            print("select return : can read:"+ str(len(self._can_read_fds))
                  + "    can_write len:" + str(len(self._can_write_fds))
                  + "    excpection len:" + str(len(self._exception_fds)))

            self.__do_read_fds()
            self.__do_write_fds()
            self.__do_exception_fds()
            self.__clear_channel_cache()
