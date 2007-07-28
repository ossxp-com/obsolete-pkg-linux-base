#!/bin/sh -e

[ -x /bin/echo ] && alias echo=/bin/echo

if [ `id -u` -ne 0 ]; then
  echo "you must be root to run this script!"
  exit 1
fi

function set_config()
{
    [ $# -ne 2 ] && { echo "Wrong parameters: set_config KEY VAL"; exit 1; }
    KEY=$1
    VAL=$2
    if ! grep -q "^$KEY $VAL$" ${CONFFILE}; then
        echo -e -n "[1mSetting $KEY $VAL[0m...	"
        grep -q "^$KEY\b" ${CONFFILE} && 
	{
          sed -i -e "s/^$KEY\b.*$/$KEY $VAL/" ${CONFFILE} 
	} || {
	  echo "" >> ${CONFFILE} 
	  echo "$KEY $VAL" >> ${CONFFILE} 
	}
        echo -e "[1mdone[0m"
	return 0
    else
        return 1
    fi
}

function do_install()
{
    # tasksel standard package
    #------------------------------------------------------------
    # aptitude search ~pstandard
    echo -e "[1minstall ~pstandard :[0m"
    aptitude install -y ~pstandard || echo -e "[1m[44minstall ~pstandard failed! [0m"
    # aptitude search ~prequired
    echo -e "[1minstall ~prequired :[0m"
    aptitude install -y ~prequired || echo -e "[1m[44minstall ~prequired failed! [0m"
    # aptitude search ~pimportant:
    echo -e "[1minstall ~pimportant :[0m"
    aptitude install -y ~pimportant || echo -e "[1m[44minstall ~pimportant failed! [0m"

    # install packages
    #------------------------------------------------------------
    # My already installed by tasksel standard package:
    apt-get install --force-yes -y less locales wget ssh sudo || true
    
    for pkg in \
        acl ascii bsdutils bzip2 curl cabextract dstat \
        flexbackup \
        htop ntpdate ia32-libs \
        openssl p7zip-full pciutils psmisc rdiff-backup \
        saidar screen shellutils ssh star sudo sysutils sysstat \
        unison vim vnstat \
    ; do
        echo -e "[1minstall $pkg :[0m"
        apt-get install --force-yes -y $pkg || echo -e "[1m[44minstall $pkg failed! [0m"
    done
    }


function do_config()
{

    #------------------------------------------------------------
    CONFFILE=/opt/ossxp/conf/public.key
    if [ -f ${CONFFILE} ]; then
        apt-key add ${CONFFILE} 
    fi

    #------------------------------------------------------------
    # set command line style to vi (/etc/inputrc, /etc/bash.bashrc)
    CONFFILE=/etc/inputrc
    if [ -f ${CONFFILE} ]; then
        if ! grep -iq "OSSXP.COM settings:" ${CONFFILE}; then
            echo -e "[1msetting ${CONFFILE}...	done[0m"
            cat >> ${CONFFILE} << EOF

### OSSXP.COM settings:
set bell-style visible
set completion-ignore-case on
set editing-mode vi
EOF
        fi
    else
        echo -e "[1mWarning: /etc/inputrc not exist, use /etc/profile instead![0m"
        # set -o vi
        CONFFILE=/etc/bash.bashrc
        if [ ! -f ${CONFFILE} ]; then
            CONFFILE=/etc/profile
        fi
        if [ -f ${CONFFILE} ]; then
            if ! grep -q "^[[:space:]]*set -o vi" ${CONFFILE}; then
                echo -e "[1msetting ${CONFFILE}...	done[0m"
                cat >> ${CONFFILE} << EOF

set -o vi
EOF
            fi
        fi
    fi
    
    
    if [ -f /etc/bash_completion ]; then
        CONFFILE=/etc/bash.bashrc
        if [ ! -f ${CONFFILE} ]; then
        CONFFILE=/etc/profile
        fi
        if [ -f ${CONFFILE} ]; then
            if ! grep -q "^[[:space:]]*[^#].*bash_completion" ${CONFFILE}; then
                echo -e "[1menable bash_completion...	done[0m"
                cat >> ${CONFFILE} << EOF

# enable bash completion in interactive shells
if [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
fi
EOF
            fi
        else
            echo -e "[1mWarning: ${CONFFILE} does not exist![0m"
        fi
    fi

    #------------------------------------------------------------
    # sudoers
    CONFFILE=/etc/sudoers
    if [ -f ${CONFFILE} ]; then
        if ! id -g wheel > /dev/null 2>&1 ; then
            addgroup --system wheel
        fi
        if ! grep -q "^%wheel" ${CONFFILE}; then
            echo -e "[1msetting ${CONFFILE}...	done[0m"
            cat >> ${CONFFILE} << EOF

%wheel          ALL = (ALL) ALL

#User_Alias      FULLTIMERS = admin1,admin2
#FULLTIMERS      ALL = NOPASSWD: ALL
EOF
        fi
    else
        echo -e "[1mWarning: ${CONFFILE} does not exist![0m"
    fi

    #------------------------------------------------------------
    # sshd_config
    CONFFILE=/etc/ssh/sshd_config
    if [ -f ${CONFFILE} ]; then
        RESTARTSSH="no"
        if ! awk -F: '{print $1;}' /etc/group | grep -q wheel; then
            /usr/sbin/addgroup --system wheel
        fi
        if ! grep -q "^[[:space:]]*[#]\?[[:space:]]*AllowGroups" ${CONFFILE}; then
            echo -e "[1msetting ${CONFFILE}...	done[0m"
            cat >> ${CONFFILE} << EOF

# Only allow login if users belong to these groups:
#AllowGroups wheel
EOF

            echo -ne "[1m[44m"
            echo -e "[/etc/ssh/sshd_config]: uncomment 'AllowGroups wheel' to secure your ssh."
            echo -ne "[0m"
        fi
    
        set_config Protocol 2 && RESTARTSSH="yes"
        set_config PermitRootLogin no && RESTARTSSH="yes"
        set_config PermitEmptyPasswords no && RESTARTSSH="yes"
        set_config UsePrivilegeSeparation yes && RESTARTSSH="yes"
    
        # restart ssh daemon
        if [ "$RESTARTSSH" = "yes" ]; then
            if [ -x /etc/init.d/ssh ]; then
                /etc/init.d/ssh restart
            else
                invoke-rc.d ssh restart 
            fi
        fi
    else
        echo -e "[1mWarning: ${CONFFILE} does not exist![0m"
    fi

    #------------------------------------------------------------
    # screenrc
    CONFFILE=/etc/screenrc
    if [ -f ${CONFFILE} ]; then
        if ! grep -q "^caption always" ${CONFFILE}; then
            echo -e "[1msetting ${CONFFILE}...	done[0m"
            cat >> ${CONFFILE} << EOF

#defscrollback 3000
#vbell on
#startup_message off

# Set the caption on the bottom line
caption always "%{= kw}%-Lw%{= BW}%n %t%{-}%+w %-= @%H - %Y/%m/%d, %C"
EOF
        fi
    else
        echo -e "[1mWarning: ${CONFFILE} does not exist![0m"
    fi

    #------------------------------------------------------------
    # locales
    CONFFILE=/etc/locale.gen
    if [ -f ${CONFFILE} ]; then
        GENLOCALE=no
        i="en_US.UTF-8 UTF-8"
        grep -q "${i}" ${CONFFILE} || { echo "${i}" >> ${CONFFILE} ;  GENLOCALE=yes; }
        i="en_US ISO-8859-1"
        grep -q "${i}" ${CONFFILE} || { echo "${i}" >> ${CONFFILE} ;  GENLOCALE=yes; }
        i="zh_CN.UTF-8 UTF-8"
        grep -q "${i}" ${CONFFILE} || { echo "${i}" >> ${CONFFILE} ;  GENLOCALE=yes; }
        i="zh_CN.GBK GBK"
        grep -q "${i}" ${CONFFILE} || { echo "${i}" >> ${CONFFILE} ;  GENLOCALE=yes; }
        i="zh_CN GB2312"
        grep -q "${i}" ${CONFFILE} || { echo "${i}" >> ${CONFFILE} ;  GENLOCALE=yes; }
        i="zh_TW.UTF-8 UTF-8"
        grep -q "${i}" ${CONFFILE} || { echo "${i}" >> ${CONFFILE} ;  GENLOCALE=yes; }
        i="zh_TW BIG5"
        grep -q "${i}" ${CONFFILE} || { echo "${i}" >> ${CONFFILE} ;  GENLOCALE=yes; }
        if [ "${GENLOCALE}" = "yes" ]; then
            echo -e "[1msetting ${CONFFILE}...	done[0m"
            /usr/sbin/locale-gen
            /usr/sbin/update-locale --no-checks "LANG=zh_CN.UTF-8"
        fi
    else
        echo -e "[1mWarning: ${CONFFILE} does not exist![0m"
    fi
    
    #------------------------------------------------------------
    # time settings
    CONFFILE=/etc/default/rcS
    if [ -f ${CONFFILE} ]; then
        if grep -iq "^[[:space:]]*utc[[:space:]]*=[[:space:]]*yes" ${CONFFILE}; then
            echo -ne "[1m[44m"
            echo -e "Warning: [/etc/default/rcS]: UTC=yes! \nbe sure its your really wants."
            echo -ne "[0m"
        fi
    fi
    
    #------------------------------------------------------------
    echo -ne "[1m[44m"
    cat << EOF

==================================================
* OSSXP said: something you can do with you system:
** [/boot/grub/menu.lst]: add 'vga=791' at the end of 'kernel=', 
   if your system support framebuffer.
** [/etc/environment]: define JAVA_HOME, CLASSPATH here for java.
** [/etc/fstab]: add flage 'acl', if ea/acl is your favorate.
** [/etc/network/interface]: add another loop device, cool.
   auto lo:0
   iface lo:0 inet static
        address x.x.x.x
        netmask 255.255.255.0
        network x.x.x.0
        broadcast x.x.x.255

EOF
    echo -ne "[0m"

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
