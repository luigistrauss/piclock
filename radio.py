import time, datetime, os, sys
import argparse
from socket import error as SocketError
from mpd import MPDClient, MPDError, CommandError

### Settings

HOST = 'localhost'
PORT = '6600'
PASSWORD = False
client = MPDClient()

def radio_start(args):
    try:
        client.connect(host=HOST, port=PORT)
    except SocketError:
        exit(1)

    if PASSWORD:
        try:
            client.password(PASSWORD)
        except CommandError:
            exit(1)

    client.clear()
    if args.volume:
        client.setvol(args.volume)
    client.load('_Radio')
    client.play()

def radio_stop(args):
    try:
        client.connect(host=HOST, port=PORT)
    except SocketError:
        exit(1)
    if PASSWORD:
        try:
            client.password(PASSWORD)
        except CommandError:
            exit(1)
    client.stop()

# Initiate parser
parser = argparse.ArgumentParser(prog='radio', 
        usage='%(prog)s [options] start/stop', 
        description='Play radio streams using mpd daemon')

sp = parser.add_subparsers(help='commands')
sp_start = sp.add_parser('start', help='Starts the radio')
sp_stop = sp.add_parser('stop', help='Stops the radio')
#sp_restart = sp.add_parser('restart', help='Restarts the radio')
parser.add_argument("--volume", "-v", help="set volume level", type=int)

# Hook subparsers up to functions
sp_stop.set_defaults(func=radio_stop)
sp_start.set_defaults(func=radio_start)
#sp_restart.set_defaults(func=radio_restart)

args = parser.parse_args()
args.func(args)
