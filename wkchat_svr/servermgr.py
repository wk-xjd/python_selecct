from wkchat_svr.subserver import SubServer
from wkchat_utils.wkchanel import WKChanel
from wkchat_utils.wkutils import str_to_data_id
import define
import asyncio

class ServerMgr:
    def __init__(self, channel: WKChanel):
        self._fd_to_subsvr = dict()
        self._channel = channel
        self._mark_channel_cache = []
        self._mark_subsvr_cache = []

    def __collect_send_data(self):
        for sub_svr in self._fd_to_subsvr.values():
            msg_list = sub_svr.get_ready_msg()
            for fid, msg in msg_list:
                self._channel.send_data(fid, msg, str_to_data_id(msg))
            sub_svr.clear_ready_msg()

    def __post_data_to_subsvr(self):
        for fd_id, data_dict in self._channel.get_recv_all().items():
            for data_id, data in data_dict.items():
                if data.startswith(define.ADD_SER_FD):
                    if self.__get_subsvr_by_fd(fd_id):
                        continue
                    self.__insert_fd_and_subsvr(fd_id, SubServer(fd_id))
                    self.__mark_channel_cache(fd_id, data_id)

                elif data.startswith(define.REMOVE_SER_FD):
                    self.__del_subsvr_by_fd(fd_id)
                    self.__mark_channel_cache(fd_id, data_id)

                elif data.startswith(define.MARKED_MSG_SEND_SUCESS):
                    self.__mark_channel_cache(fd_id, data_id)
                    self.__mark_channel_cache(fd_id, data_id)

                elif data.startswith(define.MARKED_MSG_SEND_FAIL):
                    self.__mark_subsvr_cache(fd_id)
                    self.__mark_channel_cache(fd_id, data_id)

                else:
                    print(data)
                    subsvr = self.__get_subsvr_by_fd(fd_id)
                    if subsvr:
                        subsvr.add_data(data)
                        self.__mark_channel_cache(fd_id, data_id)

    def __get_subsvr_by_fd(self, fd_id: int):
        return self._fd_to_subsvr.get(fd_id, None)

    def __del_subsvr_by_fd(self, fd_id):
        if self.__get_subsvr_by_fd(fd_id):
            self._fd_to_subsvr.pop(fd_id)

    def __insert_fd_and_subsvr(self, fd_id: int, subsvr: SubServer):
        if not subsvr:
            return

        self._fd_to_subsvr[fd_id] = subsvr

    def __mark_subsvr_cache(self, fd_id: int):
        self._mark_subsvr_cache.append(fd_id)

    def __clear_subsvr_cache(self):
        for fd_id in self._mark_subsvr_cache:
            self.__del_subsvr_by_fd(fd_id)

    def __mark_channel_cache(self, fd_id: int, data_id: int):
        self._mark_channel_cache.append((fd_id, data_id))

    def __clear_channel_cache(self):
        for fd_id, data_id in self._mark_channel_cache:
            self._channel.remove_recv_fd_data(fd_id, data_id)


    def server(self):
        self.__post_data_to_subsvr()
        self.__clear_channel_cache()
        self.__clear_subsvr_cache()
        for sub_svr in self._fd_to_subsvr.values():
            sub_svr.server()
        self.__collect_send_data()
