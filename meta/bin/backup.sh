#!/bin/bash
#
#************************************************************
# CopyLight 2002,2003 WorldHello.Net
# Auther: Jiang Xin
# $Id: backup.sh,v 1.17 2003/01/14 14:26:32 jiangxin Exp $
# 2002/03/21 08:46:29
# 1.28
#************************************************************

set -e
export PATH=/usr/bin:/usr/local/bin:/usr/sbin:/usr/local/sbin:/bin:/sbin

is_batch="no"

NO_YES()
{
	local input

	HIECHO -nocr -b -b "$*? [n]"
	[ ! -t ] && return 1 || true
	[ "x$is_batch" = "xyes" ] && return 1 || true

	read input
	case x$input in
	x)	return 1;;
	x[Yy])	return 0;;
	*)	return 1;;
	esac
}


YES_NO()
{
	local input

	HIECHO -nocr -b -b "$*? [y]"
	[ ! -t ] && return 0 || true
	[ "x$is_batch" = "xyes" ] && return 0 || true
	
	read input
	case x$input in
	x)	return 0;;
	x[Yy])	return 0;;
	*)	return 1;;
	esac
}


HIECHO()
{
	local sty1 sty0 embegin emend ps cr back wall
	
	embegin="\033[1m"
	emend="\033[0m"
	sty0="\033[40;37m"
	sty1="\033[47;34m"
	log1=""
	log2=""
	wall="no"

	ps="`date +%Y%m%d.%H%M%S`> "
	cr=""
	back=""
	
	while [ $# -gt 0 ]; do
		case $1 in
		-plain)
			sty0=""
			sty1=""
			embegin=""
			emend=""
			shift
			;;
		-noem)
			embegin=""
			emend=""
			shift
			;;
		-nocolor|-sty0)
			sty0=""
			sty1=""
			shift
			;;
		-color1|-sty1)
			sty1="\033[47;34m"
			shift
			;;
		-color2|-sty2)
			sty1="\033[47;31m"
			shift
			;;
		-nops)
			ps=""
			shift
			;;
		-nocr)
			cr="\c"
			shift
			;;
		-b|-back)
			back="${back}\b"
			shift
			;;
		-cr)
			cr="\n\n"
			shift
			;;
		-wall)
			wall="yes"
			shift
			;;
		*)
			break
			;;
		esac
	done
			
	if [ "x$wall" = "xyes" ]; then
		banner $* | wall
	else
		echo -e "${embegin}${sty1}${ps}$*${sty0}${emend}${back}${cr}"
	fi
}


PAUSE()
{
	local input

	if [ $# -ne 0 ]; then
		HIECHO -nops -nocolor $*
	fi
	[ ! -t ] && return 0 || true
	[ "x$is_batch" = "xyes" ] && return 0 || true
	
	HIECHO -nocr -nocolor -nops "press <enter> to quit!"
	read input
}


PAUSEE()
{
	local input

	if [ $? -eq 0 ]; then
		if [ $# -ne 0 ]; then
			HIECHO -nops -nocolor $*
		fi
		[ ! -t ] && return 0 || true
		[ "x$is_batch" = "xyes" ] && return 0 || true
		
		HIECHO -nocr -nocolor -nops "press <enter> to quit!"
		read input
	fi
}


PAUSENE()
{
	local input

	if [ $? -ne 0 ]; then
		if [ $# -ne 0 ]; then
			HIECHO -nops -nocolor $*
		fi
		[ ! -t ] && return 0
		[ "x$is_batch" = "xyes" ] && return 0 || true
		
		HIECHO -nocr -nocolor -nops "press <enter> to quit!"
		read input
	fi
}


EXIT_ERROR()
{
	local args
	
	while [ $# -gt 0 ]; do
		case $1 in
		-*)
			args="$args $1"
			shift
			;;
		*)
			break
			;;
		esac
	done
	
	HIECHO $args "\n---------------- FAILED ----------------------"
	PAUSE $args $*
	exit 1
}


EXIT_SUCC()
{
	if [ $# -ne 0 ]; then
			HIECHO "$*\n\n"
	fi
	exit 0
}



fn_usage()
{
local prog
prog=`basename $0`
cat << EOF
Backup Utility from WorldHello.Net
==================================
\$Id: backup.sh,v 1.17 2003/01/14 14:26:32 jiangxin Exp $
Synopsis:
	$prog [-h|-V|-l] [-full|-inc] -s <src_dir> -d <dest_dir>

Examples:
	* Full backup:
	  Backup files in /my/documents/ to /opt/backup/

		$prog -f -s /my/documents/ -d /opt/backup/

	* Increment backup:
	  Do an increment backup, from /my/documents/ to /opt/backup/

		$prog -i -s /my/documents/ -d /opt/backup/

	* Show backup history:

		$prog -l

	* Help. (This screen):

		$prog -h

	* Shwo version:

		$prog -V

EOF
	exit 0
}


fn_version()
{
	echo "Version : \$Revision: 1.17 $"
	exit 0
}


fn_backup()
{
	local source target method history tempstr tsstring
	method="inc"

	if [ -z "$HISTORY_FILE" ]; then
		history="/var/log/.backup_history"
	else
		history="$HISTORY_FILE"
	fi
	if [ ! -f $history ]; then
		touch $history
	fi

	
	while [ $# -gt 0 ] ; do
		case $1 in 
		-h|-help)
			fn_usage
			shift
			;;
		-[vV])
			fn_version
			shift
			;;
		-l)
			HIECHO "Backup Log"
			cat $history
			shift
			exit 0
			;;
		-s)
			shift
			source="$1"
			source=${source%/}
			shift
			;;
		-d)
			shift
			target="$1"
			target=${target%/}
			shift
			;;
		-i|-inc)
			shift
			method="inc"
			;;
		-f|-full)
			shift
			method="full"
			;;
		*)
			fn_usage
			shift
			;;
		esac
	done

	success="yes"

	[ -z "$source" ] && fn_usage
	[ -z "$target" ] && fn_usage
	[ -z "$method" ] && fn_usage
	
	PREFIX="`basename $source`_"
	TODAY=`date "+%y%m%d"`

	target="$target/$TODAY"
	[ "$method" = "full" ] &&  target="${target}_full"

	# test input
	[ ! -d $source ] && EXIT_ERROR "backup source dir does not exist!"
	[ ! -d $target ] && mkdir -p $target

	# get last backup timestamp of $source from timestamp string of $history
	tsstring="`grep "$source" $history  || true`"
	tsstring=${tsstring#$source:}
	ts_last="`echo $tsstring | awk -F : '{print $1;} ' | sed -e "s/[a-zA-Z]//g"`"
	if [ -z "$ts_last" ]; then
		ts_last="200101010101.01"
	fi
	LASTDATETIME=`echo $ts_last |awk '{str=$0; printf ("%s/%s/%s %s:%s:%s", substr(str,1,4), substr(str,5,2), substr(str,7,2), substr(str,9,2), substr(str,11,2), substr(str,14,2));}'`
	
	# prepare new timestamp string of $source
	ts_new=`date "+%Y%m%d%H%M.%S"`
	tsstring="`echo $tsstring | awk -F : '{printf "%s:%s:%s:%s:%s:%s:%s:%s",$1,$2,$3,$4,$5,$6,$7,$8}'`"

	if [ "$method" = "full" ]; then
		# make full backup
		tsstring="$source:${ts_new}f:$tsstring"
		
		temp=0
		for i in `ls ${target}/${PREFIX}${TODAY}_*.full.t* 2>/dev/null || true` ; do
			tempstr=`echo ${target} | sed -e 's/\//\\\\\//g' `
			tempnum=`echo $i | sed  -e 's/.full.tar.gz//g' -e 's/.full.tar//g' -e 's/.full.tgz//g' -e "s/${tempstr}\///g" -e "s/${PREFIX}${TODAY}_//g" -e 's/\.md5//'`
			if [ ${tempnum} -gt ${temp} ]; then
				temp=${tempnum}
			fi
		done
		temp=`expr ${temp} + 1`
		BACKUPFILE="${target}/${PREFIX}${TODAY}_${temp}.full.tar.gz"

		HIECHO -nocr -nops "Backup ${source} into ${BACKUPFILE}...	"
		tar -zchvf ${BACKUPFILE} ${source}  >/dev/null 2>&1 || success="no"
		if [ "$success" = "no" ]; then
			echo "" && HIECHO -nops "	no file need to backup"
		else
			( cd `dirname $BACKUPFILE`; md5 `basename $BACKUPFILE` > `basename $BACKUPFILE`.md5 )
		fi
		HIECHO -nops "done"
	elif [ "$method" = "inc" ]; then
		# make increment backup
		tsstring="$source:${ts_new}i:$tsstring"

		temp=0
		for i in `ls ${target}/${PREFIX}${TODAY}_*.inc.t* 2>/dev/null || true` ; do
			tempstr=`echo ${target} | sed -e 's/\//\\\\\//g' `
			tempnum=`echo $i | sed  -e 's/.inc.tar.gz//g' -e 's/.inc.tar//g' -e 's/.inc.tgz//g' -e "s/${tempstr}\///g" -e "s/${PREFIX}${TODAY}_//g" -e 's/\.md5//'`
			if [ ${tempnum} -gt ${temp} ]; then
				temp=${tempnum}
			fi
		done
		temp=`expr ${temp} + 1`
		BACKUPFILE="${target}/${PREFIX}${TODAY}_${temp}.inc.tar.gz"
		
		# find and tar file newer than last_backup in $source
		HIECHO -nocr -nops "Backup files into ${BACKUPFILE}...	"
		TMPFILE=`mktemp -q /tmp/backup_ts.XXXXXXXXXX`
		tar -zcv --newer-mtime="$LASTDATETIME" -f ${BACKUPFILE} ${source} >$TMPFILE
		grep -q "[^/]\+$" $TMPFILE || success="no"
		rm -f $TMPFILE
		
		if [ "$success" = "no" ]; then
			echo "" && HIECHO -nops "	no file need to backup"
			rm -f ${BACKUPFILE}
		else
			( cd `dirname ${BACKUPFILE}`; md5 `basename ${BACKUPFILE}` > `basename ${BACKUPFILE}`.md5 )
		fi

		HIECHO -nops "done"
	
	else
		EXIT_ERROR "unknow backup method : $method !"
	fi

	# update history file using the prepared timestamp string : $tsstring
	if [ "$success" != "no" ]; then
		TMPFILE=`mktemp -q /tmp/backup_history.XXXXXXXXXX`
		tempstr=`echo ${source} | sed -e 's/\//\\\\\//g' `
		sed -e "/$tempstr/d" $history > $TMPFILE
		echo $tsstring >> $TMPFILE
		mv -f $TMPFILE $history
	fi	
}

############################## end function decalre ##########################

HISTORY_FILE="/var/log/.backup_history"

fn_backup $*

