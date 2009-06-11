#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright 2009, by Jiang Xin at OpenSourceXpress co. ltd. 
Contact: <worldhello.net AT gmail.com>

Usage:
    %(PACKAGENAME)s options... list
    %(PACKAGENAME)s options... list_macros
    %(PACKAGENAME)s options... update_config_files

options:
    -n:
    --dryrun:
        Dryrun mode.

    --package name:
    -p name:
        Set package name

    --type 
    -t ip|host|email|name|password|others:
        Config file type.
"""

import os, sys
import getopt
import re

MACROS_FILE = '/etc/ossxp/packages/macros'
PACKAGE_LIB_DIR = '/opt/ossxp/lib/packages'
PATTERN_MACRONAME = re.compile(r'\(\?P<([^>]+)>.*?\)')
VALID_RECORD_TYPE = ('ip', 'host', 'email', 'name', 'password', 'others')


class ConfigFile(object):
    def __init__(self, name):
        self.name = name.strip()
        self.desc = ''
        self.types = []
        self.regex = []
        self.pattern = []

    def add_regex(self,regex):
        regex = regex.strip()
        if not regex or regex in self.regex:
            return
        self.regex.append(regex)
        self.pattern.append(re.compile(regex, re.I))

    def __str__(self):
        return self.name


class Packages(object):
    packages = {}
    _pre_defined_macros = {}
    _reference_macros = set([])


    def __init__(self, name = PACKAGE_LIB_DIR):
        if os.path.isdir(name):
            self.walk_dir(name)
        elif os.path.isfile(name):
            packagename = os.path.basename(name).rsplit('.',1)[0]
            self.packages[packagename] = self.parse_file(name)
        else:
            filename = os.path.join(PACKAGE_LIB_DIR, name) + '.conf'
            if not os.path.isfile(filename):
                raise Exception('config file for package %s does not exist!' % name)
            self.packages[name] =  self.parse_file(filename)
            print filename

    def parse_file(self, filename):
        if not os.path.isfile(filename):
            return None

        configs = []
        config  = None
        has_regex = False
        fp = open(filename)

        while True:
            line = fp.readline()
            if line == '':
                break
            if line.strip()=='' or line.strip()[0] == '#':
                continue

            if line.startswith('file:'):
                if config:
                    configs.append(config)
                config = ConfigFile(line[5:])
                has_regex = False

            if line.startswith('type:'):
                types = line[5:].split(',')
                for config_type in types:
                    config_type = config_type.strip()
                    if config_type not in VALID_RECORD_TYPE:
                        raise Exception('Unknown type: %s' % config_type)
                    config.types.append(config_type)

            if line.startswith('desc:'):
                config.desc = line[5:].strip()

            if line.startswith('regex:'):
                has_regex = True
                # regex: may follow a regex 
                line = ' '+line[5:]

            if has_regex and (line[0] == ' ' or line[0] == '\t'):
                config.add_regex(line.strip())

        if config:
            configs.append(config)

        return configs

    def walk_dir(self, path):
        packages = {}
        def _parse_dir(packages, dirname, fnames):
            for i in range(len(fnames)-1,-1,-1):
                if not fnames[i].endswith('.conf'):
                    del fnames[i]
            for i in fnames:
                pkg_name = i.rsplit('.',1)[0]
                packages[pkg_name] = self.parse_file(os.path.join(dirname, i))

        os.path.walk(path, _parse_dir, packages)
        self.packages = packages

    def get_config_obj_by_type(self, config_type=None):
        objs = []
        if config_type:
            config_type = config_type.strip().lower()
        for val in self.packages.values():
            for obj in val:
                if config_type and config_type not in obj.types:
                    continue
                objs.append(obj)
        return objs 

    def get_config_file_by_type(self, config_type=None):
        return map(lambda x:x.name, self.get_config_obj_by_type(config_type))

    def get_pre_defined_macros(self, filename=MACROS_FILE):
        if not os.path.isfile(filename):
            self._pre_defined_macros = {}
            return self._pre_defined_macros
        if self._pre_defined_macros:
            return self._pre_defined_macros
        fp = open(filename)
        for line in fp.readlines():
            line = line.strip()
            if not line or line[0]=='#':
                continue
            key, value = line.split(':',1)
            self._pre_defined_macros[key.strip()] = value.strip()
        return self._pre_defined_macros

    def get_reference_macros(self):
        if self._reference_macros:
            return self._reference_macros
        for val in self.packages.values():
            for obj in val:
                if not obj.regex:
                    continue
                for regex in obj.regex:
                    self._reference_macros |= set(PATTERN_MACRONAME.findall(regex))
        return self._reference_macros

    pre_defined_macros = property(get_pre_defined_macros)
    reference_macros = property(get_reference_macros)

    def _update_precheck(self):
        not_defined_macros = self.reference_macros - set(self.pre_defined_macros.keys())
        if not_defined_macros:
            raise Exception("Macros not defined in file %s:\n%s" % 
                (MACROS_FILE, '\n'.join(not_defined_macros)))
        for k,v in self.pre_defined_macros.items():
            if not v:
                raise Exception("You have not defined a value for macro '%s'!" % k)
       
    def _save_file(self, filename, contents):
        import difflib
        fp = open(filename, 'r')
        old = fp.read()
        fp.close()
        for line in difflib.unified_diff(old.splitlines(), contents.splitlines(), 'old %s' % filename , 'new %s' % filename, lineterm=''):
            print line
        selection = ''
        while selection not in ['y','n']:
            prompt = "Overwrite file: %s? (y/n)"
            if opt_dryrun:
                prompt += " *dryrun*" 
            selection = raw_input(prompt % filename).lower()
        if selection == 'n':
            print "ignored."
            print
            return
        if not opt_dryrun:
            fp = open(filename, 'w')
            fp.write(contents)
            fp.close()
        print "saved %s." % filename
        print

    def update(self):
        self._update_precheck()
        for key, val in self.packages.items():
            for obj in val:
                if not obj.pattern:
                    if obj.desc:
                        print >> sys.stderr, "%s\n\t<< %s (%s)" % (obj.name, obj.desc, key)
                    else:
                        print >> sys.stderr, "%s\n\t<< No pattern defined for this file in '%s'. Manual edit it please!" % (obj.name, key)
                    continue
                filename = obj.name
                if not os.path.isfile(filename):
                    print >> sys.stderr, "File '%s' not exist!" % filename
                fp = open(filename)
                contents=""
                save = False
                for line in fp.readlines():
                    for idx in range(len(obj.pattern)):
                        m = obj.pattern[idx].search(line)
                        if not m:
                            continue
                        if opt_debug:
                            print "pattern '%s' matched line '%s'" % (obj.regex[idx], line)
                        for macro in PATTERN_MACRONAME.findall(obj.regex[idx]):
                            if m.group(macro):
                                if line.count(m.group(macro)) > 1:
                                    print >> sys.stderr, "Find multiple '%s' for macro '%s' in line: %s" % \
                                        (m.group(macro), macro, line)
                                    continue
                                if m.group(macro) != self.pre_defined_macros[macro]:
                                    line = line.replace(m.group(macro), self.pre_defined_macros[macro])
                                    save = True
                            else:
                                print >> sys.stderr, "'%s' in re.match is blank, line: %s" % (macro, line)
                    contents += line
                fp.close()
                if save:
                    self._save_file(filename, contents)

def usage(code, msg=''):
    if code:
        fd = sys.stderr
    else:
        fd = sys.stdout
    print >> fd, __doc__
    if msg:
        print >> fd, msg
    sys.exit(code)

def main(argv=None):
    global opt_type, opt_package, opt_dryrun, opt_debug
    opt_type = ''
    opt_package = ''
    opt_dryrun = False
    opt_debug = False

    if argv is None:
        argv = sys.argv
    try:
        opts, args = getopt.getopt(
            argv[1:], "hvt:p:nd", 
            ["help", "verbose", "type=", "package=", "dryrun", "debug"])
    except getopt.error, msg:
         return usage(1, msg)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            return usage(0)
        elif opt in ('-t', '--type'):
            opt_type = arg.lower()
            if opt_type not in VALID_RECORD_TYPE:
                return usage(1, 'Unknown type: %s' % opt_type)
        elif opt in ('-p', '--package'):
            opt_package = arg
        elif opt in ('-n', '--dryrun'):
            opt_dryrun = True
        elif opt in ('-d', '--debug'):
            opt_debug = True
        else:
            return usage(1, 'Unknown option: %s' % opt)
        #elif opt in ('--more_options'):

    if not args:
        return usage(1)

    if opt_package:
        packages = Packages(opt_package)
    else:
        packages = Packages()

    for cmd in args:
        if cmd == 'list':
            config_files = packages.get_config_file_by_type(opt_type)
            print "\n".join(config_files)

        elif cmd in ['list_macros', 'macros']:
            not_defined_macros = packages.reference_macros - set(packages.pre_defined_macros.keys())
            print "# Pre defined macros in %s:" % MACROS_FILE
            print '\t',
            print '\n\t'.join(packages.pre_defined_macros)
            print 
            print "# Macros used in config filess:"
            print '\t',
            print '\n\t'.join(packages.reference_macros)
            if not_defined_macros:
                print "# Warning: macros not defined!!!"
                print '\t',
                print '\n\t'.join(not_defined_macros)

        elif cmd in ['update_config_files',]:
            packages.update()

if __name__ == "__main__":
    sys.exit(main())

# vim: et ts=4 sw=4
