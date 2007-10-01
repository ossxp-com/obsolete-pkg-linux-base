#!/usr/bin/python

'''
Checks for available VNC display number.

Usage: vncport.py [options]

Options:
    -h|--help
            Print this message and exit.
    -q|--quiet
            Quiet mode.
    -c|--check <Num>
            Check whether display #Num is availble.
    -a|--available
            Check next available display number.
'''

import getopt,os,socket,sys

# A display number n is taken if something is listening on the VNC server port
# (5900+n) or the X server port (6000+n).
def CheckDisplayNumber(n):
    n = int(n)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if s.connect_ex(('localhost', 6000+n)) == 0:
        print_err ( "Warning: display #%d is taken because of port %d is used." % (n,6000+n) )
        s.close()
	return 0

    if s.connect_ex(('localhost', 5900+n)) == 0:
        print_err ( "Warning: display #%d is taken because of port %d is used." % (n,5900+n) )
        s.close()
	return 0

    s.close()

    if os.access("/tmp/.X%d-lock" % n, os.F_OK) :
        print_err ( "Warning: display #%d is taken because of /tmp/.X%d-lock" % (n,n) )
	return 0

    if os.access("/tmp/.X11-unix/X%d" % n, os.F_OK) :
        print_err ( "Warning: display #%d is taken because of /tmp/.X11-unix/X%d" % (n,n) )
	return 0

    return 1

def GetAvailableDisplay():
    for port in range(0,100):
        if (CheckDisplayNumber(port)):
            print_msg ( "Display #%d is available." % port )
	    return port


def usage(code=0, msg=''):
    if code:
        fd = sys.stderr
    else:
        fd = sys.stdout
    print >> fd, __doc__
    if msg:
        print >> fd, msg
    return code

def print_err(msg):
    global opt_verbose
    if opt_verbose == 1:
        print >> sys.stderr, msg

def print_msg(msg):
    global opt_verbose
    if opt_verbose == 1:
        print msg

opt_verbose=1
opt_check=0
opt_available=0

def main(argv=None):
    global opt_verbose, opt_check, opt_available
    if argv is None:
        argv = sys.argv
    try:
        opts, args = getopt.getopt(
            argv[1:], "hc:avq",
            ["help","check=","available","verbose","quiet"])
    except getopt.error, msg:
        return usage(1, msg)

    if len(opts) == 0 or len(args) > 0:
        return usage(1)

    for opt, arg in opts:
        if opt in ("-v", "--verbose"):
	    opt_verbose = 1
        elif opt in ("-q", "--quiet"):
	    opt_verbose = 0
        if opt in ("-h", "--help"):
            return usage()
        elif opt in ("-c", "--check"):
	    opt_check = 1
	    var_check = arg
        elif opt in ("-a", "--available"):
	    opt_available= 1

    if opt_check == 1:
	    return CheckDisplayNumber(var_check)
    elif opt_available == 1:
	    return GetAvailableDisplay()

if __name__ == "__main__":
    sys.exit(main())

