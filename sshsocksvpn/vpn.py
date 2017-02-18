import os
import sys
import subprocess
import random
import psutil
import signal
import time


def execute(args, wait=True):
    print('[+] {}'.format(' '.join(args)), file=sys.stderr)
    process = subprocess.Popen(args, stdin=sys.stdin)
    if wait:
        process.communicate()
    return process


def sudo(args, wait=True):
    args.insert(0, 'sudo')
    return execute(args, wait)


def get_listening_connection(port):
    for connection in psutil.net_connections():
        if connection.laddr[1] == port:
            return connection


class TUN:
    def __init__(self, name, tunip, routes):
        self.name = 'vpn-{}'.format(name)
        self.tunip = tunip
        self.routes = routes

    def exists(self):
        syspath = '/sys/class/net/{}'.format(self.name)
        return os.path.exists(syspath)

    def create(self):
        if self.exists():
            raise RuntimeError("TUN device {} already exists".format(self.name))
        sudo(['ip', 'tuntap', 'add', 'dev', self.name, 'mode', 'tun'])
        sudo(['ip', 'link', 'set', 'dev', self.name, 'up'])
        self.add_ip(self.tunip)
        for route in self.routes:
            self.add_route(route)

    def add_route(self, route):
        sudo(['ip', 'route', 'add', route, 'dev', self.name])

    def destroy(self):
        sudo(['ip', 'link', 'del', self.name])

    def add_ip(self, ip):
        sudo(['ip', 'address', 'add', ip, 'dev', self.name])


class SSHProxy:
    def __init__(self, server):
        self.ipaddr = server['ssh_addr']
        self.port = server.get('ssh_port')
        self.listenport = int(server.get('listen_port', 1080))
        self.proc = None

    def running(self):
        return bool(get_listening_connection(self.listenport))

    def start(self):
        con = get_listening_connection(self.listenport)
        if con:
            proc = psutil.Process(pid=con.pid)
            print('SSH listening addr in used by {}'.format(proc.cmdline()))
        else:
            cmd = ['ssh', '-N', '-o', 'ControlPath=none', '-D', str(self.listenport), self.ipaddr]
            if self.port:
                cmd.extend(['-p', self.port])
            self.proc = execute(cmd, wait=False)
            now = time.time()
            while now > time.time() - 10:
                if self.proc.poll() is not None:
                    raise RuntimeError("SSH command terminated unexpectatly")
                con = get_listening_connection(self.listenport)
                if con:
                    break
                time.sleep(1)
            else:
                self.stop()
                raise RuntimeError("SSH listening port did not become available")

    def stop(self):
        con = get_listening_connection(self.listenport)
        if con and con.pid:
            os.kill(con.pid, signal.SIGTERM)


class Tun2Socks:
    def __init__(self, device, netaddr, socksport):
        self.device = device
        self.netaddr = netaddr
        self.socksport = socksport
        self.proc = None

    def start(self):
        cmd = ['badvpn-tun2socks', '--socks-server-addr', '127.0.0.1:{}'.format(self.socksport),
               '--tundev', self.device, '--netif-ipaddr', self.netaddr,
               '--netif-netmask', '255.255.255.252']
        self.proc = sudo(cmd, wait=False)

    def stop(self):
        for proc in psutil.process_iter():
            cmdline = proc.cmdline()
            if 'badvpn-tun2socks' in cmdline and 'sudo' not in cmdline and '127.0.0.1:{}'.format(self.socksport) in cmdline:
                sudo(['kill', '{}'.format(proc.pid)])
                return


class VPN:
    def __init__(self, config, name):
        self.config = config
        self.name = name
        self.tun = None
        self.sshproxy = None
        self.tunsocks = None
        self._init()

    def _init(self):
        server = self.config.servers[self.name]
        iprange = random.randint(0, 254)
        tunip = '10.66.{}.1/30'.format(iprange)
        gwip = '10.66.{}.2'.format(iprange)
        self.tun = TUN(self.name, tunip, server['routes'])
        self.sshproxy = SSHProxy(server)
        self.tunsocks = Tun2Socks(self.tun.name, gwip, self.sshproxy.listenport)

    def start(self):
        try:
            self.tun.create()
            self.sshproxy.start()
            self.tunsocks.start()
            print('Services running...', file=sys.stderr)
            pids = {self.sshproxy.proc.pid: 'ssh', self.tunsocks.proc.pid: 'tun2socks'}
            pid, status = os.wait()
            for runpid, service in pids.items():
                if runpid == pid:
                    print('{} stopped unexpectatly'.format(service), file=sys.stderr)
        finally:
            self.stop()

    def stop(self):
        if self.tunsocks:
            self.tunsocks.stop()
        if self.sshproxy:
            self.sshproxy.stop()
        if self.tun:
            self.tun.destroy()
