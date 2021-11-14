from multiprocessing import Pipe
from wkchat_svr.servermgr import ServerMgr
from wkchat_io.wkchanel import WKChanel

class ServerApp:
    def __init__(self, pipe: tuple(Pipe())):
        self._channel = WKChanel(pipe)
        self._server_mgr = ServerMgr(self._channel)

    def run(self) -> None:
        while True:
            self._channel.recv_all(True)
            self._server_mgr.server()
            self._channel.send_all()

def server_process_instance(pipe):
    app = ServerApp(pipe)
    app.run()