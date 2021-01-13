from PyQt5 import QtWidgets
import socket
import threading
import sys
import time

#为了兼容
if sys.version > '3':
    import queue as Queue
else:
    import Queue


from stok.stopThreading import *



serailTcpQueue = Queue.Queue(256)


class TcpLogic(object):

    tlink = False
    link = False

    def __init__(self, num):
        super(TcpLogic, self).__init__()
        self.tcp_socket = None
        self.client_th = None

        self.link = False


    def tcp_client_start(self, ipAddr, portValue):
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            address = (str(ipAddr), int(portValue))
            #address = ("192.168.31.14", 4533)
            print(address)
        except Exception as ret:
            msg = '请检查目标IP，目标端口\n'
            print(msg)
        else:
            try:
                msg = '正在连接目标服务器\n'
                print(msg)
                self.tcp_socket.connect(address)
            except Exception as ret:
                msg = '无法连接目标服务器\n'
                print(msg)
            else:
                self.link = True
                self.tcp_socket.send(str(address).encode('utf-8'))
                self.client_th = threading.Thread(target=self.tcpClientConcurrency, args=(address,))
                self.client_th.start()
                msg = 'TCP客户端已连接IP:%s端口:%s\n' % address
                print(msg)


    def tcpClientStart(self, ipAddr, portValue):
        if self.link == True:
            self.tcp_close()
            msg = 'TCP客户端已经断开\n'
            print(msg)
        else:
            try:
                self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                address = (str(ipAddr), int(portValue))
                # address = ("192.168.31.14", 4533)
                print(address)
                self.tcp_socket.connect(address)
                self.tcp_socket.send(str(address).encode('utf-8'))
                self.client_th = threading.Thread(target=self.tcpClientConcurrency, args=(address,))
                self.client_th.start()
                msg = 'TCP客户端已连接IP:%s端口:%s\n' % address
            except Exception as e:
                self.tcp_close()
                msg = 'TCP客户端已经断开2\n'
                print(msg)

    def tcpSendMsg(self, sendMsg):
        if self.link is False:
            msg = '请选择服务，并点击连接网络\n'
            print(msg)
        else:
            try:
                send_msg = (str(sendMsg)).encode()
                print("send_msg====", send_msg)
                self.tcp_socket.send(send_msg)
                msg = 'TCP客户端已发送\n'
                print(msg)
            except Exception as ret:
                msg = '发送失败\n'
                print(msg)

    def tcpClientConcurrency(self, address):
        """
        功能函数，用于TCP客户端创建子线程的方法，阻塞式接收
        :return:
        """
        while True:
            recv_msg = self.tcp_socket.recv(1024)
            if recv_msg:
                msg = recv_msg.decode()
                serailTcpQueue.put(msg)
                msg = '来自IP:{}端口:{}:\n{}\n'.format(address[0], address[1], msg)
                print(msg)
            else:
                self.tcp_socket.close()
                self.reset()
                msg = '从服务器断开连接\n'
                print(msg)
                break


    def tcp_close(self):
        """
        功能函数，关闭网络连接的方法
        :return:
        """
        try:
            self.tcp_socket.close()
            self.link = False
            #if self.link is True:
            msg = '已断开网络\n'
            print(msg)
            #############################
            stop_thread(self.client_th)
            msg = '线程已经停止\n'
            print(msg)
        except Exception as ret:
            pass


    def getPos(self):
        print("getPos")
        while True:
            self.tcpSendMsg("p")
            time.sleep(0.5)

    def setPos(self, az, el):
        print("setPos")
        setPosFrame = 'P'+' '+ str(az) + ' ' + str(el)
        print(setPosFrame)




def setPos2(az, el):
    print("setPos")
    setPosFrame = 'set_pos'+' '+ str(az) + ' ' + str(el)
    print(setPosFrame)

if __name__ == '__main__':
    setPos2(55, 23)