#!/bin/sh

[ -c /dev/kvm ] || sudo modprobe kvm kvm-amd kvm-intel

CWD=$(cd `dirname $0`; pwd)
LOCK_FILE=$CWD/LOCK_FILE
KVMCMD=kvm

VNCPORTCMD=/opt/ossxp/bin/vncport.py
[ -x $VNCPORTCMD ] && $VNCPORTCMD -aq
DISPNUM=$?

if [ -f $CWD/config.vm ]; then
    . $CWD/config.vm
else

HDA=base.img
HDB=swap.img
HDC=
HDD=
CDROM=/data/_iso/ubuntu/dvd/kubuntu-7.04-dvd-i386.iso

ACPI=yes
BOOT=c
MEMORY=512
MACADDR=52:54:00:12:34:04
MOUSE=usb
NET=bridge
SMP=yes
SOUNDHW=sb16
STDVGA=yes
UTC=no
VNC=yes

fi

usage()
{
trap - 0 1 2 13 15

cat <<EOF

Usage $0 [options...]

Options:
    -h|-help
        this screen
    -vnc|-no-sdl
        draw screen using vnc
    -sdl|-no-vnc
        draw screen using sdl
    -no-smp
        emulate one cpu
    -m|-mem <Num>
        set memery size: <Num> MB
    -acpi
        enable acpi
    -utc|-localtime
        bios time is utc or loaltiom
EOF
}

GetMacAddr()
{
    printf "52:54:00:12:34:%02x" $((255-$DISPNUM))
}

fn_rm_lock()
{
  trap - 0 1 2 13 15
  rm $LOCK_FILE
}

fn_create_lock()
{
  trap - 0 1 2 13 15
  if [ -f $LOCK_FILE ]; then
    echo "Error: VM already start!"
    exit 1
  fi

  touch $LOCK_FILE
  trap 'fn_rm_lock' 0 1 2 13 15
}

############################################################
# Main Function
############################################################

if [ ! -z "$HDA" ]; then
    if echo "$HDA" | egrep -qv "^/"; then
        HDA=$CWD/$HDA
    fi
fi

if [ ! -z "$HDB" ]; then
    if echo "$HDB" | egrep -qv "^/"; then
        HDB=$CWD/$HDB
    fi
fi

if [ ! -z "$HDC" ]; then
    if echo "$HDC" | egrep -qv "^/"; then
        HDC=$CWD/$HDC
    fi
fi

if [ ! -z "$HDD" ]; then
    if echo "$HDD" | egrep -qv "^/"; then
        HDD=$CWD/$HDD
    fi
fi

if [ ! -z "$CDROM" ]; then
    if echo "$CDROM" | egrep -qv "^/"; then
        CDROM=$CWD/$CDROM
    fi
fi

if echo $ACPI|egrep -iq "^no"; then 
    opt_acpi="-no-acpi"
fi

if [ ! -z "$MEMORY" ] && [ "$MEMORY" -gt 128 ]; then
    opt_mem="-m $MEMORY"
else
    opt_mem="-m 512"
fi

if echo $MOUSE|egrep -iq "^usb"; then
    opt_others="$opt_others -usb -usbdevice tablet"
fi

if [ -z "$MACADDR" ]; then
    MACADDR=$(GetMacAddr)
fi

if [ -z "$NETSCRIPT" ]; then
    NETSCRIPT="/etc/kvm/kvm-ifup"
fi

if echo $NET|egrep -iq "^bridge"; then
    opt_net="-net nic,vlan=0,macaddr=$MACADDR -net tap,vlan=0,script=${NETSCRIPT}"
elif echo $NET|egrep -iq "^nat"; then
    opt_net="-net nic,macaddr=$MACADDR -net user"
elif echo $NET|egrep -iq "^standalone"; then
    opt_net="-net nic,macaddr=$MACADDR -net tap"
elif [ ! -z "$NET" ]; then
    opt_net=$(echo "$NET"|sed -e "s/MACADDR/${MACADDR}/g")
else
    opt_net="-net nic,macaddr=$MACADDR -net user"
fi

if echo $SMP|egrep -iq "^yes"; then
    cpus=`grep "^processor" /proc/cpuinfo|wc -l`
    if [ $cpus -gt 1 ]; then
        opt_smp="-smp $cpus"
    fi
fi

if [ ! -z $SOUNDHW ]; then
    opt_others="$opt_others -soundhw $SOUNDHW"
fi

if echo $UTC|egrep -iq "^no"; then
    opt_localtime="-localtime"
fi

if echo $VNC|egrep -iq "^yes"; then
    opt_display="-vnc :$DISPNUM -k en-us"
else
    opt_display=
fi

if echo $STDVGA|egrep -iq "^yes"; then
    opt_std_vga=-std-vga
fi

if [ ! -z "$HDA" ]; then
    opt_hda="-hda $HDA"
else
    opt_hda=
fi

if [ ! -z "$HDB" ]; then
    opt_hdb="-hdb $HDB"
else
    opt_hdb=
fi

if [ ! -z "$HDC" ]; then
    opt_hdc="-hdc $HDC"
else
    opt_hdc=
fi

if [ ! -z "$HDD" ]; then
    opt_hdd="-hdd $HDD"
else
    opt_hdd=
fi

if [ ! -z "$CDROM" ]; then
    opt_cdrom="-cdrom $CDROM"
    [ -z "$BOOT" ] && BOOT=d
else
    opt_cdrom=
    [ -z "$BOOT" ] && BOOT=c
fi

if [ ! -z "$BOOT" ]; then
    opt_boot="-boot $BOOT"
fi

for disk in $HDA $HDB $HDC $HDD; do
   if [ ! -z $disk ] && ( lsattr $disk 2>/dev/null| cut -d" " -f1 | grep -q "i" || ! test -w $disk ); then
      echo -e "[1mImage($(basename $disk)) is readonly, using snapshot mode![0m"
      opt_snapshot="-snapshot"
  fi
done

while [ $# -gt 0 ]; do
  case $1 in
    -h|-help|--help)
       usage
       exit 0
       ;;
    -std-vga)
       opt_std_vga=-std-vga
       ;;
    -cmd)
       shift
       KVMCMD=$1
       ;;
    -vnc|-no-sdl)
       opt_display="-vnc :$DISPNUM -k en-us"
       ;;
    -sdl|-no-vnc)
       opt_display=
       ;;
    -no-smp)
       opt_smp=
       ;;
    -smp)
       shift
       opt_smp="-smp $1"
       ;;
    -localtime|-no-utc)
       opt_localtime="-localtime"
       ;;
    -utc)
       opt_localtime=
       ;;
    -m|-mem)
       shift
       opt_mem="-m $1"
       ;;
    -no-acpi)
       opt_acpi="-no-acpi"
       ;;
    -acpi)
       opt_acpi=
       ;;
    -boot)
       shift
       opt_boot="-boot $1"
       ;;
    -n)
       opt_dryrun=yes
       ;;
    *)
       break
       ;;
  esac
  shift
done

if echo $*|grep -q "-net"; then
    opt_net=
fi

CMD="sudo $KVMCMD \
    $opt_localtime \
    $opt_smp \
    $opt_mem \
    $opt_hda $opt_hdb $opt_hdc $opt_hdd \
    $opt_cdrom \
    $opt_boot \
    $opt_display \
    $opt_std_vga \
    $opt_acpi \
    $opt_others \
    $opt_net \
    $opt_snapshot \
    $*"


echo "======================================================================"
echo $CMD
echo "======================================================================"

if [ ! -z "$opt_snapshot" ]; then
    echo ""
    echo -e "[1mWarning: Running VM in 'snapshot' mode!!![0m"
    echo -e "[1m^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^[0m"
fi

#[ -t ] && (echo "press any key..."; read x; )

fn_create_lock

if [ "$opt_dryrun" != "yes" ]; then
    eval "$CMD"
fi
