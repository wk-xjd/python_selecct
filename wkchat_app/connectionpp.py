from wkchat_net import networkmgr
from wkchat_utils.wkchanel import WKChanel
from multiprocessing import Pipe
class ConWKChannel(WKChanel):
    def send_all(self):
        if self._send_buff != []:
            print("ConectionAPP====send all" + str(self._send_buff))
        super().send_all()

class ConnectionApp:
    def __init__(self,  pipe: tuple(Pipe())):
        self._svr_channel = ConWKChannel(pipe)
        self._net_mgr = networkmgr.NetworkMgr()
        self._net_mgr.set_channel(self._svr_channel)

    def run(self):
        print("=="*10 + "ConnectionApp run" + '=='*10)
        while True:
            self._net_mgr.network_select()
            self._svr_channel.send_all()
            self._svr_channel.recv_all()