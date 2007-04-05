#!/bin/sh -e

[ -x /bin/echo ] && alias echo=/bin/echo

if [ `id -u` -ne 0 ]; then
  echo "you must be root to run this script!"
  exit 1
fi

if [ -x /opt/ossxp/install/base.sh ]; then
    sh /opt/ossxp/install/base.sh
fi

# install packages
#------------------------------------------------------------
# My already installed by tasksel standard package:
apt-get install --force-yes -y nfs-common portmap || true

for pkg in \
    apt-show-versions ascii auto-apt curl \
    eject ethtool fping \
    gpm indent lynx mc nmap pdumpfs \
    smbfs sshfs tcpdump xprobe zhcon \
; do
    echo -e "[1minstall $pkg :[0m"
    apt-get install --force-yes -y $pkg || echo -e "[1m[44minstall $pkg failed! [0m"
done

#------------------------------------------------------------
# sshfs(fuse-utils) needs this special file
[ -c /dev/fuse ] || mknod -m 666 /dev/fuse c 10 229

#------------------------------------------------------------
# .indent.pro
CONFFILE=/etc/skel/.indent.pro
if [ ! -f ${CONFFILE} ]; then
    mkdir -p /etc/skel
    cat >> ${CONFFILE} << EOF
-bad -bap -bbb -bbo -nbc -bl -bli0 -bls -c33 -cd33 -ncdb -ncdw -nce
-cli0 -cp33 -cs -d0 -nbfda -di2 -nfc1 -nfca -hnl -ip5 -l75 -lp -pcs -nprs
-psl -saf -sai -saw -nsc -nsob -nss -i4 -ts4 -ut
EOF
fi

#------------------------------------------------------------
[ "$0" != "${0%.sh}" ] && mv -f $0 ${0%.sh}.done
exit 0
