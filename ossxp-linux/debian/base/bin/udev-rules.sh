#!/bin/sh

# You can safely redirect output of this file to file:
#
#   /etc/udev/rules.d/70-persistent-net.rules
#
# To use a more stable net device map rules, especially for VM.

show_device_rules_header()
{
	cat <<END
# Default udev rules file: /etc/udev/rules.d/70-persistent-net.rules
# using MAC address to bind a fixed device name (such as eth0, eth1).
# It's better using pci device to map ether, especially for
# virtual machines.

END
}

show_device_rules()
{
	dir=$1
	device=$(basename $dir)
	pci=$(basename $(readlink -f $dir/device))
	cat <<END
# Map PCI device $pci to ether $device
SUBSYSTEM=="net", SUBSYSTEMS=="pci", ACTION=="add", KERNELS=="$pci", NAME="$device"

END
}


show_device_rules_header

for dir in /sys/class/net/* ; do
	if [ -e $dir/device ] ; then
		show_device_rules "$dir"
	fi
done
