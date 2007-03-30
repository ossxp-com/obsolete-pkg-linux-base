#!/bin/sh -e

[ -x /bin/echo ] && alias echo=/bin/echo

if [ `id -u` -ne 0 ]; then
  echo "you must be root to run this script!"
  exit 1
fi

if [ -x /opt/ossxp/base.sh ]; then
    sh /opt/ossxp/base.sh
fi

# install packages
#------------------------------------------------------------
# My already installed by tasksel standard package:
apt-get install --force-yes -y nfs-common portmap || true

for pkg in \
    apt-show-versions ascii auto-apt curl \
    eject ethtool fping \
    gpm lynx mc pdumpfs \
    smbfs sshfs xprobe zhcon \
; do
    echo -e "[1minstall $pkg :[0m"
    apt-get install --force-yes -y $pkg || echo -e "[1m[44minstall $pkg failed! [0m"
done

#------------------------------------------------------------
# sshfs(fuse-utils) needs this special file
[ -c /dev/fuse ] || mknod -m 666 /dev/fuse c 10 229

#------------------------------------------------------------

[ "$0" != "${0%.sh}" ] && mv -f $0 ${0%.sh}.done
exit 0
