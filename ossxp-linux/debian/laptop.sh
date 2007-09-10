#!/bin/sh -e

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
for pkg in \
    acpi acpid acpi-support acpitool anacron cpufrequtils \
    hdparm sdparm hotkeys laptop-mode-tools \
    pcmciautils powersaved hotkey-setup hibernate uswsusp\
; do
    echo -e "[1minstall $pkg :[0m"
    apt-get install --force-yes -y $pkg || echo -e "[1m[44minstall $pkg failed! [0m"
done

[ "$0" != "${0%.sh}" ] && mv -f $0 ${0%.sh}.done
#exit 0
