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
	acl, apt-show-versions, ascii, autofs, bsdutils, bridge-utils, bzip2, curl, cabextract, 
	dstat, ethtool, file, fping, flexbackup, fuse-utils, 
	gnupg, htop, ia32-libs, ia32-libs-gtk, indent, iproute, 
	less, locales, lynx, ntfs-3g, ntpdate, nmap, ngrep, 
	openssl, p7zip-full, pciutils, perl, psmisc, 
	rdiff-backup, saidar, screen, shellutils, ssh, star, sudo, sysstat, sysutils, tcpdump, 
	udev, unison, vim, vnstat, wget, zhcon, 
	'''
############################################################


import apt, os, sys, getopt


interactive = 1
dryrun  = 0
verbose = 1


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
		
	print "[1m========== Install debian standard packages ==========[0m"
	cmd = 'aptitude search -F "%p" ~pstandard'
	list = apt.get_list(cmd)
	apt.run( args+ [list] )

	print "[1m========== Install debian required packages ==========[0m"
	cmd = 'aptitude search -F "%p" ~prequired'
	list = apt.get_list(cmd)
	apt.run( args+ [list] )

	print "[1m========== Install debian important packages ==========[0m"
	cmd = 'aptitude search -F "%p" ~pimportant'
	list = apt.get_list(cmd)
	apt.run( args+ [list] )

	print "[1m========== Install ossxp custom packages ==========[0m"
	apt.run( args+ [PKG_LIST] )


def main(argv=None):
	global interactive, dryrun, verbose
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
		elif opt in ('-q', '--quiet'):
			verbose = 0
		else:
			return usage(1, "Wrong options: %s %s", (opt,arg))

	if len(args) == 0:
		usage(1, "Error: You must provide an action: install or config")

	for arg in args:
		if arg in ('install'):
			do_install()
		if arg in ('config'):
			do_config()


if __name__ == "__main__":
	sys.exit(main())

