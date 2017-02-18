from argparse import ArgumentParser
import signal
import sys
import os

from .config import Config
from .vpn import VPN


def exit(msg, status=1):
    print(msg, file=sys.stderr)
    sys.exit(status)


def main():
    parser = ArgumentParser()
    defaultpath = '~/.config/sshsocksvpn.cfg'
    parser.add_argument("action", choices=['start', 'stop'], help='Command to perform\n')
    parser.add_argument('-n', '--name', required=True, help='Name of the client to start')
    parser.add_argument('-p', '--path', help='Config file to use default {}'.format(defaultpath), default=defaultpath)
    options = parser.parse_args()
    try:
        config = Config(os.path.expanduser(options.path))
    except Exception as e:
        exit('Failed to read config: {}'.format(e))

    if options.name not in config.servers:
        exit('Could not find {} in config'.format(options.name), status=1)

    vpn = VPN(config, options.name)

    def handler(signum, frame):
        vpn.stop()

    if options.action == 'start':
        signal.signal(signal.SIGTERM, handler)
        signal.signal(signal.SIGINT, handler)
        try:
            vpn.start()
        except Exception as e:
            exit(str(e), status=1)
    elif options.action == 'stop':
        vpn.stop()


if __name__ == '__main__':
    main()
