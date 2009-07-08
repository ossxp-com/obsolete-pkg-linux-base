#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
%(COPYRIGHT)s
Contact: <worldhello.net AT gmail.com>

Usage:
    %(PACKAGENAME)s options... list
    %(PACKAGENAME)s options... list_macros
    %(PACKAGENAME)s options... list_backups
    %(PACKAGENAME)s options... extract_macros
    %(PACKAGENAME)s options... change_config_files

options:
    -n:
    --dryrun:
        Dryrun mode.

    --package name:
    -p name:
        Set package name

    --type 
    -t %(VALID_TYPES)s:
        Config file type.
"""

import os, sys
import getopt
import re

COPYRIGHT="Copyright 2009, by Jiang Xin at OpenSourceXpress co. ltd."
MACROS_FILE = '/etc/ossxp/packages/macros'
PACKAGE_LIBS = ['/opt/ossxp/lib/packages', '/etc/ossxp/packages',]
PATTERN_MACRO_IN_REGEX = re.compile(r'\(\?P<([^>]+)>.*?\)')
PATTERN_MACRO_IN_REPL = re.compile(r'\\g<([^>]+)>')
VALID_TYPES = ('ip', 'host', 'email', 'name', 'number', 'password', 'backup', 'others')
IGNORE_TYPES = ('backup', 'directory')
PREFIX_NO_MACRO = "_"

def _PRE_DEFINED_MACROS(filename=MACROS_FILE):
    macros = {}
    fp = open(filename)
    for line in fp.readlines():
        line = line.strip()
        if not line or line[0]=='#':
            continue
        key, value = line.split('=',1)
        macros[key.strip()] = value.strip()
    fp.close()
    return macros

MACROS = _PRE_DEFINED_MACROS()


class ConfigSection(object):

    def __init__(self, name):
        self.file_list = map(lambda x: x.strip(), name.split(','))
        self.desc = ''
        self.types = []
        self.regex = []
        self.regex_replacement = []
        self.regex_comment = []
        self.pattern = []

    def add_regex(self, pattern, replacement='', comment=''):
        pattern = pattern.strip()
        if not pattern:
            return
        if pattern in self.regex:
            raise Exception('pattern %s already declare in %s' % (pattern, self.file_list))
        self.regex.append(pattern)
        self.regex_replacement.append(replacement)
        self.regex_comment.append(comment)
        try:
            self.pattern.append(re.compile(pattern, re.I))
        except:
            if comment:
                raise Exception("Regex compile failed for %s, line: %s.\n" % (','.join(self.file_list), comment))
            else:
                raise Exception("Regex compile failed for %s, line: %s.\n" % (','.join(self.file_list), pattern))

    def __str__(self):
        return ', '.join(self.file_list)


class Package(object):

    def __init__(self, filename):
        self.filename = filename
        self.packagename = os.path.basename(filename).rsplit('.',1)[0]
        self.config_sections = []
        self.parse_file(filename)

    def __len__(self):
        return len(self.config_sections)

    def parse_file(self, filename):
        if not os.path.isfile(filename):
            return

        config  = None
        has_regex = False
        fp = open(filename)

        readline_already = False
        line=''
        lineno = 0
        while True:
            if not readline_already:
                line = fp.readline()
                lineno = lineno+1
            else:
                readline_already = False
            stripped = line.strip()
            if line == '':
                break
            if not stripped or stripped[0] == '#':
                continue

            if line.startswith('file:') or line.startswith('directory:'):
                has_regex = False
                if config:
                    self.config_sections.append(config)
                config = ConfigSection(line.split(':',1)[1])
                if line.startswith('directory:'):
                    config.types.append('directory')
                continue

            if line.startswith('type:'):
                has_regex = False
                types = line.split(':',1)[1].split(',')
                for config_type in types:
                    config_type = config_type.strip()
                    if config_type not in VALID_TYPES:
                        raise Exception('Unknown type: %s' % config_type)
                    config.types.append(config_type)
                continue

            if line.startswith('desc:'):
                has_regex = False
                config.desc = line.split(':',1)[1].strip()
                continue

            if line.startswith('regex:'):
                has_regex = True
                # regex: may follow a regex 
                line = line.split(':',1)[1]
                stripped = line.strip()
                if not stripped:
                    continue
                if line[0] not in ' \n':
                    line = ' ' + line

            if has_regex and line[0] in ' \t':
                if stripped and stripped[0] in "*":
                    left = line.split('*', 1)[0]
                    regex_comment = stripped[1:]
                    regex_pattern = ""
                    regex_replacement = ""
                    while True:
                        line = fp.readline()
                        lineno = lineno+1
                        stripped = line.strip()
                        if (# file end
                            line == '' or
                            # another section or new regex pattern begins
                            not line.startswith(left) or len(line) == len(left) or
                            # comment or blank line
                            not stripped or stripped[0] == '#' or
                            # another regex begins
                            line[len(left)] not in ' \t'):

                            config.add_regex(pattern=regex_pattern, replacement=regex_replacement, comment=regex_comment)
                            # do not bypass this line
                            readline_already = True
                            break
                        # other parameter for pattern:
                        else:
                            if stripped[0] == '*':
                                stripped = stripped[1:]
                                key, value = stripped.split(':',1)
                                params = []
                                if '(' in key:
                                    key, params = key.split('(',1)
                                    params=params.strip()[0:-1].strip()
                                    if ',' in params:
                                        params = [ item.strip() for item in params.split(',')]
                                    else:
                                        params = [ params.strip() ]
                                key = key.strip()
                                value = value.strip()

                                if key.strip() == 'match':
                                    regex_pattern = value.strip()
                                elif key.strip() == 'replacement':
                                    if params:
                                        if len(params)==1 or params[1].lower() in ('notnull', '1'):
                                            if MACROS.get(params[0]):
                                                regex_replacement = value.strip()
                                        elif len(params)==2 and params[1].lower() in ('null', '0'):
                                            if not MACROS.get(params[0]):
                                                regex_replacement = value.strip()
                                    else:
                                        regex_replacement = value.strip()
                                else:
                                    raise Exception('Unknown directive for regex: %d:%s.' % (lineno,line))
                else:
                    config.add_regex(stripped)
            else:
                raise Exception('Unknown directive: %d:%s.' % (lineno,line))

        if config:
            self.config_sections.append(config)

        fp.close()



class PackageGroups(object):

    def __init__(self, packages = PACKAGE_LIBS):
        self.packages = {}
        self._pre_defined_macros = {}
        self._reference_macros = set([])

        def initialize(name):
            if os.path.isdir(name):
                self.walk_dir(name)
            elif os.path.isfile(name):
                packagename = os.path.basename(name).rsplit('.',1)[0]
                self.packages[packagename] = Package(name)
            else:
                for dir in PACKAGE_LIBS:
                    filename = os.path.join(dir, name) + '.conf'
                    if os.path.isfile(filename):
                        break
                if not os.path.isfile(filename):
                    raise Exception('config file for package %s does not exist!' % name)
                self.packages[name] =  self.Package(filename)

        if isinstance(packages, basestring):
            packages = packages.split(",")
        if not isinstance(packages, (list,tuple)):
            raise Exception("packages should be list or tuple.")
        for pkg in packages:
            initialize(pkg)

    def walk_dir(self, path):
        packages = {}
        def _parse_dir(packages, dirname, fnames):
            for i in range(len(fnames)-1,-1,-1):
                if not fnames[i].endswith('.conf'):
                    del fnames[i]
            for i in fnames:
                pkg_name = i.rsplit('.',1)[0]
                packages[pkg_name] = Package(os.path.join(dirname, i))

        os.path.walk(path, _parse_dir, packages)
        for key, value in packages.iteritems():
            if key in self.packages:
                raise Exception('%s in %s already initialized in other location.' % (key, path))
            else:
                self.packages[key] = value

    def get_config_obj_by_type(self, config_type=None):
        objs = []
        if config_type:
            config_type = config_type.strip().lower()
        for package in self.packages.values():
            for config_section in package.config_sections:
                # Exclude config file/dir not in this config_type
                if config_type and config_type not in config_section.types:
                    continue
                # Ignore pure backup config file, or pure backup directory
                if not config_type and not ( set(config_section.types) - set(IGNORE_TYPES) ):
                    continue
                objs.append(config_section)
        return objs 

    def get_config_file_by_type(self, config_type=None):
        files = []
        for obj in self.get_config_obj_by_type(config_type):
            files.extend(obj.file_list)
        return set(files)

    def list_backups(self):
        files = []
        backups = []
        for obj in self.get_config_obj_by_type('backup'):
            files.extend(obj.file_list)
        for item in sorted(files):
            alreadyin = False
            for bak in backups:
                if item == bak or \
                   ( item.startswith(bak) and (bak[-1]=='/' or item[len(bak)]=='/') ):
                    alreadyin = True
                    break
            if not alreadyin:
                backups.append(item)

        print '\n'.join(backups)

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
            key, value = line.split('=',1)
            self._pre_defined_macros[key.strip()] = value.strip()
        return self._pre_defined_macros

    def get_reference_macros(self):
        if self._reference_macros:
            return self._reference_macros
        for package in self.packages.values():
            for config_section in package.config_sections:
                if not config_section.regex:
                    continue
                for regex in config_section.regex:
                    self._reference_macros |= set( filter(lambda x: not x.startswith(PREFIX_NO_MACRO), PATTERN_MACRO_IN_REGEX.findall(regex)) )
        return self._reference_macros

    pre_defined_macros = property(get_pre_defined_macros)
    reference_macros = property(get_reference_macros)

    def _macros_precheck(self):
        not_defined_macros = self.reference_macros - set(self.pre_defined_macros.keys())
        if not_defined_macros:
            print >> sys.stderr, "Warning: Macros not defined in file %s:\n%s" % \
                (MACROS_FILE, '\n'.join(not_defined_macros))
        for k,v in self.pre_defined_macros.items():
            if not v:
                print >> sys.stderr, "Warning: You have not defined a value for macro '%s'!" % k
       
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

    def extract_macros(self):
        macros = {}
        for package in self.packages.values():
            for config_section in package.config_sections:
                if not config_section.regex:
                    continue

                for filename in config_section.file_list:
                    if not os.path.isfile(filename):
                        print >> sys.stderr, "Warning: file '%s' not exist!" % filename
                        continue
                    fp = open(filename)
                    for line in fp.readlines():
                        for idx in range(len(config_section.pattern)):
                            m = config_section.pattern[idx].search(line)
                            if not m:
                                continue
                            if opt_debug:
                                print "pattern '%s' matched line '%s'" % (config_section.regex[idx], line)
                            for macro in PATTERN_MACRO_IN_REGEX.findall(config_section.regex[idx]):
                                if macro.startswith(PREFIX_NO_MACRO):
                                    continue
                                if m.group(macro):
                                    if line.count(m.group(macro)) > 1:
                                        print >> sys.stderr, "Warning: find multiple '%s' for macro '%s' in line: %s" % \
                                            (m.group(macro), macro, line)
                                    if macro in macros and m.group(macro):
                                        if not macros[macro]:
                                            macros[macro] = m.group(macro)
                                        elif macros[macro] and macros[macro] != m.group(macro):
                                            print >> sys.stderr, "Error: macro %s already set to %s! set to %s failed!" % \
                                                (macro, macros[macro], m.group(macro))
                                    elif macro not in macros:
                                        macros[macro] = m.group(macro)
                                else:
                                    if macro not in macros:
                                        macros[macro] = ''
                    fp.close()
        print "# Generated by %s.\n# %s" % (sys.argv[0], COPYRIGHT)
        print "# Format: macro = value"
        print '\n'.join( [ "%s = %s" % (k, v) for k, v in sorted(macros.iteritems()) ] )


    def change_config_files(self):
        self._macros_precheck()
        for package_file_name, package in self.packages.items():
            for config_section in package.config_sections:
                if not config_section.pattern:
                    if set(config_section.types) - set(IGNORE_TYPES):
                        if config_section.desc:
                            print >> sys.stderr, "Note: %s\n\t<< %s (%s)" % (','.join(config_section.file_list), config_section.desc, package_file_name)
                        else:
                            print >> sys.stderr, "Note: %s\n\t<< No pattern defined for this file in '%s'. Manual edit it please!" % (','.join(config_section.file_list), package_file_name)
                    continue
                for config_file_name in config_section.file_list:
                    if not os.path.isfile(config_file_name):
                        print >> sys.stderr, "Warning: file '%s' not exist!" % config_file_name
                        continue
                    fp = open(config_file_name)
                    contents=""
                    save = False
                    for line in fp.readlines():
                        lineending = ""
                        while line and line[-1] in "\r\n":
                            lineending = line[-1] + lineending
                            line = line[0:-1]

                        for idx in range(len(config_section.pattern)):
                            m = config_section.pattern[idx].search(line)
                            if not m:
                                continue
                            if opt_debug:
                                print "pattern '%s' matched line '%s'" % (config_section.regex[idx], line)

                            # Pattern with a replacement
                            if config_section.regex_replacement[idx]:
                                replacement = config_section.regex_replacement[idx]
                                for macro in PATTERN_MACRO_IN_REPL.findall(replacement):
                                    if macro.startswith(PREFIX_NO_MACRO) or self.pre_defined_macros.get(macro) is None:
                                        continue
                                    replacement = re.sub(r'\\g<%s>' % macro, self.pre_defined_macros[macro], replacement)

                                linesub = config_section.pattern[idx].sub(replacement, line)
                                if linesub != line:
                                    save = True
                                    line = linesub

                            # Pattern without a replacement
                            #  * first search against named pattern, and get what named pattern is
                            #  * substitued matched named pattern in contents to macro.
                            else:

                                for macro in PATTERN_MACRO_IN_REGEX.findall(config_section.regex[idx]):
                                    if macro.startswith(PREFIX_NO_MACRO):
                                        raise Exception('Macro %s can not start with %s, if used as named pattern, define a replacement for pattern!' % (macro, PREFIX_NO_MACRO))
                                    if m.group(macro):
                                        if line.count(m.group(macro)) > 1:
                                            print >> sys.stderr, "Error: find multiple '%s' for macro '%s' in line: %s" % \
                                                (m.group(macro), macro, line)
                                            continue
                                        if macro not in self.pre_defined_macros:
                                            raise Exception("Error: macro '%s' not defined." % macro)
                                        if m.group(macro) != self.pre_defined_macros[macro]:
                                            line = line.replace(m.group(macro), self.pre_defined_macros[macro])
                                            save = True
                                    else:
                                        print >> sys.stderr, "Warning: '%s' in re.match is blank, line: %s" % (macro, line)
                        contents += line + lineending
                    fp.close()
                    if save:
                        self._save_file(config_file_name, contents)

def usage(code, msg=''):
    if code:
        fd = sys.stderr
    else:
        fd = sys.stdout
    print >> fd, __doc__ % {
        "COPYRIGHT":COPYRIGHT,
        "PACKAGENAME":sys.argv[0],
        "VALID_TYPES":' | '.join(VALID_TYPES), 
        }

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
            if opt_type not in VALID_TYPES:
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
        packages = PackageGroups(opt_package)
    else:
        packages = PackageGroups()

    for cmd in args:
        if cmd == 'list':
            config_files = packages.get_config_file_by_type(opt_type)
            print "\n".join(sorted(config_files))

        elif (cmd.startswith('list_') and len(cmd)>len('list_') and  'list_macros'.startswith(cmd) ) or \
             (not cmd.startswith('list_') and len(cmd)>len('list') and  'listmacros'.startswith(cmd) ):
            not_defined_macros = packages.reference_macros - set(packages.pre_defined_macros.keys())
            print "# Pre defined macros in %s:" % MACROS_FILE
            print '\t',
            print '\n\t'.join(sorted(packages.pre_defined_macros.keys()))
            print 
            print "# Macros used in config filess:"
            print '\t',
            print '\n\t'.join(sorted(packages.reference_macros))
            if not_defined_macros:
                print "# Warning: macros not defined!!!"
                print '\t',
                print '\n\t'.join(sorted(not_defined_macros))

        elif (cmd.startswith('list_') and len(cmd)>len('list_') and  'list_backups'.startswith(cmd) ) or \
             (not cmd.startswith('list_') and len(cmd)>len('list') and  'listbackups'.startswith(cmd) ):
            packages.list_backups()

        elif len(cmd)>=len('change') and  'change_config_files'.startswith(cmd):
            packages.change_config_files()

        elif len(cmd)>=len('extract') and  'extract_macros'.startswith(cmd):
            packages.extract_macros()

        else:
            usage(1, 'Unknown cmd: %s' % cmd)

if __name__ == "__main__":
    sys.exit(main())

# vim: et ts=4 sw=4
