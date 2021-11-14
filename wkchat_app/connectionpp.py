from wkchat_io import networkmgr, wkchanel
from multiprocessing import Pipe

class ConnectionApp:
    def __init__(self,  pipe: tuple(Pipe())):
        self._svr_channel = wkchanel.WKChanel(pipe)
        self._net_mgr = networkmgr.NetworkMgr()
        self._net_mgr.set_channel(self._svr_channel)

    def run(self):
        while True:
            self._net_mgr.network_select()
            self._svr_channel.send_all()
            self._svr_channel.recv_all()









