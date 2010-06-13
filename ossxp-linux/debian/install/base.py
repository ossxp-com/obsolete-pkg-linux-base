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
	acl, apt-show-versions, ascii, autofs, bsdutils, bridge-utils, bzip2,
	curl, cabextract, coreutils | shellutils,
	dstat, ethtool, file, fpdns, fping, fuse-utils,
	git-core, gnupg, htop, ia32-libs, ia32-libs-gtk, indent, iproute,
	less, locales, lynx, lsb-release, make, ntfs-3g, ntp | ntpdate, nmap, ngrep,
	openssl, p7zip-full, pciutils, perl, psmisc, preload,
	gistore | etckeeper | rdiff-backup, rsync, rar, saidar,
	byobu | screen screen-profiles screen-profiles-extras,
	sharutils, ssh, sshfs, star, sudo, sysstat, tcpdump,
	mercurial, memtester | sysutils, procinfo | sysutils, tofrodos | sysutils,
	udev, unison, vim, vnstat, wget, zhcon,
	'''
############################################################


import myapt as apt
import os, sys, re, string, getopt, tempfile, shutil


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
	if userid and userid != 'root':
		os.system("adduser %s %s" % (userid, group))

def do_config():
	#------------------------------------------------------------
	CONFFILE='/opt/ossxp/conf/public.key'
	if os.path.exists(CONFFILE):
		os.system('apt-key add %s' % CONFFILE)
	
	#------------------------------------------------------------
	CONFFILE='/etc/inputrc'
	if os.path.exists(CONFFILE):
		patch = {}
		patch['filemod'] = "644"
		patch['precheck_deny'] = "set completion-ignore-case on"
		patch['stamp_before'] = "##### ossxp_config_begin #####"
		patch['stamp_end']    = "##### ossxp_config_end #####"
		patch['append']    = '''
set bell-style visible
set completion-ignore-case on
set editing-mode vi
'''
		apt.config_file_append(CONFFILE, patch)	

	#------------------------------------------------------------
	CONFFILE='/etc/bash.bashrc'
	if not os.path.exists(CONFFILE):
		CONFFILE='/etc/profile'
	if os.path.exists(CONFFILE):
		patch = {}
		patch['filemod'] = "644"
		patch['precheck_deny'] = "set -o vi"
		patch['stamp_before'] = "##### ossxp_config_begin #####"
		patch['stamp_end']    = "##### ossxp_config_end #####"
		if os.path.exists('/etc/bash_completion'):
			patch['append']    = '''
if [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
fi
set -o vi
alias svnclean='svn st | grep "^?" | sed -e "s/?//g" | xargs -I {} -i bash -c "echo delete {}; rm -rf {}"'
alias ll='ls -al --color=auto'
'''
		else:
			patch['append']    = '''
set -o vi
'''
		apt.config_file_append(CONFFILE, patch)	

	#------------------------------------------------------------
	CONFFILE='/etc/sudoers'
	if os.path.exists(CONFFILE):
		patch = {}
		patch['filemod'] = "440"
		patch['precheck_deny'] = "ossxp_config_begin"
		patch['stamp_before'] = "##### ossxp_config_begin #####"
		patch['stamp_end']    = "##### ossxp_config_end #####"
		patch['append']    = '''
%sudo      ALL = NOPASSWD: ALL

#User_Alias	FULLTIMERS = admin1,admin2
#FULLTIMERS	ALL = NOPASSWD: ALL
'''
		apt.config_file_append(CONFFILE, patch)	

		## Add group sudo if not exist
		add_me_to_group("sudo")

	#------------------------------------------------------------
	CONFFILE='/etc/ssh/sshd_config'
	if os.path.exists(CONFFILE):
		patch = {}
		patch['filemod'] = "644"
		patch['precheck_deny'] = "ossxp_config_begin"
		patch['stamp_before'] = "##### ossxp_config_begin #####"
		patch['stamp_end']    = "##### ossxp_config_end #####"
		patch['append']    = '''
## Only allow login if users belong to these groups.
## User shouldn't be in both groups, or user can not login using ssh.
## Person in sftp group can only use chroot sftp service.
AllowGroups ssh sftp

## People belong to sftp group, can not access ssh, only provide sftp service
## People in this sftp group, can have a invaild shell: /bin/false,
## and user homedir must owned by root user.
Match group sftp
    ChrootDirectory  %h
    X11Forwarding no
    AllowTcpForwarding no
    ForceCommand internal-sftp
## END OF File or another Match conditional block
'''
		#patch['trans_from'] = ['Protocol 2', 'PermitRootLogin no', 'PermitRootLogin no', 'UsePrivilegeSeparation yes']
		#patch['trans_to']   = ['Protocol 2', 'PermitRootLogin no', 'PermitRootLogin no', 'UsePrivilegeSeparation yes']
		apt.config_file_append(CONFFILE, patch)	

		## Add group ssh if not exist
		add_me_to_group("ssh")

	#------------------------------------------------------------
	CONFFILE='/etc/ssh/ssh_config'
	if os.path.exists(CONFFILE):
		patch = {}
		patch['filemod'] = "644"
		patch['precheck_deny'] = "ossxp_config_begin"
		patch['stamp_before'] = "##### ossxp_config_begin #####"
		patch['stamp_end']    = "##### ossxp_config_end #####"
		patch['append']    = '''
Host *
    CheckHostIP no
    ForwardX11 yes
    HashKnownHosts no
    StrictHostKeyChecking no
'''
		apt.config_file_append(CONFFILE, patch)	

	#------------------------------------------------------------
	CONFFILE='/etc/screenrc'
	if os.path.exists(CONFFILE):
		patch = {}
		patch['filemod'] = "644"
		patch['precheck_deny'] = "caption always"
		patch['stamp_before'] = "##### ossxp_config_begin #####"
		patch['stamp_end']    = "##### ossxp_config_end #####"
		patch['append']    = '''
## Install package 'screen-profiles*' or 'byotu' for lovely screen profiles
#defscrollback 3000
#vbell on
#startup_message off
## Set the caption on the bottom line
caption always "%{= kw}%-Lw%{= BW}%n %t%{-}%+w %-= @%H - %Y/%m/%d, %C"
'''
		apt.config_file_append(CONFFILE, patch)	

	if os.path.isfile('/usr/bin/byobu-config'):
		os.system('/usr/bin/byobu-config')
		print "Run byobu instead of screen for the first time."
	elif os.path.isfile('/usr/bin/screen-profiles'):
		os.system('/usr/bin/screen-profiles')

	#------------------------------------------------------------
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

	#------------------------------------------------------------
	if not os.path.exists('/dev/loop63'):
		for i in range(8,64):
			if os.path.exists('/dev/loop%d' % i):
				continue
			cmd = "mknod -m 660 /dev/loop%d b 7 %d" % (i, i)
			os.system(cmd)
			cmd = "chown root.disk /dev/loop%d" % i
			os.system(cmd)

	#------------------------------------------------------------
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

	#------------------------------------------------------------
	dist = os.popen("lsb_release -i").read().strip().lower()
	if dist.endswith('ubuntu'):
		for locale in [ 'zh_CN', 'zh_CN.GBK', 'zh_CN.UTF-8', 'zh_TW', 'en_US', 'en_US.UTF-8' ]:
			os.system("locale-gen %s" % locale)
	elif dist.endswith('debian'):
			os.system("dpkg-reconfigure locales || true")

	#------------------------------------------------------------
	if os.path.isfile('/usr/bin/git'):
		## aliases
		os.system("git config --system alias.st status")
		os.system("git config --system alias.ci commit")
		os.system("git config --system alias.co checkout")
		os.system("git config --system alias.br branch")
		## ui.color
		os.system('git config --system color.ui "auto"')


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
