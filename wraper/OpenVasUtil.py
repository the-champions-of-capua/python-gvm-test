import sys
from gvm.connections import UnixSocketConnection, SSHConnection, DebugConnection
from gvm.protocols.latest import Gmp
# from gvm.xml import pretty_print
from gvm.errors import GvmError

import xmltodict
import json

import logging
from datetime import datetime

DEBUG = True

logging.basicConfig(level=logging.DEBUG, filename="test-gvm" + str(datetime.now().date()) + ".log")

# path = "/var/run/openvasmd.sock"
path = '/var/run/gvmd.sock'

OPENVAS_CONN=DebugConnection(UnixSocketConnection(path=path)) if DEBUG else UnixSocketConnection(path=path)


class OpenVASTool():
    def __init__(self, connection=OPENVAS_CONN, username="admin", password="admin"):
        self.gmp = Gmp(connection=connection)
        self.username=username
        self.password=password
        try:
            self.gmp.authenticate(self.username, self.password)
        except GvmError as e:
            print('An error occurred', e, file=sys.stderr)

    def push_command(self, command, params):
        """

        :param command: 执行的命令, 同openvasmd的cmd
        :param params: 命令中传递的参数
        :return: 返回响应的内容
        """
        with self.gmp:
            if not params:
                responce = self.gmp.__getattribute__(command)()
            else:
                responce = self.gmp.__getattribute__(command)(**params)
            result = json.loads(json.dumps(xmltodict.parse(responce)))
            try:
                return result[command+"_response"]
            except:
                return result
