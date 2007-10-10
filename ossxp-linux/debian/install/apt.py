#!/usr/bin/env python

'''PROGRAM INTRODUCTION

Usage: %(PROGRAM)s [options]

Options:

    -h|--help
        Print this message and exit.
    -i|--interactive
        Run in interactive mode
    -b|--batch
        Run in batch mode
    -n|--dryrun
        Dryrun mode: acturally, do not run
'''


import os, sys, re, string, getopt


VERSION_EQUAL=0
VERSION_DIFF=1
VERSION_UNKNOWN=2
VERSION_NOTINST=3


def usage(code, msg=''):
	if code:
		fd = sys.stderr
	else:
		fd = sys.stdout
	print >> fd, __doc__
	if msg:
		print >> fd, msg
	sys.exit(code)

def run(*argv):
	interactive = 1
	dryrun = 1
	list = ""
	install = 1

	# if argv passed from sys.argv, argv[0] should pass to getopt
	if len(argv) == 1:
		argv=argv[0]

	try:
		opts, args = getopt.getopt(
			argv, "hiIbn", 
			["help", "install", "remove", "interactive", "batch", "no-interactive", "dryrun"])
	except getopt.error, msg:
		return usage(1, msg)

	for opt, arg in opts:
		if opt in ('-h', '--help'):
			return usage(0)
		elif opt in ('-i', '--interactive'):
			interactive = 1
		elif opt in ('-I', '-b', '--batch', '--no-interactive'):
			interactive = 0
		elif opt in ('-n', '--dryrun'):
			dryrun = 1
		elif opt in ('--install'):
			install = 1
		elif opt in ('--remove'):
			install = 0
	print "interactive: %d" % interactive
	print "dryrun: %d" % dryrun

	if len(args) == 0:
		return usage(1)

	for item in args:
		if item == '-':
			item = ''
			while 1:
				try:
					line = raw_input()
					if item == '':
						item = line
					else:
						item = "%s, %s" % (item, line)
				except EOFError:
					break
		if list == '':
			list = item
		else:
			list = "%s, %s" % (list, item)

	print "list is : %s" % list
	if install:
		process_packages(list, install_mode=1, interactive=interactive, dryrun=dryrun)
	else:
		process_packages(list, install_mode=0, interactive=interactive, dryrun=dryrun)

alike_pkgs = (
	( 'exim4-daemon-light', 'exim4-daemon-heavy', 'exim4-daemon-custom', ),
	( 'apache2', 'ossxp-apache2-mpm-worker', 'ossxp-apache2-mpm-prefork', 'apache2-mpm-worker', 'apache2-mpm-prefork', )
	)


def get_pkg_status(pkg):
	policy = os.popen('LANG=C apt-cache policy %s 2>/dev/null' % pkg, 'r').read()
	if len(policy) == 0:
		print "Package %s does not exist!" % pkg    
		return VERSION_UNKNOWN

	match=re.search('^[\s]*Installed:[\s]*(.*)$', policy, re.M)
	if match:
		inst_version = match.group(1)
		if inst_version == '(none)':
			inst_version = None
			return VERSION_NOTINST
	else:
		return VERSION_UNKNOWN
		

	match=re.search('^[\s]*Candidate:[\s]*(.*)$', policy, re.M)
	if match:
		cand_version = match.group(1)
		if cand_version == '(none)':
			cand_version = None
			return VERSION_UNKNOWN
	else:
		return VERSION_UNKNOWN


	if inst_version != cand_version:
		print "Package %s should be upgrade." % pkg    
		return VERSION_DIFF
	else:
		print "Package %s already installed." % pkg    
		return VERSION_EQUAL

def check_package(pkg):
	pkg = pkg.strip()
	for items in alike_pkgs:
		if pkg in items:
			for item in items:
				status = get_pkg_status(item) 
				if status == VERSION_EQUAL or status == VERSION_DIFF:
					return (item, status)
	status = get_pkg_status(pkg)
	return (pkg,status)


def pre_check(packages):
	list = packages.split(',')
	uptodate_list=[]
	upgrade_list=[]
	notinst_list=[]
	unknown_list=[]
	for item in list:
		# pkg_a | pkg_b means install one of them
		split = item.split('|')
		if len(split) > 1:
			found = 0
			for pkg in split:
				pkg, status = check_package(pkg) 
				# test if pkg is uptodate
				if status == VERSION_EQUAL:
					uptodate_list.append(pkg)
					found = 1
					break
				elif status == VERSION_DIFF:
					upgrade_list.append(pkg)
					found = 1
					break
			if found:
				continue

		pkg = split[0]
		pkg, status = check_package(pkg) 
		if status == VERSION_EQUAL:
			uptodate_list.append(pkg)
		elif status == VERSION_DIFF:
			upgrade_list.append(pkg)
		elif status == VERSION_NOTINST:
			notinst_list.append(pkg)
		else:
			unknown_list.append(pkg)

	print "unknown_list: %s" % unknown_list
	print "upgrade_list: %s" % upgrade_list
	print "uptodate_list: %s" % uptodate_list
	print "notinst_list: %s" % notinst_list
	r = {   VERSION_EQUAL: uptodate_list,
		VERSION_DIFF: upgrade_list,
		VERSION_UNKNOWN: unknown_list,
		VERSION_NOTINST: notinst_list }
	return r

def process_packages(list, install_mode=1, interactive=1, dryrun=1):
	lists = pre_check(list)
	if install_mode:
		if lists[VERSION_UNKNOWN]:
			print "These packages are not found for this distrabution:"
			print lists[VERSION_UNKNOWN]
		if lists[VERSION_EQUAL]:
			print "Already installed packages:"
			print lists[VERSION_EQUAL]
		if lists[VERSION_NOTINST]:
			print "[1mThese packages will be installed as new:[0m"
			print lists[VERSION_NOTINST]
		if lists[VERSION_DIFF]:
			print "[1mThese packages will be upgrade:[0m"
			print lists[VERSION_DIFF]

		if not lists[VERSION_NOTINST] and not lists[VERSION_DIFF]:
			print "No packages will be install."
			return
	else:
		if lists[VERSION_UNKNOWN]:
			print "These packages are not found for this distrabution:"
			print lists[VERSION_UNKNOWN]
		if lists[VERSION_NOTINST]:
			print "[1mThese packages not installed yet:[0m"
			print lists[VERSION_NOTINST]
		if lists[VERSION_EQUAL] or lists[VERSION_DIFF]:
			print "These packages will be REMOVED!!!:"
			print lists[VERSION_EQUAL]
			print lists[VERSION_DIFF]

		if not lists[VERSION_EQUAL] and not lists[VERSION_DIFF]:
			print "No packages will be removed."
			return

	if install_mode:
		if interactive:
			cmd = "apt-get install %s" % string.join(lists[VERSION_NOTINST] + lists[VERSION_DIFF], " ")
		else:
			#os.system("apt-get install --force-yes -y %" % )
			cmd = "apt-get install --force-yes -y %s" % string.join(lists[VERSION_NOTINST] + lists[VERSION_DIFF], " ")
	else:
		if dryrun:
			cmd = "dpkg --dry-run --remove %s" % string.join(lists[VERSION_EQUAL] + lists[VERSION_DIFF], " ")
		else:
			cmd = "dpkg --remove %s" % string.join(lists[VERSION_EQUAL] + lists[VERSION_DIFF], " ")


	print "Will running: [1m%s[0m" % cmd
	if interactive:
		raw_input ("Press any key...")

	if install_mode:
		if not dryrun:
			pass
			os.system(cmd)
	else:
		os.system(cmd)
		

def main(argv=None):
	if argv is None:
		argv = sys.argv
	run(argv[1:])

if __name__ == "__main__":
	#pre_check("a, b, c, d | e, acl, kde, hal, libhal-storage1, libhal1, exim4-daemon-light , gnome") 

	#process_packages ("a, b, c, d | e, acl, kde, hal, libhal-storage1, libhal1, exim4-daemon-light , gnome") 
	#process_packages ("a, b, c, d | e, acl, libhal1, gnome", '--remove') 

	sys.exit(main())

