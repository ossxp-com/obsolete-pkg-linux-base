#!/bin/sh -e

# include apt maintainance functions
. ./apt.inc

########################################
# User defined packages list
########################################
PKG_LIST="
    x-window-system-core xdg-utils menu 
    ttf-arphic-uming ttf-arphic-ukai ttf-bitstream-vera 
    ttf-arphic-newsung wqy-bitmapfont 
    scim scim-chinese scim-pinyin scim-tables-zh fcitx im-switch 
    alsa-base alsa-oss xsane 
    cupsys-client cupsys-driver-gutenprint cupsys cups-pdf cupsys-bsd printconf 
    foomatic-gui foomatic-filters-ppds foomatic-db-hpijs foomatic-db-gutenprint 
    discover1 hal-device-manager 
    azureus amule d4x ossxp-freemind firestarter kate quanta tsclient krdc 
    gq meld 
    "

[ -x /bin/echo ] && alias echo=/bin/echo

if [ `id -u` -ne 0 ]; then
  echo "you must be root to run this script!"
  exit 1
fi

if [ -x /opt/ossxp/install/base.sh ]; then
    sh /opt/ossxp/install/base.sh
fi

#------------------------------------------------------------
# install packages
echo "[1m========== Install user defined packages ==========[0m"
install_packages $PKG_LIST

[ "$0" != "${0%.sh}" ] && mv -f $0 ${0%.sh}.done
#exit 0
