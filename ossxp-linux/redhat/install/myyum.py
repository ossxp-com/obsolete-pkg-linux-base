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
import re
import unittest
import yum
sys.path.append('/usr/share/yum-cli')
import cli
import yummain


VERSION_EQUAL=0
VERSION_DIFF=1
VERSION_UNKNOWN=2
VERSION_NOTINST=3
verbose=1

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
    package_list = ""
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
        if package_list == '':
            package_list = item
        else:
            package_list = "%s, %s" % (package_list, item)

    if install:
        process_packages(package_list, install_mode=1, interactive=interactive, dryrun=dryrun)
    else:
        process_packages(package_list, install_mode=0, interactive=interactive, dryrun=dryrun)

alike_pkgs = (
    ( 'exim4-daemon-light', 'exim4-daemon-heavy', 'exim4-daemon-custom', ),
    ( 'apache2', 'ossxp-apache2-mpm-worker', 'ossxp-apache2-mpm-prefork', 'apache2-mpm-worker', 'apache2-mpm-prefork', )
    )


def get_list(cmd):
    package_list=""
    policy = os.popen(cmd, 'r')
    while 1:
        line=policy.readline()
        if not line:
            break
        line=line.strip()
        if package_list == '':
            package_list = line
        else:
            package_list = "%s, %s" % (package_list, line)
    return package_list

def get_pkg_status(pkg):
    return myb.get_pkg_status(pkg)

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

def pre_check(pset_list):
    """
    pset_list = "pset, pkg pkg | pkg, pset"
    pset      = "pkg1 pkg2 | pkg3 | pkg4"
    pgroup    = "pkg [pkg ...]"
    """
    uptodate_list=[]
    upgrade_list=[]
    notinst_list=[]
    unknown_list=[]
    for pset in pset_list.split(','):
        pset = pset.strip()
        if len(pset) == 0:
            continue
        # pkg_a | pkg_b means install one of them
        has_installed = False
        pset_notinst_list = []
        for pgroup in pset.split('|'):
            num_of_uninstalled = len(pset_notinst_list)
            for pkg in pgroup.split():
                pkg = pkg.strip()
                if pkg.startswith("not_installed_"):
                    status = VERSION_NOTINST
                elif pkg.startswith("current_installed_"):
                    status = VERSION_EQUAL
                elif pkg.startswith("outofdate_installed_"):
                    status = VERSION_DIFF
                elif pkg.startswith("cannot_installed_"):
                    status = VERSION_UNKNOWN
                else:
                    pkg, status = check_package(pkg) 

                # test if pkg is uptodate
                if status == VERSION_EQUAL:
                    uptodate_list.append(pkg)
                    has_installed = True
                elif status == VERSION_DIFF:
                    upgrade_list.append(pkg)
                    has_installed = True
                elif status == VERSION_NOTINST:
                    if num_of_uninstalled == 0:
                        pset_notinst_list.append(pkg)
                else:
                    unknown_list.append(pkg)
        if not has_installed and pset_notinst_list:
            notinst_list.extend( pset_notinst_list )

    vprint ("unknown_list: %s" % unknown_list)
    vprint ("upgrade_list: %s" % upgrade_list)
    vprint ("uptodate_list: %s" % uptodate_list)
    vprint ("notinst_list: %s" % notinst_list)
    r = {   VERSION_EQUAL: uptodate_list,
        VERSION_DIFF: upgrade_list,
        VERSION_UNKNOWN: unknown_list,
        VERSION_NOTINST: notinst_list }
    return r

def hack_config_file(conffile, options, must_exists=True):
    def lines_match(lines, needle, begin=None):
        found = False
        lineno = begin and int(begin) or 0
        for line in lines[lineno:]:
            if hasattr( needle, 'search'):
                if needle.search( line ):
                    found = True
                    break
            else:
                if needle in line:
                    found = True
                    break
            lineno += 1

        if found:
            return lineno
        else:
            return None


    def insert_at(lines, after=None, before=None):
        lineno = None
        if after:
            if not isinstance( after, (list, dict) ):
                after = [ after ]
            lineno_after = None
            for needle in after:
                lineno_after = lines_match(lines, needle)
                if lineno_after is not None:
                    lineno_after += 1
                    break
            lineno = lineno_after

        if before:
            if not isinstance( before, (list, dict) ):
                before = [ before ]
            lineno_before = None
            for needle in before:
                lineno_before = lines_match(lines, needle, begin=lineno)
                if lineno_before is not None:
                    break
            lineno = lineno_before
        return lineno

    if must_exists and not os.path.exists(conffile):
        print "[1m%s not exists, hacked FAILED![0m" % conffile
        return 1

    if not options:
        print "[1m%s not hacked, because nothing I can do![0m" % conffile
        return 0

    lines = open(conffile).read().splitlines()

    for item in options:
        key = item[0]
        opt = item[1]

        must_not  = opt.get('must-not')
        must_have = opt.get('must-have')
        after     = opt.get('after')
        before    = opt.get('before')

        if must_not and lines_match(lines, must_not) is not None:
            continue
        if must_have and not lines_match(lines, must_have) is None:
            continue

        if key == 'add':
            lineno = insert_at(lines, after=after, before=before)
            if opt.get('contents'):
                if lineno is None:
                    lines.append( opt.get('contents') )
                else:
                    lines.insert( lineno, opt.get('contents') )

    fd, tmpfile = tempfile.mkstemp(suffix=".tmp", text=True)
    os.write(fd, "\n".join(lines) + "\n")
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
                # set orignal owner and permission
                os.system( "chown --reference %s %s" % (conffile, tmpfile) )
                os.system( "chmod --reference %s %s" % (conffile, tmpfile) )
                shutil.move(tmpfile, conffile)
                vprint ("[1m%s modified successful.[0m" % conffile)
                break
    else:
        print "[1m%s already hacked, not touched.[0m" % conffile

def process_packages(package_list, install_mode=1, interactive=1, dryrun=1):
    myb.process_packages(package_list,install_mode,interactive,dryrun)

def main(argv=None):
    if argv is None:
        argv = sys.argv
    run(argv[1:])

class MyTestCase (unittest.TestCase):
    def _testPreCheck(self):
        pkglist = ""
        r = pre_check(pkglist)
        self.assertEqual(r[VERSION_EQUAL], [], "current... for: " + pkglist)
        self.assertEqual(r[VERSION_UNKNOWN], [], "cannot... for: " + pkglist)
        self.assertEqual(r[VERSION_DIFF], [], "outofdate... for: " + pkglist)
        self.assertEqual(r[VERSION_NOTINST], [], "not... for: " + pkglist) 

        pkglist = "cannot_installed_a | cannot_installed_b"
        r = pre_check(pkglist)
        self.assertEqual(r[VERSION_EQUAL], [], "current... for: " + pkglist)
        self.assertEqual(r[VERSION_UNKNOWN], ["cannot_installed_a", "cannot_installed_b"], "cannot... for: " + pkglist)
        self.assertEqual(r[VERSION_DIFF], [], "outofdate... for: " + pkglist)
        self.assertEqual(r[VERSION_NOTINST], [], "not... for: " + pkglist) 

        pkglist = "outofdate_installed_a | cannot_installed_b"
        r = pre_check(pkglist)
        self.assertEqual(r[VERSION_EQUAL], [], "current... for: " + pkglist)
        self.assertEqual(r[VERSION_DIFF], ["outofdate_installed_a"], "outofdate... for: " + pkglist)
        self.assertEqual(r[VERSION_UNKNOWN], ["cannot_installed_b"], "cannot... for: " + pkglist)
        self.assertEqual(r[VERSION_NOTINST], [], "not... for: " + pkglist) 

        pkglist = "cannot_installed_b | outofdate_installed_a"
        r = pre_check(pkglist)
        self.assertEqual(r[VERSION_EQUAL], [], "current... for: " + pkglist)
        self.assertEqual(r[VERSION_DIFF], ["outofdate_installed_a"], "outofdate... for: " + pkglist)
        self.assertEqual(r[VERSION_UNKNOWN], ["cannot_installed_b"], "cannot... for: " + pkglist)
        self.assertEqual(r[VERSION_NOTINST], [], "not... for: " + pkglist) 

        pkglist = "outofdate_installed_a | not_installed_b"
        r = pre_check(pkglist)
        self.assertEqual(r[VERSION_EQUAL], [], "current... for: " + pkglist)
        self.assertEqual(r[VERSION_DIFF], ["outofdate_installed_a"], "outofdate... for: " + pkglist)
        self.assertEqual(r[VERSION_UNKNOWN], [], "cannot... for: " + pkglist)
        self.assertEqual(r[VERSION_NOTINST], [], "not... for: " + pkglist) 

        pkglist = "not_installed_b | outofdate_installed_a"
        r = pre_check(pkglist)
        self.assertEqual(r[VERSION_EQUAL], [], "current... for: " + pkglist)
        self.assertEqual(r[VERSION_DIFF], ["outofdate_installed_a"], "outofdate... for: " + pkglist)
        self.assertEqual(r[VERSION_UNKNOWN], [], "cannot... for: " + pkglist)
        self.assertEqual(r[VERSION_NOTINST], [], "not... for: " + pkglist) 

        pkglist = "outofdate_installed_a outofdate_installed_b not_installed_c not_installed_d | outofdate_installed_x | cannot_installed_x | not_installed_x | not_installed_y | current_installed_a"
        r = pre_check(pkglist)
        self.assertEqual(r[VERSION_EQUAL], ["current_installed_a"], "current... for: " + pkglist + " is: " + ", ".join(r[VERSION_EQUAL]))
        self.assertEqual(r[VERSION_DIFF], ["outofdate_installed_a", "outofdate_installed_b", "outofdate_installed_x"], "outofdate... for: " + pkglist + " is: " + ", ".join(r[VERSION_DIFF]))
        self.assertEqual(r[VERSION_UNKNOWN], ["cannot_installed_x"], "cannot... for: " + pkglist + " is: " + ", ".join(r[VERSION_UNKNOWN]))
        self.assertEqual(r[VERSION_NOTINST], [], "not... for: " + pkglist + " is: " + ", ".join(r[VERSION_NOTINST])) 

        pkglist = "current_installed_a | outofdate_installed_a outofdate_installed_b not_installed_c not_installed_d | outofdate_installed_x | cannot_installed_x | not_installed_x | not_installed_y"
        r = pre_check(pkglist)
        self.assertEqual(r[VERSION_EQUAL], ["current_installed_a"], "current... for: " + pkglist + " is: " + ", ".join(r[VERSION_EQUAL]))
        self.assertEqual(r[VERSION_DIFF], ["outofdate_installed_a", "outofdate_installed_b", "outofdate_installed_x"], "outofdate... for: " + pkglist + " is: " + ", ".join(r[VERSION_DIFF]))
        self.assertEqual(r[VERSION_UNKNOWN], ["cannot_installed_x"], "cannot... for: " + pkglist + " is: " + ", ".join(r[VERSION_UNKNOWN]))
        self.assertEqual(r[VERSION_NOTINST], [], "not... for: " + pkglist + " is: " + ", ".join(r[VERSION_NOTINST])) 

        pkglist = "not_installed_a | current_installed_a | outofdate_installed_a outofdate_installed_b not_installed_c not_installed_d | outofdate_installed_x | cannot_installed_x | not_installed_x | not_installed_y"
        r = pre_check(pkglist)
        self.assertEqual(r[VERSION_EQUAL], ["current_installed_a"], "current... for: " + pkglist + " is: " + ", ".join(r[VERSION_EQUAL]))
        self.assertEqual(r[VERSION_DIFF], ["outofdate_installed_a", "outofdate_installed_b", "outofdate_installed_x"], "outofdate... for: " + pkglist + " is: " + ", ".join(r[VERSION_DIFF]))
        self.assertEqual(r[VERSION_UNKNOWN], ["cannot_installed_x"], "cannot... for: " + pkglist + " is: " + ", ".join(r[VERSION_UNKNOWN]))
        self.assertEqual(r[VERSION_NOTINST], [], "not... for: " + pkglist + " is: " + ", ".join(r[VERSION_NOTINST])) 

        pkglist = "cannot_installed_a | not_installed_a not_installed_b not_installed_c | cannot_installed_x | not_installed_x | not_installed_y"
        r = pre_check(pkglist)
        self.assertEqual(r[VERSION_EQUAL], [], "current... for: " + pkglist + " is: " + ", ".join(r[VERSION_EQUAL]))
        self.assertEqual(r[VERSION_DIFF], [], "outofdate... for: " + pkglist + " is: " + ", ".join(r[VERSION_DIFF]))
        self.assertEqual(r[VERSION_UNKNOWN], ["cannot_installed_a", "cannot_installed_x"], "cannot... for: " + pkglist + " is: " + ", ".join(r[VERSION_UNKNOWN]))
        self.assertEqual(r[VERSION_NOTINST], ["not_installed_a", "not_installed_b", "not_installed_c"], "not... for: " + pkglist + " is: " + ", ".join(r[VERSION_NOTINST])) 

        pkglist = "cannot_installed_a | not_installed_a not_installed_b not_installed_c | cannot_installed_x | not_installed_x | not_installed_y, not_installed_f, not_installed_g, current_installed_a"
        r = pre_check(pkglist)
        self.assertEqual(r[VERSION_EQUAL], ["current_installed_a"], "current... for: " + pkglist + " is: " + ", ".join(r[VERSION_EQUAL]))
        self.assertEqual(r[VERSION_DIFF], [], "outofdate... for: " + pkglist + " is: " + ", ".join(r[VERSION_DIFF]))
        self.assertEqual(r[VERSION_UNKNOWN], ["cannot_installed_a", "cannot_installed_x"], "cannot... for: " + pkglist + " is: " + ", ".join(r[VERSION_UNKNOWN]))
        self.assertEqual(r[VERSION_NOTINST], ["not_installed_a", "not_installed_b", "not_installed_c", "not_installed_f", "not_installed_g"], "not... for: " + pkglist + " is: " + ", ".join(r[VERSION_NOTINST])) 

    def _testHackConffile(self):
        conffile = "%s_unittest_%d" %( __file__, os.getpid())

        fp = open(conffile, 'w')
        fp.write("""
1. # Authentication
2. PermitRootLogin yes
3. 
4. this is end of orignal file.
""")
        fp.close()
        os.chmod(conffile, 0610)

        options = []
        options.append(
		    ('add', {'must-not': 'AllowGroups',
				 'contents': '''
AllowGroups ssh sftp
''',
		    		 'after': [ 'PermitRootLogin', '# Authentication' ],
		    		},
		    ) )

	options.append(
		('add', {'must-not': 'Match group sftp',
				 'contents': '''
Match group sftp
    ...
## END OF File or another Match conditional block
'''
				},
		) )

        hack_config_file( conffile, options )
        self.assert_( os.stat( conffile ).st_mode == 0100610, "file permission changed!" )
        hack_config_file( conffile, options )
        self.assert_( os.stat( conffile ).st_mode == 0100610, "file permission changed!" )

        fp = open(conffile, 'w')
        fp.write("""
1. PermitRootLogin yes
2. # Authentication
3. 
4. this is end of orignal file.
""")
        fp.close()
        os.chmod(conffile, 0600)

        hack_config_file( conffile, options )
        self.assert_( os.stat( conffile ).st_mode == 0100600, "file permission changed!" )

    def testyum(self):
        #MyYumBase()
        #ybc.provides(['yum'])
        #ybc.provides(['python'])
        #ybc.installPkgs(['libuser'])
        #myb.test()
        pass

    def _test_check_packages(self):
        pkg = "yum"
        pkg,status = check_package(pkg)
        self.assertEqual(VERSION_EQUAL, status, "current... for: " + pkg)

        pkg = "abc"
        pkg,status = check_package(pkg)
        self.assertEqual(VERSION_UNKNOWN, status, "current... for: " + pkg)

        pkg = "epel-release"
        pkg,status = check_package(pkg)
        self.assertEqual(VERSION_DIFF, status, "current... for: " + pkg)

        pkg = "etckeeper"
        pkg,status = check_package(pkg)
        self.assertEqual(VERSION_NOTINST, status, "current... for: " + pkg)

    def test_process_packages(self):
        interactive = 1
        dryrun = 0
        package_list = "weechat|abc, hello world|man,libuser"
        process_packages(package_list, install_mode=1, interactive=interactive, dryrun=dryrun)

class MyYumBase(cli.YumBaseCli):
    def __init__(self):
        cli.YumBaseCli.__init__(self)

    def test(self):
        #i=0
        #for pkg in self.rpmdb:
        #    print pkg.name + " " + pkg.description
        #    i += 1
        #print str(i) + " packages"
        #self.rpmdb.getPkgList()
        #searchPackageProvides()
        #searchGenerator(searchlist,args)
        #searchPackages()
        #self.remove(po)

        searchlist = ['name']
        args = ["libuser" ]
        matching = self.searchGenerator(searchlist, args)
        for (po, matched_value) in matching:
            print po.name + " " + po.description
            if po.name == 'libuser':
                self.install(po)
        self.buildTransaction()
        self.processTransaction()

    def get_pkg_list(self,pset_list):
        pkg_list = []
        for pset in pset_list.split(','):
            pset = pset.strip()
            if len(pset) == 0:
                continue
            # pkg_a | pkg_b means install one of them
            has_installed = False
            for pgroup in pset.split('|'):
                tmp_list = [ pkg.strip() for pkg in pgroup.split() ]
                pkg_list.extend(tmp_list)
        return pkg_list

    def divide_package(self,pkg_list):
        pl = self.doPackageLists(pkgnarrow='all',patterns=pkg_list)
        print [ pkg.name for pkg in pl.reinstall_available ]
        print [ pkg.name for pkg in  pl.old_available ]
        print [ pkg.name for pkg in pl.obsoletesTuples ]
        print [ pkg.name for pkg in pl.recent ]
        print [ pkg.name for pkg in pl.extras ]

        uptodate_list = []
        upgrade_list = []
        #[ upgrade_list.append(pkg.name) if pkg in pl.available for pkg in pl.installed else uptodate_list.append(pkg.name) ]
        notinst_list = [ pkg.name for pkg in pl.available ]
        unknown_list = [ pkg.name for pkg in pl.obsoletes ]

        vprint ("unknown_list: %s" % unknown_list)
        vprint ("upgrade_list: %s" % upgrade_list)
        vprint ("uptodate_list: %s" % uptodate_list)
        vprint ("notinst_list: %s" % notinst_list)
        r = {   VERSION_EQUAL: uptodate_list,
            VERSION_DIFF: upgrade_list,
            VERSION_UNKNOWN: unknown_list,
            VERSION_NOTINST: notinst_list }
        return r

    def get_pkg_status(self,pkg):
        if self.rpmdb.installed(pkg):
            pl = self.doPackageLists('updates')
            exactmatch, matched, unmatched = yum.packages.parsePackages(pl.updates, [pkg])
            exactmatch = yum.misc.unique(exactmatch)
            if exactmatch:
                vprint ("Package %s should be upgrade." % pkg)
                return VERSION_DIFF
            else:
                vprint ("Package %s already installed." % pkg)
                return VERSION_EQUAL
        self.pl = self.doPackageLists('available')
        exactmatch, matched, unmatched = yum.packages.parsePackages(self.pl.available, [pkg])
        exactmatch = yum.misc.unique(exactmatch)
        if exactmatch:
            vprint ("Package %s has not yet installed!" % pkg)
            return VERSION_NOTINST
        else:
            vprint ("Package %s does not exist!" % pkg)
            return VERSION_UNKNOWN

    def process_packages(self,package_list, install_mode=1, interactive=1, dryrun=1):
        pkg_list = self.get_pkg_list(package_list)
        lists = self.divide_package(pkg_list)
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
                cmd = "yum install %s" % string.join(lists[VERSION_NOTINST] + lists[VERSION_DIFF], " ")
            else:
                cmd = "yum install -y %s" % string.join(lists[VERSION_NOTINST] + lists[VERSION_DIFF], " ")
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
                vprint ( "Installing these packages: %s" % cmd)
                pkg_list = lists[VERSION_NOTINST] + lists[VERSION_DIFF]
                self.installPkgs(pkg_list)
        else:
            vprint ( "Removing these packages: %s" % cmd)
            pkg_list = self.pl.available, lists[VERSION_EQUAL] + lists[VERSION_DIFF]
            self.erasePkgs(pkg_list)

        self.buildTransaction()
        #ybc.conf.setConfigOption('assumeyes',True)
        self.doTransaction()


myb = MyYumBase()

if __name__ == '__main__':
    unittest.main()

# vim: et ts=4 sw=4
