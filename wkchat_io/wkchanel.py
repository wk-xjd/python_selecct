import multiprocessing
import define


class WKChanel:
    def __init__(self, pipe: tuple(multiprocessing.Pipe())):
        self._send_pipe, self._recv_pipe = pipe
        self._send_buff = []
        self._recv_buff = {}

    def send_data(self, fd_id, data, data_id):
        s_data = (fd_id, data, data_id)
        if s_data not in self._send_buff:
            self._send_buff.append(s_data)

    def send_all(self):
        self._send_pipe.send(self._send_buff)
        if self._send_buff != []:
            print("send_all" + str(self._send_buff))
        self._send_buff = []

    def recv_all(self, block = False):
        if not self._recv_pipe:
            return

        if not block and self._recv_pipe.poll():
            return

        channel_recv_data = self._recv_pipe.recv()
        for line in list(channel_recv_data):
            fd_id, data, data_id = line
            if fd_id in self._recv_buff:
                self._recv_buff[fd_id][data_id] = data
            else:
                self._recv_buff[fd_id] = {data_id: data}

    def get_recv_data(self, fd_id):
        return self._recv_buff.get(fd_id, None)

    def get_recv_all(self):
        return self._recv_buff

    def remove_recv_fd_data(self, fd_id, data_id):
        if fd_id not in self._recv_buff:
            return

        if data_id not in self._recv_buff[fd_id]:
            return

        if data_id == define.MARKED_MSG_SEND_ERROR_ID:
            self._recv_buff.pop(fd_id)
        else:
            self._recv_buff[fd_id].pop(data_id)








