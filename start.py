import os, sys

path = os.path.dirname(__file__)
sys.path.append(path)
from server import tcpServer

if __name__ == '__main__':
    tcpServer.server_run()
