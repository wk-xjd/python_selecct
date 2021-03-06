"""
为避免粘包，
1-4字节，0@wk：包头
5-8字节， 若为包头则指定发送数据大小
"""
import queue
import define
from wkchat_utils.wkutils import bytebinary_to_num

class MsgBuff:
    def __init__(self, data=b""):
        self._raw_data = data
        self._msg_buff_queue = queue.Queue()
        self._msg_buff = ""
        self._msg_length = 0
        self.__deal_date()

    def __deal_date(self):
        length = len(self._raw_data)
        if length <= 0:
            return

        if length > 8:
            # 取前8个字符，utf-8一个英文字符，一个字节
            header = self._raw_data[0:8]
            length -= 8
            if header[:4] == define.TCP_MSG_HEADER:
                print(header[4:])
                self._msg_length = bytebinary_to_num(header[4:])
                print(self._msg_buff)
                self._raw_data = self._raw_data[8:]

        if self._msg_length > length:
            self._msg_buff + self._raw_data.decode("utf-8")
            self._raw_data = b""
            self._msg_length -= length
        else:
            self._msg_buff += self._raw_data[:self._msg_length].decode('utf-8')
            self._raw_data = self._raw_data[self._msg_length:]
            self._msg_length = 0

        if self._msg_length == 0 and self._msg_buff:
            self._msg_buff_queue.put(self._msg_buff)
            self._msg_buff = ""

    def put_data(self, data):
        self._raw_data = data
        self.__deal_date()

    def get_msg(self):
        if self._msg_buff_queue.empty():
            return None
        return self._msg_buff_queue.get()






