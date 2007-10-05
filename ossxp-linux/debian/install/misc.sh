#!/bin/sh -e

# include apt maintainance functions
. /opt/ossxp/install/apt.inc

########################################
# User defined packages list
########################################
PKG_LIST="
    nfs-common portmap
    auto-apt 
    eject 
    gpm mc pdumpfs resolvconf 
    smbfs sshfs xprobe 
    "

[ -x /bin/echo ] && alias echo=/bin/echo

if [ `id -u` -ne 0 ]; then
  echo "you must be root to run this script!"
  exit 1
fi

if [ -x /opt/ossxp/install/base.sh ]; then
    sh /opt/ossxp/install/base.sh
fi

function do_install()
{
    # install packages
    #------------------------------------------------------------
    echo "[1m========== Install user defined packages ==========[0m"
    install_packages $PKG_LIST
}

function do_config()
{
    #------------------------------------------------------------
    # sshfs(fuse-utils) needs this special file
    if [ ! -c /dev/fuse ]; then
        echo -ne "[1m[44m"
        cat << EOF

==================================================
* FUSE and/or SSHFS is installed but fuse not built-in kernel.
  You can load fuse at runtime: 'modprobe fuse'
  Or add 'fuse' to /etc/modules to load it when kernel restart.

EOF
        echo -ne "[0m"
    fi
}


#------------------------------------------------------------
# MAIN FUNCTION HERE
if [ $# -eq 0 ]; then
    do_install
    do_config
    [ "$0" != "${0%.sh}" ] && mv -f $0 ${0%.sh}.done
    exit 0
fi

while [ $# -gt 0 ]; do
    case $1 in
    install)
        shift
        do_install
    ;;
    config)
        shift
        do_config
    ;;
    *)
        echo "Wrong params: $1"
        shift
    ;;
    esac
done

#exit 0
