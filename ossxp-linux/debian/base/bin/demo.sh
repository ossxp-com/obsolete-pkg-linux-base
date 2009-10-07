#!/bin/bash

count=0

prompt()
{
    eol=yes
    pause=
    echo -e -n "[1m"
    while [ $# -gt 0 ]; do
        case $1 in
        -N)
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
    if [ $count -gt 0 ]; then echo -n -e "{$count} "; fi
    echo -n -e $*
    echo -e -n "[0m"
    if [ "$eol" = "yes" ]; then echo ""; fi
    if [ "$pause" = "yes" ]; then read ignore; fi
}

help_msg()
{
    echo -e "[1mSyntax:[0m"
    echo -e "\t$0 start: switch to demo mode"
    echo -e "\t$0 stop:  quit demo mode"
}

demo_start()
{
    prompt -N -n "Stop crontab ...\t"
    /etc/init.d/cron stop >/dev/null 2>&1
    prompt "done"

    prompt -N "Please check if br1 is configured, and has ip address ...."
    ifup br1
    ifconfig br1
    prompt -p "done"

    prompt -N "Please check dns resolv.conf, if only 127.0.0.1 left ..."
    cat > /etc/resolv.conf <<EOF
#nameserver 202.106.0.20
#nameserver 202.106.46.151
nameserver 127.0.0.1
search foo.bar
EOF
    cat /etc/resolv.conf
    prompt -p "done"


    prompt -N -n "Set screen resolution to 1024x768 ( yes/no )?"
    read check
    case $check in
      y|Y|y*|Y*)
        xrandr -s 1024x768
        ;;
      *)
        echo "you can set resolution by hands: xrandr -s 1024x768"
        ;;
    esac
    prompt "done"

    prompt -N "set alias for shell by hands...\t"
    if ! grep -q "^syntax off" ~/.vimrc; then
        prompt "set *syntax off* in ~/.vimrc"
        echo "syntax off" >> ~/.vimrc
    fi
    echo "+++++++++++++++++++++++++++++++++++++++++++++++"
    cat << EOF
Turn off color of *ls*:
    alias ls='ls --color=none -F'

Turn off color of *vi*:
    :syntax off
EOF
    echo "+++++++++++++++++++++++++++++++++++++++++++++++"
    prompt -p "done"
}

demo_stop()
{
    prompt -N -n "Start crontab ...\t"
    /etc/init.d/cron start >/dev/null 2>&1
    prompt "done"

    prompt -N "Please check dns resolv.conf, if only there are available dns left ..."
    cat > /etc/resolv.conf <<EOF
nameserver 202.106.0.20
nameserver 202.106.46.151
nameserver 127.0.0.1
search foo.bar
EOF
    cat /etc/resolv.conf
    prompt -p "done"


    prompt -N -n "Set screen resolution back to 1280x800 ( yes/no )?"
    read check
    case $check in
      n|N|n*|N*)
        echo "you can set resolution by hands: xrandr -s 1280x800"
        ;;
      *)
        xrandr -s 1280x800
        ;;
    esac
    prompt "done"

    if grep -q "^syntax off" ~/.vimrc; then
        prompt "remove *syntax off* from ~/.vimrc"
        sed -i -e "/^syntax off/ d" ~/.vimrc
    fi
    prompt -N "set alias for shell by hands...\t"
    echo "+++++++++++++++++++++++++++++++++++++++++++++++"
    cat << EOF
Turn off color of *ls*:
    alias ls='ls --color=auto -F'

Turn on color of *vi*:
    :syntax on
EOF
    echo "+++++++++++++++++++++++++++++++++++++++++++++++"
    prompt -p "done"
}


###########################################################
# Program begins
###########################################################

if [ `id -u` != 0 ]; then
    prompt "============================================="
    prompt "Setting demostration environment. "
    prompt "only root user can run this script."
    prompt "============================================="
    exit 1
fi

if [ $# -eq 0 ]; then
    help_msg
else
    case $1 in
    sta*|STA*)
        demo_start
        ;;
    sto*|STO*)
        demo_stop
        ;;
    esac
fi

exit 0

