#!/usr/bin/python

import os, sys, re, string

VERSION_EQUAL=0
VERSION_DIFF=1
VERSION_UNKNOWN=2
VERSION_NOTINST=3

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
				found = 0
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

def install_packages(list, interactive=1, dryrun=0):
	lists = pre_check(list)
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

	if interactive:
		cmd = "apt-get install %s" % string.join(lists[VERSION_NOTINST] + lists[VERSION_DIFF], " ")
	else:
		#os.system("apt-get install --force-yes -y %" % )
		cmd = "apt-get install --force-yes -y %s" % string.join(lists[VERSION_NOTINST] + lists[VERSION_DIFF], " ")

	print "Will running: [1m%s[0m" % cmd
	if interactive:
		raw_input ("Press any key...")
	if not dryrun:
		pass
		#os.system(cmd)
		

def uninstall_packages(list, interactive=1, dryrun=0):
	lists = pre_check(list)
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

	if dryrun:
		cmd = "dpkg --dry-run --remove %s" % string.join(lists[VERSION_EQUAL] + lists[VERSION_DIFF], " ")
	else:
		cmd = "dpkg --remove %s" % string.join(lists[VERSION_EQUAL] + lists[VERSION_DIFF], " ")

	print "Will running: [1m%s[0m" % cmd
	if interactive:
		raw_input ("Press any key...")
	#os.system(cmd)
		

#print "%s return %s" % ('acl', check_package('acl'))
#print "%s return %s" % ('xxx', check_package('xxx'))
#print "%s return %s" % ('apache', check_package('apache2-mpm-prefork'))

#pre_check("a, b, c, d | e, acl, kde, hal, libhal-storage1, libhal1, exim4-daemon-light , gnome") 
install_packages ("a, b, c, d | e, acl, kde, hal, libhal-storage1, libhal1, exim4-daemon-light , gnome") 
uninstall_packages ("a, b, c, d | e, acl, libhal1, gnome") 
