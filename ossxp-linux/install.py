#!/usr/bin/env python

import sys
import os


def install_file(build_root):
    dir_name = "redhat"
    for filename in os.listdir(dir_name):
        if filename.endswith('.install'):
            for line in open(os.path.join(dir_name, filename)):
                source,dist = line.split()
                dist = os.path.join(build_root, dist.lstrip('/'))
                if not os.path.exists(dist):
                    os.makedirs(dist)
                os.system("cp -vr %s %s" % (source, dist))

if __name__ == "__main__":
    if len(sys.argv)>1:
        build_root = sys.argv[1]
    else:
        build_root = os.getcwd()
    install_file(build_root)
