# SSH Socks5 VPN

## Goal

Have an easy way to manage socks tunnels created via SSH and manage a tun2socks on top of it.

## Dependencies

[Python3](http://www.python.org/)
[openssh](https://www.openssh.com/portable.html)
[badvpn-tun2socks](https://github.com/ambrop72/badvpn)
[psutil](https://github.com/giampaolo/psutil)

## Installation

`pip install sshsocksvpn`


## Configuration

See [examples](https://github.com/grimpy/sshsocksvpn/blob/master/examples/config.cfg)  
For advanced SSH configuration use `~/.ssh/config`


## Usage

```
sshsocksvpn --help
usage: sshsocksvpn [-h] -n NAME [-p PATH] {start,stop}

positional arguments:
  {start,stop}          Command to perform

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  Name of the server to start
  -p PATH, --path PATH  Config file to use default ~/.config/sshvpn.cfg
```
