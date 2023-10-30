#!/usr/bin/env python3
SERVER_IP = "127.0.0.1"
SERVER_PORT = 9999

import socket as s

MSG_SIZE = 999

from threading import Thread, Lock

class ChatProtocol:
    def __init__(self, nick):  # konštruktór
        self._nick = nick  # atribút

    def login(self):  # metóda
        return "LOGIN|{}".format(self._nick).encode()

    def exit(self):  # metóda
        return "EXIT|{}".format(self._nick).encode()

    def send_msg(self, msg):  # metóda
        return "SENDMSG|{}|{}".format(self._nick, msg).encode()

    def who(self):  # metóda
        return "WHO|{}".format(self._nick).encode()

    def users(self, user_list):  # metóda
        users = ""
        for user in user_list:
            users += user + ","
        if len (users) > 1:
            users = users[0:len(users)-1]
        return "USERS|{}".format(self._nick).encode()

    def parse(self, bin_msg : bytes, user_list : list, client_sock : s.socket, lock : Lock):  # metóda
        str_msg = bin_msg.decode()
        list_msg_parts = str_msg.split("|")
        if len (list_msg_parts) > 1:
            nick = list_msg_parts[1]
        if len (list_msg_parts) > 2:
            message = list_msg_parts[2]

        if list_msg_parts[0] == "LOGIN":
            lock.acquire()
            user_list.append(nick)
            lock.release()
            print("Client {} has been connected".format(nick))

        elif list_msg_parts[0] == "EXIT":
            lock.acquire()
            user_list.remove(nick)
            lock.release()
            print("Client {} has been disconnected".format(nick))

        elif list_msg_parts[0] == "SENDMSG":
            print("Client {} message: {}".format(nick, message))

        elif list_msg_parts[0] == "WHO":
            print("Client {} requested list of users".format(nick))
            client_sock.send(self.users(user_list))

        elif list_msg_parts[0] == "USERS":
            users = nick.split(",")
            print("Logged in users: {}.".format(users))

sock = s.socket(family=s.AF_INET, type=s.SOCK_STREAM)
sock.connect((SERVER_IP, SERVER_PORT))

nick = input("Enter nick: ")
protocol = ChatProtocol(nick)
sock.send(protocol.login())

while True:
    msg = input("Enter Message: ")
    if msg[0] == "%":
        if msg[1] == "q":
            sock.send(protocol.exit())
            sock.close()
            exit(0)
        elif msg[1] == "w":
            sock.send(protocol.who())
            bin_msg = sock.recv(MSG_SIZE)
            protocol.parse(bin_msg, None, None, None)

    sock.send(protocol.send_msg(msg))
