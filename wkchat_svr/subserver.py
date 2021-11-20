from wkchat_svr.msgbuff import MsgBuff

class SubServer:
    def __init__(self, fd_id: int):
        self._fd_id = fd_id
        self._msg_buff = MsgBuff()
        self._send_msg_buff = []


    def add_data(self, data: bytes):
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
