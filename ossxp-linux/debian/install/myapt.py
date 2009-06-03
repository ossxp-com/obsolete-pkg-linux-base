#!/usr/bin/env python

'''PROGRAM INTRODUCTION

Usage: %(PROGRAM)s [options] [list]

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
    --install
        Install packages
    --remove
        Remove packages

list
    Comma seperated packages list
'''


import os, sys, re, string, getopt, tempfile, shutil


VERSION_EQUAL=0
VERSION_DIFF=1
VERSION_UNKNOWN=2
VERSION_NOTINST=3
verbose=0


def vprint(str):
	global verbose
	if verbose:
		print str


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
	global verbose
	interactive = 1
	dryrun = 0
	list = ""
	install = 1

	# if argv passed from sys.argv, argv[0] should pass to getopt
	if len(argv) == 1:
		argv=argv[0]

	try:
		opts, args = getopt.getopt(
			argv, "hivbnq", 
			["help", "verbose", "quiet", "install", "remove", "interactive", "batch", "dryrun"])
	except getopt.error, msg:
		return usage(1, msg)

	for opt, arg in opts:
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
		elif opt in ('--install'):
			install = 1
		elif opt in ('--remove'):
			install = 0

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

	if install:
		process_packages(list, install_mode=1, interactive=interactive, dryrun=dryrun)
	else:
		process_packages(list, install_mode=0, interactive=interactive, dryrun=dryrun)

alike_pkgs = (
	( 'exim4-daemon-light', 'exim4-daemon-heavy', 'exim4-daemon-custom', ),
	( 'apache2', 'ossxp-apache2-mpm-worker', 'ossxp-apache2-mpm-prefork', 'apache2-mpm-worker', 'apache2-mpm-prefork', )
	)


def get_list(cmd):
	list=""
	policy = os.popen(cmd, 'r')
	while 1:
		line=policy.readline()
		if not line:
			break
		line=line.strip()
		if list == '':
			list = line
		else:
			list = "%s, %s" % (list, line)
	return list


def get_pkg_status(pkg):
	policy = os.popen('LANG=C apt-cache policy %s 2>/dev/null' % pkg, 'r').read()
	if len(policy) == 0:
		vprint ("Package %s does not exist!" % pkg)
		return VERSION_UNKNOWN

	match=re.search('^[\s]*Installed:[\s]*(.*)$', policy, re.M)
	if match:
		inst_version = match.group(1)
	else:
		return VERSION_UNKNOWN
	
	match=re.search('^[\s]*Candidate:[\s]*(.*)$', policy, re.M)
	if match:
		cand_version = match.group(1)
	else:
		return VERSION_UNKNOWN

	if cand_version == '(none)':
		cand_version = None
		return VERSION_UNKNOWN

	if inst_version == '(none)':
		inst_version = None
		return VERSION_NOTINST

	if inst_version != cand_version:
		vprint ("Package %s should be upgrade." % pkg)
		return VERSION_DIFF
	else:
		vprint ("Package %s already installed." % pkg)
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
		item = item.strip()
		if len(item) == 0:
			continue
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

	vprint ("unknown_list: %s" % unknown_list)
	vprint ("upgrade_list: %s" % upgrade_list)
	vprint ("uptodate_list: %s" % uptodate_list)
	vprint ("notinst_list: %s" % notinst_list)
	r = {   VERSION_EQUAL: uptodate_list,
		VERSION_DIFF: upgrade_list,
		VERSION_UNKNOWN: unknown_list,
		VERSION_NOTINST: notinst_list }
	return r


def config_file_append(conffile, patch):
	if not os.path.exists(conffile):
		return 1
	if not patch.has_key('stamp_before') or not patch['stamp_before'] or not patch.has_key('stamp_end') or not patch['stamp_end']:
		return 2

	buff = open(conffile).read()

	if patch.has_key('precheck_deny') and patch['precheck_deny']:
		if re.match(patch['precheck_deny'], buff, re.DOTALL):
			vprint ("Match %s, not modify config file %s" % (patch['precheck_deny'], conffile) )
			return 0
	if patch.has_key('precheck_pass') and patch['precheck_pass']:
		if not re.match(patch['precheck_pass'], buff, re.DOTALL):
			vprint ("Not match %s, not modify config file %s" % (patch['precheck_deny'], conffile) )
			return 0

	p = re.compile('^(.*)%s.*%s(.*)$' % (patch['stamp_before'],patch['stamp_end']), re.DOTALL)
	m = p.match(buff)

	if m:
		vprint ("Find stamp_before and stamp_end in %s" % conffile)
		buff=m.group(1) + patch['stamp_before'] + patch['append'] + patch['stamp_end'] + m.group(2)
	else:
		vprint ("Not find stamp tag, append to file %s" % conffile)
		buff=buff + patch['stamp_before'] + patch['append'] + patch['stamp_end'] + '\n'
	
	fd, tmpfile = tempfile.mkstemp(suffix=".tmp", text=True)
	os.write(fd,buff)
	os.close(fd)
	diff=os.popen('diff -u %s %s' % (conffile, tmpfile)).read()
	if len(diff) > 0:
		print "[1m%s will be modified:[0m" % conffile
		print diff
		while 1:
			choice = raw_input('Change config file ? (y/n)')[:1]
			if choice in ['n', 'N']:
				os.unlink(tmpfile)
				vprint ("%s not modified." % conffile)
				break
			elif choice in ['y', 'Y']:
				shutil.move(tmpfile, conffile)
				if patch.has_key('filemod') and patch['filemod']:
					os.chmod( conffile, int(patch['filemod'],8) )
					vprint ("change filemode to %d" % int(patch['filemod']) )
				else:
					os.chmod( conffile, 0644 )
					vprint ("change filemode to 0664")

				vprint ("[1m%s modified successful.[0m" % conffile)
				break


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
			print "No packages will be installed."
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
			cmd = "apt-get install --force-yes -y %s" % string.join(lists[VERSION_NOTINST] + lists[VERSION_DIFF], " ")
	else:
		if dryrun:
			cmd = "dpkg --dry-run --remove %s" % string.join(lists[VERSION_EQUAL] + lists[VERSION_DIFF], " ")
		else:
			cmd = "dpkg --remove %s" % string.join(lists[VERSION_EQUAL] + lists[VERSION_DIFF], " ")


	print "Will running: [1m%s[0m" % cmd
	if interactive:
		raw_input ("Press any key...")
	print "install_mod: %d, dryrun:%d" % (install_mode, dryrun)
	if install_mode:
		if not dryrun:
			vprint ( "Running: %s" % cmd)
			os.system(cmd)
	else:
		vprint ( "Running: %s" % cmd)
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

