
__version__ = "1.0.1"

import os
import sys
import socket
from decimal import Decimal

class MuninPlugin(object):
    title = ""
    args = None
    vlabel = None
    info = None
    category = None
    fields = []

    def __init__(self):
        self.category = os.environ.get('GRAPH_CATEGORY') or self.category
        super(MuninPlugin, self).__init__()

    def autoconf(self):
        return False

    def config(self):
        conf = []
        for k in ('title', 'category', 'args', 'vlabel', 'info', 'scaled'):
            v = getattr(self, k, None)
            if v is not None:
                if isinstance(v, bool):
                    v = "yes" if v else "no"
                conf.append('graph_%s %s' % (k, v))

        for field_name, field_args in self.fields:
            for arg_name, arg_value in field_args.iteritems():
                conf.append('%s.%s %s' % (field_name, arg_name, arg_value))

        print "\n".join(conf)

    def suggest(self):
        sys.exit(1)

    def run(self):
        cmd = (sys.argv[1] if len(sys.argv) > 1 else None) or "execute"
        if cmd == "execute":
            self.execute()
        elif cmd == "autoconf":
            try:
                ac = self.autoconf()
            except Exception, exc:
                print "no (%s)" % str(exc)
                sys.exit(1)
            if not ac:
                print "no"
                sys.exit(1)
            print "yes"
        elif cmd == "config":
            self.config()
        elif cmd == "suggest":
            self.suggest()
        sys.exit(0)

class MuninClient(object):
    def __init__(self, host, port=4949):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.sock.recv(4096) # welcome, TODO: receive all

    def _command(self, cmd, term):
        self.sock.send("%s\n" % cmd)
        buf = ""
        while term not in buf:
            buf += self.sock.recv(4096)
        return buf.split(term)[0]

    def list(self):
        return self._command('list', '\n').split(' ')

    def fetch(self, service):
        data = self._command("fetch %s" % service, ".\n")
        if data.startswith('#'):
            raise Exception(data[2:])
        values = {}
        for line in data.split('\n'):
            if line:
                k, v = line.split(' ', 1)
                values[k.split('.')[0]] = Decimal(v)
        return values
