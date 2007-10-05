#!/bin/sh -e

# include apt maintainance functions
. /opt/ossxp/install/apt.inc

########################################
# User defined packages list
########################################
PKG_LIST="
    gcc gcc-3.4 gdb g++ make patch autoconf automake chrpath cdbs 
    dh-make debhelper dh-buildinfo dpkg-dev dpkg-repack dpatch quilt doxygen 
    java-package kernel-package fakeroot module-init-tools 
    devscripts fakeroot hdparm 
    libtool libc6-dev libncurses5-dev 
    libssl-dev libldap2-dev libxml2-dev libexpat1-dev libperl-dev libbz2-dev 
    libc-client-dev libcurl3-dev libfreetype6-dev libgcrypt11-dev libgd2-xpm-dev 
    libjpeg62-dev libmcrypt-dev libmhash-dev libmysqlclient-dev libpng12-dev libsnmp-dev 
    libsdl1.2debian libsdl1.2debian-all libsdl-image1.2 
    libsdl1.2-dev libsdl-image1.2-dev libasound2 libasound2-dev 
    lintian linda lsb-release pkg-config 
    mkisofs module-assistant 
    patchutils pbuilder python-dev qemu swig 
    uuid-dev xutils zlib1g-dev 
    "

[ -x /bin/echo ] && alias echo=/bin/echo

if [ `id -u` -ne 0 ]; then
  echo "you must be root to run this script!"
  exit 1
fi

if [ -x /opt/ossxp/install/misc.sh ]; then
    sh /opt/ossxp/install/misc.sh
fi

#------------------------------------------------------------
# install packages
echo "[1m========== Install user defined packages ==========[0m"
install_packages $PKG_LIST

[ "$0" != "${0%.sh}" ] && mv -f $0 ${0%.sh}.done
#exit 0
