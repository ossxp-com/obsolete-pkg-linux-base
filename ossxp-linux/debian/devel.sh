#!/bin/sh -e

[ -x /bin/echo ] && alias echo=/bin/echo

if [ `id -u` -ne 0 ]; then
  echo "you must be root to run this script!"
  exit 1
fi

if [ -x /opt/ossxp/misc.sh ]; then
    sh /opt/ossxp/misc.sh
fi

#------------------------------------------------------------
# install packages
for pkg in \
    gcc g++ make patch autoconf automake chrpath \
    dh-make debhelper dpkg-dev dpkg-repack dpatch quilt doxygen \
    java-package kernel-package fakeroot module-init-tools \
    devscripts fakeroot file gnupg  \
    libtool libc6-dev libncurses5-dev \
    libssl-dev libldap2-dev libxml2-dev libexpat1-dev libperl-dev libbz2-dev \
    libc-client-dev libcurl3-dev libfreetype6-dev libgcrypt11-dev libgd2-xpm-dev \
    libjpeg62-dev libmcrypt-dev libmhash-dev libmysqlclient-dev libpng12-dev libsnmp-dev \
    lintian linda lsb-release pkg-config \
    module-assistant \
    perl pbuilder python-dev swig \
    uuid-dev xutils zlib1g-dev \
; do
    echo -e "[1minstall $pkg :[0m"
    apt-get install --force-yes -y $pkg || echo -e "[1m[44minstall $pkg failed! [0m"
done

[ "$0" != "${0%.sh}" ] && mv -f $0 ${0%.sh}.done
#exit 0
