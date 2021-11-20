import socket
import define
from wkchat_net.networkconection import NetworkConnection
from wkchat_utils.wkchanel import WKChanel
from wkchat_utils.wkutils import socket_to_fd_id, str_to_data_id


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
            else:
                try:
                    data = fd.recv(1024)
                    if data != define.EMPTY_BYTES:
                        # 收到数据，监听写
                        self.__send_channel_data(fd, data, str_to_data_id(data))
                        self._netConnection.add_write_fd(fd)
                    else:
                        # 客户端断开
                        self.__clear_exception_fd(fd)
                except Exception as e:
                    print(e)
                    self.__clear_exception_fd(fd)

    def __do_write_fds(self):
        for fd in self._can_write_fds:
            data_and_data_id = self._channel.get_recv_data(socket_to_fd_id(fd))
            if not data_and_data_id or type(data_and_data_id) != dict:
                continue

            for data_id, data in data_and_data_id.items():
                try:
                    fd.send(data.encode("utf-8"))
                    self.__mark_remove_channel_data(socket_to_fd_id(fd), data_id)
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
            self._channel.send_data(socket_to_fd_id(fd), data, data_id)

    def __mark_remove_channel_data(self, fd_id, data_id):
        self._mark_remove_channel_data_buff.append((fd_id, data_id))

    def __clear_channel_cache(self):
        if not self._channel:
            assert False
        for fd_id, data_id in self._mark_remove_channel_data_buff:
            self._channel.remove_recv_fd_data(fd_id, data_id)

    def set_channel(self, ch: WKChanel):
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
