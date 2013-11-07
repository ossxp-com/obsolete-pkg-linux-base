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
    -f|--force
        Force install
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
	acl, apt-show-versions, arping, ascii, autofs, bsdutils, bridge-utils, bzip2,
	curl, cabextract, coreutils | shellutils,
	dstat, emacs, ethtool, file, fpdns, fping, fuse-utils,
	git | git-core, gnupg, htop, ia32-libs, ia32-libs-gtk, indent, iproute,
	less, locales, lynx, lsb-release, make, ntfs-3g, ntp | ntpdate, nmap, ngrep,
	openssl, p7zip-full, pciutils, perl, psmisc, preload,
	gistore | etckeeper | rdiff-backup, rsync, rar, ruby, saidar,
	sharutils, ssh, sshfs, star, sudo, sysstat, tcpdump, tmux,
	mercurial, memtester | sysutils, procinfo | sysutils, tofrodos | sysutils,
	udev, unison, vim, vnstat, wget, zhcon,
	'''
############################################################


import myapt as apt
import os, sys, re, string, getopt, tempfile, shutil
import subprocess


interactive = 1
dryrun  = 0
verbose = 0
STAMPFILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), '.%s.done' % os.path.splitext(os.path.basename(__file__))[0])


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

def add_me_to_group( group ):
	if not group:
		raise Exception("no group defined.")

	## Add group if not exist
	found = False
	f = open("/etc/group")
	for line in f:
		if line.startswith(group + ":"):
			found = True
			break
	f.close()
	if not found:
		os.system("addgroup --system %s" % group)

	## Add current user to group
	userid=os.getenv("SUDO_USER", os.getenv("USER"))
	if userid == 'root':
		userid = os.popen("getent passwd 1000").read().strip().split(':')[0]

	if userid and userid != 'root':
		os.system("adduser %s %s" % (userid, group))

def do_config():
	do_patch_config()
	do_config_increase_loopdev()
	do_config_udev_rules()
	do_config_locales()
	add_me_to_group("sudo")
	add_me_to_group("ssh")


def do_patch_config():
	quiltdir="/opt/ossxp/rpatch/linux-base"
	os.system("rpatch -p1 / %s" % quiltdir)


def do_config_increase_loopdev():
	if not os.path.exists('/dev/loop63'):
		for i in range(8,64):
			if os.path.exists('/dev/loop%d' % i):
				continue
			cmd = "mknod -m 660 /dev/loop%d b 7 %d" % (i, i)
			os.system(cmd)
			cmd = "chown root.disk /dev/loop%d" % i
			os.system(cmd)


def do_config_locales():
	locales = [ 'zh_CN', 'zh_CN.GBK', 'zh_CN.UTF-8', 'zh_TW',
				'en_US', 'en_US.UTF-8' ]
	installed = output = subprocess.Popen([ "locale", "-a" ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True ).communicate()[0]
	installed = installed.lower().replace('-','').splitlines()

	uninstalled = [ l for l in locales if l.lower().replace('-','') not in installed ]
	if uninstalled:
		print "Some locale %s not installed, begin install locales:" % uninstalled
		print "Press any key to continue..."
		ignore = raw_input()

		dist = os.popen("lsb_release -i").read().strip().lower()
		if dist.endswith('ubuntu'):
			for locale in locales:
				os.system("locale-gen %s" % locale)
		elif dist.endswith('debian'):
				os.system("dpkg-reconfigure locales || true")
	else:
		print "[1mAll needed locale installed[0m"


def do_config_udev_rules():
	print "[1m========== Note for updating udev rules file ==========[0m"
	print "If this is a VM, it's better rewrite dev rules using this command:"
	print ""
	print "[1m        sh /opt/ossxp/bin/udev-rules.sh > \[0m"
	print "[1m           /etc/udev/rules.d/70-persistent-net.rules[0m"
	print ""

##---------------------------------------------------------------------
def main(argv=None):
	global interactive, dryrun, verbose

	force = False

	if os.getuid() != 0:
		return usage(1, "Error: not try this, only root user can!")

	if argv is None:
		argv = sys.argv
	try:
	    opts, args = getopt.getopt(
		argv[1:], "hivbnqf",
		["help", "verbose", "quiet", "install", "remove", "interactive", "batch", "dryrun", "force"])
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
		elif opt in ('-f', '--force'):
			force = True
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
			if not force and os.path.exists(STAMPFILE):
				if os.path.getmtime(STAMPFILE) > os.path.getmtime(__file__):
					print "%s already installed." % os.path.basename(sys.argv[0])
					return(0)

			do_install()

			os.system('touch %s' % STAMPFILE)

		elif arg in ('config'):
			do_config()


if __name__ == "__main__":
	sys.exit(main())

# vim: noet ts=4 sw=4
