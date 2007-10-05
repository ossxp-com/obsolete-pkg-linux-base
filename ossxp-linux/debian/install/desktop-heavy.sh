#!/bin/sh -e

# include apt maintainance functions
. /opt/ossxp/install/apt.inc

########################################
# User defined packages list
########################################
PKG_LIST="
    kde kdm kde-i18n-zhcn kde-i18n-zhtw 
    amarok mozilla-firefox mozilla-firefox-locale-zh-cn 
    mozilla-thunderbird mozilla-thunderbird-inspector mozilla-thunderbird-typeaheadfind thunderbird-locale-zh-cn 
    nessusd nessus nmapfe flashplugin-nonfree 
    kompare cervisia kdesvn kdevelop3 kdevelop 
    evince kchmviewer gthumb gimp inkscape 
    gspca-source ndiswrapper-source ndiswrapper-utils module-assistant 
    gtkam kphotoalbum gphoto2 
    kino kinoplugs 
    tightvncserver 
    pidgin ekiga v4l-config libsdl1.2debian-all 
    wine wine-utils 
    "

[ -x /bin/echo ] && alias echo=/bin/echo

if [ `id -u` -ne 0 ]; then
  echo "you must be root to run this script!"
  exit 1
fi

if [ -x /opt/ossxp/install/desktop-light.sh ]; then
    sh /opt/ossxp/install/desktop-light.sh
fi

#------------------------------------------------------------
# install packages
echo "[1m========== Install user defined packages ==========[0m"
install_packages $PKG_LIST

[ "$0" != "${0%.sh}" ] && mv -f $0 ${0%.sh}.done
#exit 0
