########################################
# install packages only necessary
########################################
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
        echo -e "[1mAlready installed packages :[0m"
        echo $ignore_list
        echo ""
    fi
    if [ ! -z "$unknown_list" ]; then
        echo -e "[1mWarning: Not exist packages found : [0m"
        echo $unknown_list
        echo ""
    fi
    if [ -z "$upgrade_list" ]; then
        echo -e "[1mNothing will be installed or upgraded.[0m"
        echo ""
    else
        echo -e "[1mFollowing packages will be installed :[0m"
        echo $upgrade_list
        read -p "Press any key ..." -s -n1
        echo ""
	if [ "$interactive" = "yes" ]; then
            apt-get install $upgrade_list || echo -e "[1m[44minstall failed! [0m"
	else
            apt-get install --force-yes -y $upgrade_list || echo -e "[1m[44minstall failed! [0m"
	fi
        echo ""
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
        echo -e "Packages not yet installed :"
        echo $ignore_list
        echo ""
    fi
    if [ -z "$delete_list" ]; then
        echo -e "Nothing will be uninstalled."
        echo ""
    else
	if [ "$purgemode" = "yes" ]; then
          echo -e "[1mFollowing packages will be purged:[0m"
	else
          echo -e "[1mFollowing packages will be uninstalled:[0m"
	fi
        echo $delete_list
        read -p "Press any key ..." -s -n1
        echo ""
	if [ "$dryrun" = "yes" ]; then
            dpkg --dry-run --remove $delete_list
	elif [ "$purgemode" = "yes" ]; then
            dpkg --purge $delete_list || echo -e "[1m[44minstall failed! [0m"
	else
            dpkg --remove $delete_list || echo -e "[1m[44minstall failed! [0m"
	fi
        echo ""
    fi
}


