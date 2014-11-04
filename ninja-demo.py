#!/usr/bin/env python
"""
Usage:
    ninja-demo.py <host> [--username username]
"""
import contextlib
import docopt
import paramiko
import sys
import threading
import tty

def display_thread(channel):
    while True:
        data = channel.recv(1024)

        if data == '':
            break

        sys.stdout.write(data)
        sys.stdout.flush()

def main():
    options = docopt.docopt(__doc__)
    host = options['<host>']

    if options['--username']:
        username = options['--username']
    else:
        username = None

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect(host, username = username)
    channel = client.invoke_shell()
    t = threading.Thread(target = display_thread, args = [channel])
    t.start()

    fd = sys.stdin.fileno()
    tty.setcbreak(fd) # echo off

    try:
        while True:
            channel.send(sys.stdin.read(1))
    except KeyboardInterrupt:
        channel.close()
        client.close()
        t.join()

if __name__ == '__main__':
    main()
