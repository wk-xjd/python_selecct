import socket


def bytebinary_to_num(byte: bytes) -> int:
    return int(byte.hex(), 16)

def socket_to_fd_id(fd: socket.socket) -> int:
    return fd.fileno()

def str_to_data_id(data: str) -> int:
    return int(hash(data))