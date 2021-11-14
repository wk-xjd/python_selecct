from multiprocessing import Pipe
from wkchat_svr.servermgr import ServerMgr
from wkchat_io.wkchanel import WKChanel

class ClientApp:
    def __init__(self, pipe: tuple(Pipe())):
        self._channel = WKChanel(pipe)
        self._server_mgr = ServerMgr(self._channel)

    def run(self) -> None:
        while True:
            self._channel.recv_all(True)
            self._server_mgr.server()
            self._channel.send_all()

def client_server_instance(pipe):
    app = ClientApp(pipe)
    app.run()