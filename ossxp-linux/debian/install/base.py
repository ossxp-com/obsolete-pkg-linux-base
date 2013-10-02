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
	do_config_inputrc()
	do_config_bash()
	do_config_sudo()
	do_config_ssh()
	do_config_sshd()
	do_config_screenrc()
	do_config_indent_pro()
	do_config_increase_loopdev()
	do_config_resolvconf()
	do_config_locales()
	do_config_git()
	do_config_adduser_conf()
	do_config_udev_rules()


def do_config_inputrc():
	options = []
	options.append(
		('add', {'must-not': 'bell-style',
				 'contents': 'set bell-style visible',
				},
		) )

	options.append(
		('add', {'must-not': 'completion-ignore-case',
				 'contents': 'set completion-ignore-case on',
				},
		) )

	options.append(
		('add', {'must-not': 'editing-mode',
				 'contents': 'set editing-mode vi',
				},
		) )

	apt.hack_config_file( '/etc/inputrc', options )


def do_config_bash():
	options = []
	options.append(
		('add', {'must-not': 'bash_completion',
				 'contents': '''
if [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
fi
''',
				},
		) )

	options.append(
		('add', {'must-not': re.compile('set\s+.*\s+vi'),
				 'contents': 'set -o vi',
				},
		) )

	options.append(
		('add', {'must-not': 'svnclean',
				 'contents': '''
#alias svnclean='svn st | grep "^?" | sed -e "s/?//g" | xargs -I {} -i bash -c "echo delete {}; rm -rf {}"'
''',
				},
		) )

	options.append(
		('add', {'must-not': 'alias ll',
				 'contents': """alias ll='ls -al --color=auto'""",
				},
		) )

	CONFFILE='/etc/bash.bashrc'
	if not os.path.exists(CONFFILE):
		CONFFILE='/etc/profile'
	apt.hack_config_file( CONFFILE, options )


def do_config_sudo():
	options = []
	options.append(
		('add', {'must-not': re.compile('^%sudo'),
				 'contents': '%sudo      ALL = NOPASSWD: ALL',
				 'after': [ re.compile('#+\s*%sudo'), 
				 			'# Uncomment to allow members of',
							'# User privilege specification' ],
				},
		) )

	options.append(
		('add', {'must-not': re.compile('User_Alias\s+FULLTIMERS'),
				 'contents': '#User_Alias	FULLTIMERS = admin1,admin2',
				 'after': [ 'Host alias specification',
							'User privilege specification' ],
				},
		) )

	options.append(
		('add', {'must-not': re.compile('FULLTIMERS\s+ALL\s*='),
				 'contents': '#FULLTIMERS	ALL = NOPASSWD: ALL',
				 'after': 'User privilege specification',
				},
		) )

	apt.hack_config_file( '/etc/sudoers', options )

	## Add group sudo if not exist
	add_me_to_group("sudo")



def do_config_sshd():
	options = []
	options.append(
		('add', {'must-not': 'AllowGroups',
				 'contents': '''
## Only allow login if users belong to these groups.
## User shouldn't be in both groups, or user can not login using ssh.
## Person in sftp group can only use chroot sftp service.
AllowGroups ssh sftp
''',
				 'after': [ 'PermitRootLogin', '# Authentication' ],
				},
		) )

	options.append(
		('add', {'must-not': 'UseDNS',
				 'contents': '''
## Specifies whether sshd(8) should look up the remote host name and
## check that the resolved host name for the remote IP address maps back
## to the very same IP address.
## If not disabled, SSHD will try to do a slow reverse lookup of the IP
## address of the client causing for an unnecessary delay during authentication.
UseDNS no
''',
				 'after': [ 'PermitRootLogin', '# Authentication' ],
				},
		) )

	options.append(
		('add', {'must-not': 'Match group sftp',
				 'contents': '''
## People belong to sftp group, can not access ssh, only provide sftp service
## People in this sftp group, can have a invaild shell: /bin/false,
## and user homedir must owned by root user.
#Match group sftp
#    ChrootDirectory  %h
#    X11Forwarding no
#    AllowTcpForwarding no
#    ForceCommand internal-sftp
## END OF File or another Match conditional block
'''
				},
		) )

	apt.hack_config_file( '/etc/ssh/sshd_config', options )

	## Add group ssh if not exist
	add_me_to_group("ssh")


def do_config_ssh():
	options = []
	options.append(
		('add', {'must-not': 'Host *',
				 'contents': '''
Host *
    CheckHostIP no
    ForwardX11 yes
    HashKnownHosts no
    StrictHostKeyChecking no
''',
				},
		) )
	apt.hack_config_file( '/etc/ssh/ssh_config', options )


def do_config_screenrc():
	options = []
	options.append(
		('add', {'must-not': 'defscrollback',
				 'contents': '#defscrollback 3000',
				},
		) )
	options.append(
		('add', {'must-not': 'vbell',
				 'contents': '#vbell on',
				},
		) )
	options.append(
		('add', {'must-not': 'defscrollback',
				 'contents': '#defscrollback 3000',
				},
		) )
	options.append(
		('add', {'must-not': 'startup_message',
				 'contents': '#startup_message off',
				},
		) )
	options.append(
		('add', {'must-not': 'caption always',
				 'contents': '''caption always "%{= kw}%-Lw%{= BW}%n %t%{-}%+w %-= @%H - %Y/%m/%d, %C"''',
				},
		) )

	apt.hack_config_file( '/etc/screenrc', options )

	#if os.path.isfile('/usr/bin/byobu-config'):
	#	os.system('/usr/bin/byobu-config')
	#	print "Run byobu instead of screen for the first time."
	#elif os.path.isfile('/usr/bin/screen-profiles'):
	#	os.system('/usr/bin/screen-profiles')


def do_config_indent_pro():
	CONFFILE='/etc/skel/.indent.pro'
	if not os.path.exists(CONFFILE):
		content = '''
-bad -babbo -nbc -bl -bli0 -bls -c33 -cd33 -ncdb -ncdw -nce
-cli0 -c-d0 -nbfda -di2 -nfc1 -nfca -hnl -ip5 -l75 -lp -pcs -nprs
-psl -sasaw -nsc -nsob -nss -i4 -ts4 -ut
'''
		file = open(CONFFILE, 'w')
		file.write(content)
		file.close()


def do_config_increase_loopdev():
	if not os.path.exists('/dev/loop63'):
		for i in range(8,64):
			if os.path.exists('/dev/loop%d' % i):
				continue
			cmd = "mknod -m 660 /dev/loop%d b 7 %d" % (i, i)
			os.system(cmd)
			cmd = "chown root.disk /dev/loop%d" % i
			os.system(cmd)


def do_config_resolvconf():
	CONFFILE='/etc/resolvconf/resolv.conf.d/tail'
	if os.path.exists(os.path.dirname(CONFFILE)):
		if not os.path.exists(CONFFILE) or os.path.getsize(CONFFILE)==0:
			content = '''
# If you want custom nameservers than what DHCP get, edit this file:
#     /etc/resolvconf/resolv.conf.d/base
#     Add record such as: 'nameserver 127.0.0.1'...
#     Then reload resolvconf: /etc/init.d/resolvconf reload
'''
			file = open(CONFFILE, 'w')
			file.write(content)
			file.close()


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


def do_config_git():
	if os.path.isfile('/usr/bin/git'):
		## aliases
		os.system("git config --system alias.st status")
		os.system("git config --system alias.ci commit")
		os.system("git config --system alias.co checkout")
		os.system("git config --system alias.br branch")
		## ui.color
		os.system('git config --system color.ui "auto"')


def do_config_adduser_conf():
	options = []
	options.append(
		('add', {'must-not': re.compile('^ADD_EXTRA_GROUPS='),
				 'contents': 'ADD_EXTRA_GROUPS=1',
				 'after': re.compile('^#ADD_EXTRA_GROUPS='),
				},
		) )

	options.append(
		('add', {'must-not': re.compile('^EXTRA_GROUPS='),
				 'contents': 'EXTRA_GROUPS=cdrom floppy audio dip video plugdev ssh',
				 'after': re.compile('^#EXTRA_GROUPS='),
				},
		) )

	apt.hack_config_file( '/etc/adduser.conf', options )

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
