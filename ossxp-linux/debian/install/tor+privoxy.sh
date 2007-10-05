#!/bin/sh -e

[ -x /bin/echo ] && alias echo=/bin/echo

if [ `id -u` -ne 0 ]; then
  echo "you must be root to run this script!"
  exit 1
fi

#------------------------------------------------------------
# add tor DEBIAN SOURCE to /etc/apt/sources.list
CONFFILE=/etc/apt/sources.list
if [ -f ${CONFFILE} ]; then
    if ! grep -q "mirror.noreply.org/pub/tor" ${CONFFILE}; then
        echo -e "[1msetting ${CONFFILE}...	done[0m"

        cat >> ${CONFFILE} << EOF

deb     http://mirror.noreply.org/pub/tor etch main
EOF

        apt-get update
    fi
else
    echo "ERROR: $CONFFILE not found!"
fi

#------------------------------------------------------------
# install tor+privoxy
apt-get install tor tsocks privoxy || echo -e "[1m[44minstall tor tsocks privoxy failed! [0m"

#------------------------------------------------------------
# update config: /etc/tsocks.conf
CONFFILE=/etc/tsocks.conf
if [ -f ${CONFFILE} ]; then
    if ! grep -q "ossxp.com" ${CONFFILE}; then
        echo -e "[1msetting ${CONFFILE}...	done[0m"
        sed -i -e 's/^\(server\|server_type\|server_port\)\( =.*\)$/#\1\2/g' ${CONFFILE} || true
        cat >> ${CONFFILE} << EOF

# ossxp.com: binding tor (NOT REMOVE THIS LINE)
server = 127.0.0.1
server_type = 5
server_port = 9050
EOF
    fi
else
    echo "ERROR: $CONFFILE not found!"
fi

#------------------------------------------------------------
# update config: /etc/privoxy/config
CONFFILE=/etc/privoxy/config
if [ -f ${CONFFILE} ]; then
    if ! grep -q "^forward-socks4a / localhost:9050 ." ${CONFFILE}; then
        echo -e "[1msetting ${CONFFILE}...	done[0m"
        cat >> ${CONFFILE} << EOF

forward-socks4a / localhost:9050 .
EOF
    fi
else
    echo "ERROR: $CONFFILE not found!"
fi

#------------------------------------------------------------
# update config: /etc/privoxy/config
[ -x /etc/init.d/tor ]     && ( /etc/init.d/tor     restart || true )
[ -x /etc/init.d/privoxy ] && ( /etc/init.d/privoxy restart || true )

#------------------------------------------------------------
# Usage: set http(s) proxy server to: localhost:8118
echo ""
echo -e "[1mUsage: set http(s) proxy server to: localhost:8118[0m"
echo ""

[ "$0" != "${0%.sh}" ] && mv -f $0 ${0%.sh}.done

exit 0
