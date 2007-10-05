#!/bin/sh -e

# include apt maintainance functions
. ./apt.inc

########################################
# User defined packages list
########################################
PKG_LIST="
    xfce4 xdm xscreensaver 
    "

[ -x /bin/echo ] && alias echo=/bin/echo

if [ `id -u` -ne 0 ]; then
  echo "you must be root to run this script!"
  exit 1
fi

if [ -x /opt/ossxp/install/desktop-core.sh ]; then
    sh /opt/ossxp/install/desktop-core.sh
fi

#------------------------------------------------------------
# install packages
echo "[1m========== Install user defined packages ==========[0m"
install_packages $PKG_LIST

[ "$0" != "${0%.sh}" ] && mv -f $0 ${0%.sh}.done
#exit 0
