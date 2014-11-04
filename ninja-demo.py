#!/usr/bin/env python
"""
Usage:
    ninja-demo.py [--username username] <host> <script>
"""
import contextlib
import docopt
import os
import paramiko
import sys
import threading
import time
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

def parse_next_char(f):
    ch = f.read(1)

    if ch != '\\':
        return ch

    ch = f.read(1)

    if ch == '\\':
        return '\\'
    
    if ch == 'x':
        return f.read(2).decode('hex')

    if ch == 'b':
        while sys.stdin.read(1) != ' ':
            pass

        return ''

    raise Exception('Invalid escape sequence')

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

    width, height = [int(s) for s in os.popen('stty size', 'r').read().split()]
    channel = client.invoke_shell(width = width, height = height)
    
    with joining(threading.Thread(target = display_thread, args = [channel])):
        with contextlib.closing(channel):
            with open(script) as f:
                fd = sys.stdin.fileno()
                tty.setcbreak(fd)

                while True:
                    sys.stdin.read(1)
                    channel.send(parse_next_char(f))

if __name__ == '__main__':
    main()
