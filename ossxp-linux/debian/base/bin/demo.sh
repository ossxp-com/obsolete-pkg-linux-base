#!/bin/bash

count=0

function prompt()
{
    eol=yes
    pause=
    echo -e -n "[1m"
    while [ $# -gt 0 ]; do
        case $1 in
        -c)
            count=$((count+1))
            ;;
        -n)
            eol=
            ;;
        -p)
            pause=yes
            ;;
        *)
            break
            ;;
        esac
        shift
    done
    echo -n -e "{$count} "
    echo -n -e $*
    echo -e -n "[0m"
    if [ "$eol" = "yes" ]; then echo ""; fi
    if [ "$pause" = "yes" ]; then read ignore; fi
}

if [ `id -u` != 0 ]; then
    prompt "============================================="
    prompt "Setting demostration environment. "
    prompt "only root user can run this script."
    prompt "============================================="
    exit 1
fi


prompt -c -n "Stop crontab ...\t"
/etc/init.d/cron stop >/dev/null 2>&1
prompt "done"

prompt -c "Please check if br1 is configured, and has ip address ...."
ifup br1
ifconfig br1
prompt -p "done"

prompt -c "Please check dns resolv.conf, if only 127.0.0.1 left ..."
cat > /etc/resolv.conf <<EOF
#nameserver 202.106.0.20
#nameserver 202.106.46.151
nameserver 127.0.0.1
search foo.bar
EOF
cat /etc/resolv.conf
prompt -p "done"


prompt -c -n "Set screen resolution to 1024x768 ( yes/no )?"
read check
case $check in
  n|N|n*|N*)
    echo "you can set resolution by hands: xrandr -s 1024x768"
    ;;
  *)
    xrandr -s 1024x768
esac
prompt "done"


