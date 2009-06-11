#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
import re

MACROS_FILE = '/etc/ossxp/packages/macros'
PATTERN_MACRONAME = re.compile(r'\(\?P<([^>]+)>.*?\)')

class ConfigFile(object):
    def __init__(self, name):
        self.name = name.strip()
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


def _parse_file(filename):
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
        if line.strip()=='' or line[0] == '#':
            continue

        if line.startswith('file:'):
            if config:
                configs.append(config)
            config = ConfigFile(line[5:])
            has_regex = False

        if line.startswith('type:'):
            types = line[5:].split(',')
            for type in types:
                type = type.strip()
                if type not in ['ip', 'host']:
                    raise Exception('Unknown type: %s' % type)
                config.types.append(type)

        if line.startswith('regex:'):
            has_regex = True
            continue

        if has_regex and (line[0] == ' ' or line[0] == '\t'):
            config.add_regex(line.strip())

    if config:
        configs.append(config)

    return configs

def _parse_dir(configs, dirname, fnames):
    for i in range(len(fnames)-1,-1,-1):
        if not fnames[i].endswith('.conf'):
            del fnames[i]
    for i in fnames:
        pkg_name = i.rsplit('.',1)[0]
        configs[pkg_name] = _parse_file(os.path.join(dirname, i))
    return configs

def get_config_objects(configs, type=None):
    objects = []
    if type:
        type = type.strip().lower()
    for val in configs.values():
        for obj in val:
            if type and type not in obj.types:
                continue
            objects.append(obj)
    return objects 

def get_macros(filename):
    macros = {}
    if not os.path.isfile(filename):
        return macros
    fp = open(filename)
    for line in fp.readlines():
        line = line.strip()
        if not line or line[0]=='#':
            continue
        key, value = line.split(':',1)
        macros[key.strip()] = value.strip()
    return macros

def get_reference_macros(configs):
    refs = set([])
    for val in configs.values():
        for obj in val:
            if not obj.pattern:
                continue
            for regex in obj.regex:
                refs |= set(PATTERN_MACRONAME.findall(regex))
    return refs

def _substitute_precheck(configs, macros):
    refs = get_reference_macros(configs)
    not_defined_macros = refs-set(macros.keys())
    if not_defined_macros:
        raise Exception("Macros not defined in file %s:\n%s" % 
            (MACROS_FILE, '\n'.join(not_defined_macros)))
    for k,v in macros.items():
        if not v:
            raise Exception("You have not defined a value for macro '%s'!" % k)
   

def save_file(filename, contents):
    import difflib
    fp = open(filename, 'r')
    old = fp.read()
    fp.close()
    for line in difflib.unified_diff(old.splitlines(), contents.splitlines(), 'old %s' % filename , 'new %s' % filename, lineterm=''):
        print line
    fp = open(filename, 'w')
    fp.write(contents)
    fp.close()
    print "saved %s." % filename

def substitute(configs):
    macros = get_macros(MACROS_FILE)

    _substitute_precheck(configs, macros)

    for val in configs.values():
        for obj in val:
            if not obj.pattern:
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
                    for macro in PATTERN_MACRONAME.findall(obj.regex[idx]):
                        if m.group(macro):
                            if line.count(m.group(macro)) > 1:
                                print >> sys.stderr, "Find multiple '%s' for macro '%s' in line: %s" % \
                                    (m.group(macro), macro, line)
                                continue
                            if m.group(macro) != macros[macro]:
                                line = line.replace(m.group(macro), macros[macro])
                                save = True
                        else:
                            print >> sys.stderr, "'%s' in re.match is blank, line: %s" % (macro, line)
                contents += line
            fp.close()
            if save:
                save_file(filename, contents)


configs = {}
os.path.walk('/opt/ossxp/lib/packages/', _parse_dir, configs)

print >> sys.stderr, '-'*50

substitute(configs)
sys.exit(0)

print configs

print map(lambda x:x.name, get_config_objects(configs, 'host'))
print '-'*50
print map(lambda x:x.name, get_config_objects(configs, 'ip'))
print '-'*50
check_config_files(configs)

# vim: et ts=4 sw=4
