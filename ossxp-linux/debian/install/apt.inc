
########################################
# install packages only necessary
########################################
function install_packages()
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


