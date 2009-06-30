#!/usr/bin/env python
#
'''PROGRAM INTRODUCTION

Usage: %(PROGRAM)s [options] [install] [config]

Options:

    -h|--help
        Print this message and exit.
    -i|--interactive
        Run in interactive mode
    -b|--batch
        Run in batch mode
    -n|--dryrun
        Dryrun mode: acturally, do not run
    -v|--verbose
        Verbose mode: more debug message
    -q|--quiet
        Quiet mode: less message

Actions:
    install
        install packages
    config
        change necessary system config files
'''

############################################################
PKG_LIST='''
	xfce4, xdm, xscreensaver, 
	epiphany-browser, konsole, 
	shorewall | firestarter | guarddog | guidedog | kmyfirewall, 
	alsa-base, alsa-oss, 
	tsclient, xvncviewer, 
	d4x, ossxp-freemind, 
	'''

# foomatic-gui, foomatic-filters-ppds, foomatic-db-hpijs, foomatic-db-gutenprint, 
############################################################


import myapt as apt
import os, sys, getopt, string


interactive = 1
dryrun  = 0
verbose = 1
STAMPFILE = ".desktop.light.done"


def usage(code, msg=''):
	if code:
		fd = sys.stderr
	else:
		fd = sys.stdout
	print >> fd, __doc__
	if msg:
		print >> fd, msg
	sys.exit(code)


def do_install():
	args=[]
	if interactive:
		args.append('-i')
	else:
		args.append('-b')
	if dryrun:
		args.append('-n')
	if verbose:
		args.append('-v')
	else:
		args.append('-q')
	args.append('--install')
		
	print "[1m========== Install ossxp custom packages ==========[0m"
	apt.run( args+ [PKG_LIST] )


def main(argv=None):
	global interactive, dryrun, verbose

	if os.getuid() != 0:
		return usage(1, "Error: not try this, only root user can!")

	if argv is None:
		argv = sys.argv
	try:
	    opts, args = getopt.getopt(
		argv[1:], "hivbnq", 
		["help", "verbose", "quiet", "install", "remove", "interactive", "batch", "dryrun"])
	except getopt.error, msg:
		 return usage(1, msg)

	for opt,arg in opts:
		if opt in ('-h', '--help'):
			return usage(0)
		elif opt in ('-i', '--interactive'):
			interactive = 1
		elif opt in ('-b', '--batch'):
			interactive = 0
		elif opt in ('-n', '--dryrun'):
			dryrun = 1
		elif opt in ('-v', '--verbose'):
			verbose = 1
			apt.verbose = 1
		elif opt in ('-q', '--quiet'):
			verbose = 0
			apt.verbose = 0
		else:
			return usage(1, "Wrong options: %s %s", (opt,arg))

	if len(args) == 0:
		usage(1, "Error: You must provide an action: install or config")

	for arg in args:
		if arg in ('install'):
			if os.path.exists(STAMPFILE):
				print "%s already installed." % os.path.basename(sys.argv[0])
				return(0)

			depends=["desktop-core.py"]
			for pkg in depends:
				cmd="python %s %s" % (pkg, string.join(argv[1:]," "))
				print "[1mDepends on %s, run: %s[0m" % (pkg, cmd)
				os.system(cmd)

			do_install()

			os.system('touch %s' % STAMPFILE)
		if arg in ('config'):
			do_config()


if __name__ == "__main__":
	sys.exit(main())

