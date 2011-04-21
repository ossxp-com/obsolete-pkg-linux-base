#!/bin/sh -e

[ "$(echo -e)" = "-e" ] && ECHO="echo" || ECHO="echo -e"

if [ `id -u` -ne 0 ]; then
  $ECHO "you must be root to run this script!"
  exit 1
fi

#------------------------------------------------------------
# add tor DEBIAN SOURCE to /etc/apt/sources.list
CONFFILE=/etc/apt/sources.list
if [ -f ${CONFFILE} ]; then
    if ! grep -q "mirror.noreply.org/pub/tor" ${CONFFILE}; then
        $ECHO "[1msetting ${CONFFILE}...	done[0m"

        cat >> ${CONFFILE} << EOF

deb     http://mirror.noreply.org/pub/tor etch main
EOF

        apt-get update
    fi
else
    $ECHO "ERROR: $CONFFILE not found!"
fi

#------------------------------------------------------------
# install tor+privoxy
apt-get install tor tsocks privoxy || $ECHO "[1m[44minstall tor tsocks privoxy failed! [0m"

#------------------------------------------------------------
# update config: /etc/tsocks.conf
CONFFILE=/etc/tsocks.conf
if [ -f ${CONFFILE} ]; then
    if ! grep -q "ossxp.com" ${CONFFILE}; then
        $ECHO "[1msetting ${CONFFILE}...	done[0m"
        sed -i -e 's/^\(server\|server_type\|server_port\)\( =.*\)$/#\1\2/g' ${CONFFILE} || true
        cat >> ${CONFFILE} << EOF

# ossxp.com: binding tor (NOT REMOVE THIS LINE)
server = 127.0.0.1
server_type = 5
server_port = 9050
EOF
    fi
else
    $ECHO "ERROR: $CONFFILE not found!"
fi

#------------------------------------------------------------
# update config: /etc/privoxy/config
CONFFILE=/etc/privoxy/config
if [ -f ${CONFFILE} ]; then
    if ! grep -q "^forward-socks4a / localhost:9050 ." ${CONFFILE}; then
        $ECHO "[1msetting ${CONFFILE}...	done[0m"
        cat >> ${CONFFILE} << EOF

forward-socks4a / localhost:9050 .
EOF
    fi
else
    $ECHO "ERROR: $CONFFILE not found!"
fi

#------------------------------------------------------------
# update config: /etc/privoxy/config
[ -x /etc/init.d/tor ]     && ( /etc/init.d/tor     restart || true )
[ -x /etc/init.d/privoxy ] && ( /etc/init.d/privoxy restart || true )

#------------------------------------------------------------
# Usage: set http(s) proxy server to: localhost:8118
$ECHO ""
$ECHO "[1mUsage: set http(s) proxy server to: localhost:8118[0m"
$ECHO ""

[ "$0" != "${0%.sh}" ] && mv -f $0 ${0%.sh}.done

exit 0
