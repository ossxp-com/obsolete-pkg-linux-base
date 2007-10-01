#!/bin/sh

[ -c /dev/kvm ] || sudo modprobe kvm kvm-amd kvm-intel

CWD=$(cd `dirname $0`; pwd)
LOCK_FILE=$CWD/LOCK_FILE

DISK_C=$CWD/ossxp-server-base.img
DISK_D=$CWD/swap.img
#CDROM=/data/_iso/debian/debian-etch4.0r0_i386/debian-40r0-i386-DVD-1.iso

opt_mem="-m 512"
opt_localtime="--localtime"
opt_net="-net nic,vlan=0 -net tap,vlan=0,script=/etc/kvm/kvm-ifup"
opt_acpi="-no-acpi"
opt_others="-soundhw sb16 -usb -usbdevice tablet"  # -no-quit

VNCPORTCMD=/opt/ossxp/bin/vncport.py

if [ ! -z "$DISK_C" ]; then
    opt_disk_c="-hda $DISK_C"
else
    opt_disk_c=
fi

if [ ! -z "$DISK_D" ]; then
    opt_disk_d="-hdb $DISK_D"
else
    opt_disk_d=
fi

if [ ! -z "$CDROM" ]; then
    opt_cdrom="-cdrom $CDROM"
    opt_boot="-boot d"
else
    opt_cdrom=
    opt_boot="-boot c"
fi

if [ ! -z $DISK_C ] && [ -f $DISK_C ] && [ ! -w $DISK_C ]  ; then
    echo "Disk c image is readonly, using snapshot mode"
    opt_snapshot="-snapshot"
fi

[ -x $VNCPORTCMD ] && $VNCPORTCMD -aq
DISPNUM=$?
opt_display="-vnc 0.0.0.0:$DISPNUM -k en-us"

cpus=`grep "^processor" /proc/cpuinfo|wc -l`
if [ $cpus -gt 1 ]; then
    opt_smp="-smp 2"
else
    opt_smp=
fi


function usage()
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


while [ $# -gt 0 ]; do
  case $1 in
    -h|-help|--help)
       usage
       exit 0
       ;;
    -vnc|-no-sdl)
       opt_display="-vnc 0.0.0.0:$DISPNUM -k en-us"
       ;;
    -sdl|-no-vnc)
       opt_display=
       ;;
    -no-smp)
       shift
       opt_smp=
       ;;
    -smp)
       shift
       opt_smp="-smp $1"
       ;;
    -localtime|-no-utc)
       opt_localtime="--localtime"
       ;;
    -utc)
       opt_localtime=
       ;;
    -m|-mem)
       shift
       opt_mem="-m $1"
       ;;
    -acpi)
       opt_acpi=
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

CMD="sudo kvm \
    $opt_localtime \
    $opt_smp \
    $opt_mem \
    $opt_disk_c \
    $opt_disk_d \
    $opt_cdrom \
    $opt_boot \
    $opt_display \
    $opt_acpi \
    $opt_others \
    $opt_net \
    $opt_snapshot \
    $*"

fn_create_lock

echo "======================================================================"
echo $CMD
echo "======================================================================"

eval "$CMD"

