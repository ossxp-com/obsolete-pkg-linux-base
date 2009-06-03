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
	dstat, ethtool, file, fpdns, fping, fuse-utils, 
	gnupg, htop, ia32-libs, ia32-libs-gtk, indent, iproute, 
	less, locales, lynx, ntfs-3g, ntpdate, nmap, ngrep, 
	openssl, p7zip-full, pciutils, perl, psmisc, preload, 
	rdiff-backup, rsync, rar, saidar, screen, coreutils | shellutils, ssh, star, sudo, sysstat, tcpdump, 
	memtester | sysutils, procinfo | sysutils, tofrodos | sysutils,
	udev, unison, vim, vnstat, wget, zhcon, 
	'''
############################################################


import myapt as apt
import os, sys, re, string, getopt, tempfile, shutil


interactive = 1
dryrun  = 0
verbose = 0
STAMPFILE = ".base.done"


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
		#patch['precheck_deny'] = "set completion-ignore-case on"
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
		#patch['precheck_deny'] = "set -o vi"
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
		patch['precheck_deny'] = "%wheel"
		patch['stamp_before'] = "##### ossxp_config_begin #####"
		patch['stamp_end']    = "##### ossxp_config_end #####"
		patch['append']    = '''
#%wheel		ALL = (ALL) ALL
%wheel		ALL = NOPASSWD: ALL

#User_Alias	FULLTIMERS = admin1,admin2
#FULLTIMERS	ALL = NOPASSWD: ALL
'''
		apt.config_file_append(CONFFILE, patch)	

	#------------------------------------------------------------
	CONFFILE='/etc/ssh/sshd_config'
	if os.path.exists(CONFFILE):
		patch = {}
		patch['filemod'] = "644"
		patch['precheck_deny'] = "AllowGroups wheel"
		patch['stamp_before'] = "##### ossxp_config_begin #####"
		patch['stamp_end']    = "##### ossxp_config_end #####"
		patch['append']    = '''
# Only allow login if users belong to these groups:
#AllowGroups wheel
'''
		patch['trans_from'] = ['Protocol 2', 'PermitRootLogin no', 'PermitRootLogin no', 'UsePrivilegeSeparation yes']
		patch['trans_to']   = ['Protocol 2', 'PermitRootLogin no', 'PermitRootLogin no', 'UsePrivilegeSeparation yes']
		apt.config_file_append(CONFFILE, patch)	


	#------------------------------------------------------------
	CONFFILE='/etc/screenrc'
	if os.path.exists(CONFFILE):
		patch = {}
		patch['filemod'] = "644"
		#patch['precheck_deny'] = "caption always"
		patch['stamp_before'] = "##### ossxp_config_begin #####"
		patch['stamp_end']    = "##### ossxp_config_end #####"
		patch['append']    = '''
#defscrollback 3000
#vbell on
#startup_message off

# Set the caption on the bottom line
caption always "%{= kw}%-Lw%{= BW}%n %t%{-}%+w %-= @%H - %Y/%m/%d, %C"
'''
		apt.config_file_append(CONFFILE, patch)	


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
	CONFFILE='/etc/apt/apt.conf.d/01defaultrelease'
	if os.path.exists(os.path.dirname(CONFFILE)) and not os.path.exists(CONFFILE):
		content = '''// APT::Default-Release "stable";\n// APT::Cache-Limit "141943904";\n'''
		file = open(CONFFILE, 'w')
		file.write(content)
		file.close()



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

			do_install()

			os.system('touch %s' % STAMPFILE)
		if arg in ('config'):
			do_config()


if __name__ == "__main__":
	sys.exit(main())

