#避免出现魔数，预定义一些参数
ADD_SER_FD = "0@add_ser_fd" # 新增一个连接e
REMOVE_SER_FD = "1@remove_svr_fd" # 移除一个连接

MARKED_MSG_SEND_SUCESS = "2@marked_msg_send_sucess" # 标记消息发送成功
MARKED_MSG_SEND_FAIL = "3@marked_msg_send_fail" # 标记消息发送失败
ADD_SER_FD_ID = 0
REMOVE_SER_FD_ID = 1
MARKED_MSG_SEND_ERROR_ID = -1

# 包头
TCP_MSG_HEADER = "0@wk"

# 参数
SERVER_IP = ""
SERVER_PORT = 7890
SERVER_MAX_LISTEN_PORT = 10
SERVER_SELECT_TIMEOUT = 3.0



