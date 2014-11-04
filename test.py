import sys
import tty

fd = sys.stdin.fileno()
tty.setcbreak(fd)

while True:
    print ord(sys.stdin.read(1))
