########################################
# install packages only necessary
########################################

[ "$(echo -e)" = "-e" ] && ECHO="echo" || ECHO="echo -e"

install_packages()
{
    unknown_list=
    upgrade_list=
    ignore_list=
    interactive="no"
    packages=

    while [ $# -gt 0 ]; do
        if [ "$1" = "-" ] ; then
		while read item; do
		    if [ "$item" != "-" ]; then
			packages="$packages $item"
		    fi
		done
	elif [ "$1" = "-i" ]; then
        	interactive="yes"
	else
		packages="$packages $1"
	fi
        shift
    done

    for item in $packages; do
	INSTALLED=$(LC_ALL=C apt-cache policy $item 2>/dev/null | grep Installed  -n | cut -d":" -f3)
	CANDIDATE=$(LC_ALL=C apt-cache policy $item 2>/dev/null | grep Candidate  -n | cut -d":" -f3)
	if [ -z "$CANDIDATE" ]; then
	    unknown_list="$unknown_list $item"
	elif [ "$CANDIDATE" != "$INSTALLED" ]; then
	    upgrade_list="$upgrade_list $item"
	else
	    ignore_list="$ignore_list $item"
	fi
    done

    if [ ! -z "$ignore_list" ]; then
        $ECHO "[1mAlready installed packages :[0m"
        $ECHO $ignore_list
        $ECHO ""
    fi
    if [ ! -z "$unknown_list" ]; then
        $ECHO "[1mWarning: Not exist packages found : [0m"
        $ECHO $unknown_list
        $ECHO ""
    fi
    if [ -z "$upgrade_list" ]; then
        $ECHO "[1mNothing will be installed or upgraded.[0m"
        $ECHO ""
    else
        $ECHO "[1mFollowing packages will be installed :[0m"
        $ECHO $upgrade_list
        read -p "Press any key ..." -s -n1
        $ECHO ""
	if [ "$interactive" = "yes" ]; then
            yum install $upgrade_list || $ECHO "[1m[44minstall failed! [0m"
	else
            yum install -y $upgrade_list || $ECHO "[1m[44minstall failed! [0m"
	fi
        $ECHO ""
    fi
}

########################################
# uninstall packages only necessary
########################################
uninstall_packages()
{
    delete_list=
    ignore_list=
    interactive="no"
    dryrun="no"
    packages=
    purgemode="no"

    while [ $# -gt 0 ]; do
        if [ "$1" = "-" ] ; then
		while read item; do
		    if [ "$item" != "-" ]; then
			packages="$packages $item"
		    fi
		done
	elif [ "$1" = "-n" ]; then
        	dryrun="yes"
	elif [ "$1" = "-i" ]; then
        	interactive="yes"
	elif [ "$1" = "--purge" ]; then
        	purgemode="yes"
	else
		packages="$packages $1"
	fi
        shift
    done

    for item in $packages; do
	INSTALLED=$(LC_ALL=C apt-cache policy $item 2>/dev/null | grep Installed  -n | cut -d":" -f3 | sed -e "s/ //g")
	#CANDIDATE=$(LC_ALL=C apt-cache policy $item 2>/dev/null | grep Candidate  -n | cut -d":" -f3)
	if [ -z "$INSTALLED" ]; then
	    ignore_list="$ignore_list $item"
	elif [ "$INSTALLED" = "(none)" ]; then
	    ignore_list="$ignore_list $item"
	else
	    delete_list="$delete_list $item"
	fi
    done

    if [ ! -z "$ignore_list" ]; then
        $ECHO "Packages not yet installed :"
        $ECHO $ignore_list
        $ECHO ""
    fi
    if [ -z "$delete_list" ]; then
        $ECHO "Nothing will be uninstalled."
        $ECHO ""
    else
	if [ "$purgemode" = "yes" ]; then
          $ECHO "[1mFollowing packages will be purged:[0m"
	else
          $ECHO "[1mFollowing packages will be uninstalled:[0m"
	fi
        $ECHO $delete_list
        read -p "Press any key ..." -s -n1
        $ECHO ""
	if [ "$dryrun" = "yes" ]; then
            dpkg --dry-run --remove $delete_list
	elif [ "$purgemode" = "yes" ]; then
            dpkg --purge $delete_list || $ECHO "[1m[44minstall failed! [0m"
	else
            rpm -e $delete_list || $ECHO "[1m[44minstall failed! [0m"
	fi
        $ECHO ""
    fi
}


