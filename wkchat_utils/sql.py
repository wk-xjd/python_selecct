import sqlite3

class AccountDB:
    def __init__(self):
        self._account_db = sqlite3.connect("account.db")

    def get_account_pwd(self, acc_id: int):
        pass

    def modify_account_pwd(self, acc_id: int, new_pwd: int):
        pass

    def get_account_friends(self, acc_id: int):
        pass

    def add_account_friend(self, acc_id: int, fri_id:int):
        pass


class OffLineMsgDB:
    def __init__(self):
        self._offline_msg_db = sqlite3.connect("offline_msg.db")

    def add_new_msg(self, acc_id: int, msg: str):
        pass

    def mark_read_msg(self, acc_id: int, msg_id: int):
        pass

    def get_offline_msg(self, acc_id: int):
        pass