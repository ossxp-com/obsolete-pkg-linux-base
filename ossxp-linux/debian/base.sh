#!/bin/sh -e

[ -x /bin/echo ] && alias echo=/bin/echo

if [ `id -u` -ne 0 ]; then
  echo "you must be root to run this script!"
  exit 1
fi

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
apt-get install --force-yes -y less locales wget || true

for pkg in \
    acl bsdutils bzip2 \
    flexbackup \
    ntpdate \
    openssl p7zip-full pciutils psmisc rdiff-backup \
    screen shellutils ssh star sudo sysutils \
    unison vim \
; do
    echo -e "[1minstall $pkg :[0m"
    apt-get install --force-yes -y $pkg || echo -e "[1m[44minstall $pkg failed! [0m"
done

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

#User_Alias      FULLTIMERS = admin1,admin2
#FULLTIMERS      ALL = NOPASSWD: ALL

%wheel          ALL = (ALL) ALL
EOF
    fi
fi


#------------------------------------------------------------
# sshd_config
CONFFILE=/etc/ssh/sshd_config
if [ -f ${CONFFILE} ]; then
    if ! id -g wheel > /dev/null 2>&1 ; then
        addgroup --system wheel
    fi
    if ! grep -q "^[[:space:]]*[#]\?[[:space:]]*AllowGroups" ${CONFFILE}; then
        echo -e "[1msetting ${CONFFILE}...	done[0m"
        cat >> ${CONFFILE} << EOF

# Only allow login if users belong to these groups:
#AllowGroups wheel
EOF

        echo -ne "[1m[44m"
        echo -e "[/etc/ssh/sshd_config]: uncomment 'AllowGroups wheel' to secure you linux."
        echo -ne "[0m"
    fi

    if ! grep -q "Specifies whether root can log in using ssh" ${CONFFILE}; then
        sed -i -e "/PermitRootLogin/ d"  ${CONFFILE}
        cat >> ${CONFFILE} << EOF

# OSSXP.COM: Specifies whether root can log in using ssh
PermitRootLogin no
EOF
    fi
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

[ "$0" != "${0%.sh}" ] && mv -f $0 ${0%.sh}.done
#exit 0
