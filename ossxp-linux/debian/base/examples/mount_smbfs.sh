#!/bin/bash

USER=USERNAME
PASS=PASSWORD
UNIXID=$USER
SERVER="10.0.0.5"
SHARE="e\$"
MOUNTPOINT=/mnt

sudo mount -t smbfs -o "username=$USER,password=$PASS,uid=$UNIXID,iocharset=utf8,codepage=cp936,lfs" "//$SERVER/$SHARE" "$MOUNTPOINT" &

sleep 3

