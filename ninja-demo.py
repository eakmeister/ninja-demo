#!/usr/bin/env python
"""
Usage:
    ninja-demo.py [--username username] <host> <script>
"""
import contextlib
import docopt
import paramiko
import sys
import threading
import tty

@contextlib.contextmanager
def joining(thread):
    thread.start()

    try:
        yield thread
    finally:
        thread.join()

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
    script = options['<script>']

    if options['--username']:
        username = options['--username']
    else:
        username = None

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect(host, username = username)
    channel = client.invoke_shell()
    
    with joining(threading.Thread(target = display_thread, args = [channel])):
        with contextlib.closing(channel):
            fd = sys.stdin.fileno()
            tty.setcbreak(fd) # echo off

            while True:
                channel.send(sys.stdin.read(1))

if __name__ == '__main__':
    main()
