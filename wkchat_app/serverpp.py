from multiprocessing import Pipe
from wkchat_svr.servermgr import ServerMgr
from wkchat_utils.wkchanel import WKChanel
import asyncio

class SvrWKChannel(WKChanel):
    def send_all(self):
        if self._send_buff != []:
            print("SvrApp send_all" + str(self._send_buff))
        super().send_all()

    def recv_all(self):
        if not self._recv_pipe:
            return
        channel_recv_data = self._recv_pipe.recv()
        for line in list(channel_recv_data):
            fd_id, data, data_id = line
            if fd_id in self._recv_buff:
                self._recv_buff[fd_id][data_id] = data
            else:
                self._recv_buff[fd_id] = {data_id: data}


class ServerApp:
    def __init__(self, pipe: tuple(Pipe())):
        self._channel = SvrWKChannel(pipe)
        self._server_mgr = ServerMgr(self._channel)

    def run(self) -> None:
        print("==" * 10 + "ServerApp run" + '==' * 10)
        while True:
            self._channel.recv_all()
            self._server_mgr.server()
            print("==" * 10 + "ServerApp " + '==' * 10)
            self._channel.send_all()

def server_process_instance(pipe):
    app = ServerApp(pipe)
    app.run()