import multiprocessing
import asyncio
import define

class WKChanel:
    def __init__(self, pipe: tuple(multiprocessing.Pipe())):
        self._send_pipe, self._recv_pipe = pipe
        self._send_buff = []
        self._recv_buff = {}
        self._recv_buff_fd_set = set()

    def send_data(self, fd_id: int, data: bytes, data_id: int):
        if len(data) == 0:
            return
        s_data = (fd_id, data, data_id)
        if s_data not in self._send_buff:
            self._send_buff.append(s_data)

    def send_all(self):
        if self._send_buff == []:
            return
        self._send_pipe.send(self._send_buff)
        self._send_buff = []


    def recv_all(self):
        if not self._recv_pipe:
            return
        if not self._recv_pipe.poll():
            return
        channel_recv_data = self._recv_pipe.recv()
        for line in list(channel_recv_data):
            fd_id, data, data_id = line
            if fd_id in self._recv_buff:
                self._recv_buff[fd_id][data_id] = data
            else:
                self._recv_buff[fd_id] = {data_id: data}
            self._recv_buff_fd_set.add(fd_id)

    def get_recv_data(self, fd_id: int):
        return self._recv_buff.get(fd_id, None)

    def get_recv_all(self):
        return self._recv_buff

    def remove_recv_fd_data(self, fd_id: int, data_id: int):
        if fd_id not in self._recv_buff:
            return

        if data_id not in self._recv_buff[fd_id]:
            return

        if data_id == define.MARKED_MSG_SEND_ERROR_ID:
            self._recv_buff.pop(fd_id)
            if self.is_recv_data_fd(fd_id):
                self._recv_buff_fd_set.remove(fd_id)
        else:
            self._recv_buff[fd_id].pop(data_id)
            if len(self._recv_buff[fd_id]) <= 0 and self.is_recv_data_fd(fd_id):
                self._recv_buff_fd_set.remove(fd_id)

    def is_recv_data_fd(self, fd_id: int):
        return fd_id in self._recv_buff_fd_set