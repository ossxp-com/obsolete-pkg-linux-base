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
    x-window-system-core xdg-utils menu \
    ttf-arphic-uming ttf-arphic-ukai ttf-bitstream-vera \
    ttf-arphic-newsung wqy-bitmapfont \
    scim scim-chinese scim-pinyin scim-tables-zh fcitx im-switch \
    alsa-base alsa-oss xsane \
    cupsys-client cupsys-driver-gutenprint cupsys cups-pdf cupsys-bsd printconf \
    foomatic-gui foomatic-filters-ppds foomatic-db-hpijs foomatic-db-gutenprint \
    discover1 hal-device-manager \
    azureus amule d4x ossxp-freemind firestarter kate quanta tsclient \
    gq meld \
; do
    echo -e "[1minstall $pkg :[0m"
    apt-get install --force-yes -y $pkg || echo -e "[1m[44minstall $pkg failed! [0m"
done

[ "$0" != "${0%.sh}" ] && mv -f $0 ${0%.sh}.done
#exit 0
