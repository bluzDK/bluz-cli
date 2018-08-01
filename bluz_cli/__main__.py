import sys
from commands import *

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    if len(args) == 0 or args[0] == 'help':
        print "Welcome to bluz CLI"
        print "This tool will help you provision bluz boards, talk to them over Serial, and update keys"
        print ""
        print "Arguments:"
        print "  provision <API Key>"
        print "    - provisions a new bluz board"
        print ""
    elif args[0] == 'provision':
        Commands.provision(args[1:])
    elif args[0] == 'program':
        Commands.program(args[1:])
    elif args[0] == 'version':
        print "Version: " + str(__init__.__version__)
    else:
        print "Invalid argument, try 'bluz help' for instructions"


if __name__ == '__main__':
    main()