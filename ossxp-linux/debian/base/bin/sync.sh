#!/bin/sh
#set -x

SYNCFROM=/src/dir
SYNCTO=/dest/dir
LOGINNAME=ssh_login_user
SERVERNAME=remote_server
AUTHUSER=web_auth_login
AUTHPASS=web_auth_passwd

sync_with_winbox()
{
  echo "backup to winbox"
  MOUNTCMD="/mount/script.sh"
  MOUNTPOINT="/mount/point/dir/"
  SYNCTO=_backup
  
  if ! mount | grep -q $MOUNTPOINT; then
    UMOUNT=yes
    sh $MOUNTCMD || exit 1
  else
    UMOUNT=no
  fi
  
  if [ -d $MOUNTPOINT/$SYNCTO/ ]; then
    rdiff-backup -v5 --ignore-fs-abilities $SYNCFROM $MOUNTPOINT/$SYNCTO && \
       ( rdiff-backup --force --ignore-fs-abilities --remove-older-than 3M $MOUNTPOINT/$SYNCTO >/dev/null )
  else
    echo "Error: target not mount! rdiff-backup failed!"
  fi

  if [ "$UMOUNT" = "yes" ]; then
    umount $MOUNTPOINT
  fi
}

sync_with_linux()
{
  echo "backup to ${SERVERNAME}"
  curl -u ${AUTHUSER}:${AUTHPASS} http://${SERVERNAME}/ssh_open/ && \
  rdiff-backup -v5 --ignore-fs-abilities ${SYNCFROM} ${LOGINNAME}@${SERVERNAME}::/target/dir/
}

if [ $# -gt 0 ]; then
  case $1 in
    winbox)
      sync_with_winbox
   ;;
    linux)
      sync_with_linux
      ;;
  esac
else
  sync_with_winbox
  sync_with_linux
fi
