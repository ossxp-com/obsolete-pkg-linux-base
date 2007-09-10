#!/bin/sh
# levels:  100 60 20 28 36 44 52 60 68 76 84 92 100

DEV=/proc/acpi/video/VGA/LCD/brightness

[ -f $DEV ] || modprobe video
value="`cat $DEV | grep current: | awk '{print $2;}'`"
echo $value

if [ $value -eq 0 ]; then
	value=92
fi
if [ $value -ge 92 ]; then
	value=92
else
	value=`expr $value + 8`
fi

[ -f $DEV ] && echo $value > $DEV
