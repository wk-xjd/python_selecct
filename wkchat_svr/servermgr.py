from wkchat_svr.msgbuff import MsgBuff
from wkchat_io.wkchanel import WKChanel
import define

class SubServer:
    def __init__(self, fd_id):
        self._fd_id = fd_id
        self._msg_buff = MsgBuff()
        self._send_msg_buff = []


    def add_data(self, data):
        self._msg_buff.put_data(data)

    def server(self):
        msg = self._msg_buff.get_msg()
        if not msg:
            return
        self.__handle_msg(msg)

    def __handle_msg(self, msg):
        print("__handle_msg:" + msg)
        self.__send_msg(self._fd_id, "hello wrold")

    def __send_msg(self, fd_id, msg):
        self._send_msg_buff.append((fd_id, msg))

    def get_ready_msg(self):
        return self._send_msg_buff

    def clear_ready_msg(self):
        self._send_msg_buff = []


class ServerMgr:
    def __init__(self, channel:WKChanel):
        self._fd_to_subsvr = dict()
        self._channel = channel
        self._mark_remove_channel_data_buff = []

    def __collect_send_data(self):
        for sub_svr in self._fd_to_subsvr.values():
            msg_list = sub_svr.get_ready_msg()
            for fid, msg in msg_list:
                self._channel.send_data(fid, msg, hash(msg))
            sub_svr.clear_ready_msg()

    def __post_data_to_subsvr(self):
        for fid, data_dict in self._channel.get_recv_all().items():
            for data_id, data in data_dict.items():
                if data.startswith(define.ADD_SER_FD) and not self._fd_to_subsvr.get(fid):
                    self._fd_to_subsvr[fid] = SubServer(fid)

                elif data.startswith(define.REMOVE_SER_FD) and self._fd_to_subsvr.get(fid):
                    self._fd_to_subsvr.pop(fid)

                elif data.startswith(define.MARKED_MSG_SEND_SUCESS):
                    self.__mark_remove_channel_data(fid, data_id)
                elif data.startswith(define.MARKED_MSG_SEND_FAIL):
                    pass
                else:
                    if self._fd_to_subsvr.get(fid, None):
                        self._fd_to_subsvr[fid].add_data(data)
                        self.__mark_remove_channel_data(fid, data_id)

    def __mark_remove_channel_data(self, fd_id, data_id):
        self._mark_remove_channel_data_buff.append((fd_id, data_id))

    def __clear_channel_cache(self):
        for fd_id, data_id in self._mark_remove_channel_data_buff:
            self._channel.remove_recv_fd_data(fd_id, data_id)

    def server(self):
        self.__post_data_to_subsvr()
        self.__clear_channel_cache()
        for sub_svr in self._fd_to_subsvr.values():
            sub_svr.server()
        self.__collect_send_data()
