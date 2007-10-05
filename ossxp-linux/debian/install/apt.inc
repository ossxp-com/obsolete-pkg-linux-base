
########################################
# install packages only necessary
########################################
function install_packages()
{
    unknown_list=
    upgrade_list=
    ignore_list=

    if [ $# -eq 1 ] && [ "$1" = "-" ] ; then
        packages=
        while read item; do
	    if [ "$item" != "-" ]; then
	        packages="$packages $item"
	    fi
	done
	install_packages $packages
	return 
    elif [ $# -gt 0 ]; then
        while [ $# -gt 0 ]; do
		INSTALLED=$(LC_ALL=C apt-cache policy $1 2>/dev/null | grep Installed  -n | cut -d":" -f3)
		CANDIDATE=$(LC_ALL=C apt-cache policy $1 2>/dev/null | grep Candidate  -n | cut -d":" -f3)
		if [ -z "$CANDIDATE" ]; then
		    unknown_list="$unknown_list $1"
		elif [ "$CANDIDATE" != "$INSTALLED" ]; then
		    upgrade_list="$upgrade_list $1"
		else
		    ignore_list="$ignore_list $1"
		fi
		shift
        done
    fi

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
        apt-get install --force-yes -y $upgrade_list || echo -e "[1m[44minstall failed! [0m"
        echo ""
    fi
}


