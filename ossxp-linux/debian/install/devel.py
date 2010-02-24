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
	gcc, gcc-3.4, gdb, g++, make, patch, autoconf, automake, chrpath, cdbs, 
	dh-make, debhelper, dh-buildinfo, dpkg-dev, dpkg-repack, config-package-dev, dpatch, quilt, doxygen, 
	java-package, kernel-package, fakeroot, module-init-tools, 
	devscripts, fakeroot, hdparm, 
	libtool, libc6-dev, libncurses5-dev, 
	libssl-dev, libldap2-dev, libxml2-dev, libexpat1-dev, libperl-dev, libbz2-dev, 
	libc-client2007b-dev | libc-client-dev, libcurl4-openssl-dev | libcurl3-dev, libfreetype6-dev, libgcrypt11-dev, libgd2-xpm-dev, 
	libjpeg62-dev, libmcrypt-dev, libmhash-dev, libmysqlclient15-dev | libmysqlclient-dev, libpng12-dev, libsnmp-dev, 
	libsdl1.2debian, libsdl1.2debian-all, libsdl-image1.2, 
	libsdl1.2-dev, libsdl-image1.2-dev, libasound2, libasound2-dev, 
	lintian, linda, lsb-release, pkg-config, 
	junit, ant, java-gcj-compat-dev, libjcommon-java, libjfreechart-java, libjdom1-java, libbackport-util-concurrent-java, 
	libdbus-1-dev, python-all-dev, ruby1.8, ruby1.8-dev, python-pybabel, python-setuptools, rubygems
	manpages-dev, genisoimage | mkisofs, module-assistant, 
	patchutils, pbuilder, python-dev, qemu, swig, shtool,
	uuid-dev, xutils, zlib1g-dev, 
    git-cvs, git-svn, gitk, mercurial, 
	'''
############################################################


import myapt as apt
import os, sys, getopt, string


interactive = 1
dryrun  = 0
verbose = 1
STAMPFILE = ".devel.done"


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

def do_config():
    pass

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
				if os.path.getmtime(STAMPFILE) > os.path.getmtime(__file__):
					print "%s already installed." % os.path.basename(sys.argv[0])
					return(0)

			depends=["base.py"]
			for pkg in depends:
				cmd="python %s %s" % (pkg, string.join(argv[1:]," "))
				print "[1mDepends on %s, run: %s[0m" % (pkg, cmd)
				os.system(cmd)

			do_install()

			os.system('touch %s' % STAMPFILE)

		elif arg in ('config'):
			do_config()


if __name__ == "__main__":
	sys.exit(main())

