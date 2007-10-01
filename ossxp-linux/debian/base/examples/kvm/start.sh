#!/bin/sh

[ -c /dev/kvm ] || sudo modprobe kvm kvm-amd kvm-intel

DISK_C=ossxp-working.img
DISK_D=swap.img
#CDROM=/data/_iso/debian/debian-etch4.0r0_i386/debian-40r0-i386-DVD-1.iso

opt_mem="-m 512"
opt_localtime="--localtime"

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


EOF
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
    *)
       usage
       exit 1
       ;;
  esac
  shift
done


sudo kvm \
    $opt_localtime \
    $opt_smp \
    $opt_mem \
    $opt_disk_c \
    $opt_disk_d \
    $opt_cdrom \
    $opt_boot \
    $opt_display \
    -no-acpi \
    -soundhw sb16 \
    -usb -usbdevice tablet \
    -net nic,vlan=0 -net tap,vlan=0,script=/etc/kvm/kvm-ifup \
    &


#    -net nic -net user \
#    -no-quit  \
