#!/bin/sh -e

# include apt maintainance functions
. /opt/ossxp/install/apt.inc

[ -x /bin/echo ] && alias echo=/bin/echo

if [ `id -u` -ne 0 ]; then
  echo "you must be root to run this script!"
  exit 1
fi

SCRIPTNAME=`basename $0`
TYPE="--thread"
INSTALLCMD="install_packages -i"

function usage()
{
    echo "Usage:"
    echo "    $SCRIPTNAME [--prefork|--thread] <server> ..."
    echo "Available Servers:"
    echo "    lamp --- mysql & apache & php"
    echo "    apache"
    echo "    php"
    echo "    svn"
    echo "    mailman"
    echo "    mantis"
    echo "    mwiki"
    echo "    gosa"
    echo "    docbook"
    echo "    phpbb"
    exit 1
}


function inst_apache
{
    if [ "$TYPE" = "--prefork" ]; then
        $INSTALLCMD \
            ossxp-apache2-mpm-prefork ossxp-apache2-doc \
            ossxp-apache2 
    else
        $INSTALLCMD \
            ossxp-apache2-mpm-worker ossxp-apache2-doc \
            ossxp-apache2 
    fi
}


function inst_gosa
{
    $INSTALLCMD \
            ossxp-gosa ossxp-gosa-schema ossxp-ldap
}


function inst_docbook
{
    $INSTALLCMD \
            ossxp-docbook
}


function inst_php
{
    if [ "$TYPE" = "--prefork" ]; then
        $INSTALLCMD \
            ossxp-php5-common ossxp-libapache2-mod-php5 \
            ossxp-php5-cgi ossxp-php5-cli ossxp-php5 \
            ossxp-php5-gd ossxp-php5-mysql 
    else
        $INSTALLCMD \
            ossxp-php5-common-mt ossxp-libapache2-mod-php5-mt \
            ossxp-php5-cgi-mt ossxp-php5-cli-mt ossxp-php5-mt \
            ossxp-php5-gd-mt ossxp-php5-mysql-mt 
    fi
}


function inst_svn
{
    $INSTALLCMD \
            ossxp-libsvn1 ossxp-libapache2-svn ossxp-libsvn-doc \
            ossxp-subversion ossxp-subversion-tools ossxp-python-subversion \
            ossxp-svn-client ossxp-svn-server
}


function inst_mailman
{
    $INSTALLCMD \
        ossxp-mailman 
}


function inst_mysql
{
    $INSTALLCMD \
        mysql-server
}


function inst_mwiki
{
    $INSTALLCMD \
        ossxp-mediawiki ossxp-mediawiki-math
        # ossxp-mediawiki-style-worldhello
}


function inst_mantis
{
    $INSTALLCMD \
        ossxp-mantis ossxp-linux-fonts 
	# ossxp-mantis-theme-worldhello
}


function inst_phpbb
{
    $INSTALLCMD \
        ossxp-phpbb \
	ossxp-phpbb-avatars \
        ossxp-phpbb-language-zh \
        ossxp-phpbb-smiles 
        # ossxp-phpbb-style-worldhello
}

########################################
# main function here:
########################################

[ $# -eq 0 ] && usage
while [ $# -gt 0 ]; do
    case $1 in
    --prefork)
        TYPE=$1
        ;;

    --thread|--mpm|--worker)
        TYPE=$1
        ;;
    -*)
        echo -e "[1mError: unknown option: $1[0m"
        usage
        ;;

    lamp)
        cmd_mysql=1
        cmd_apache=1
        cmd_php=1
        ;;

    apache)
        cmd_apache=1
        ;;

    php)
        cmd_php=1
        ;;

    subversion|svn)
        cmd_svn=1
        ;;

    mailman)
	cmd_mailman=1
        ;;

    mantis)
        cmd_mantis=1
        ;;

    mwiki)
        cmd_mwiki=1
        ;;

    gosa)
        cmd_gosa=1
        ;;

    docbook)
        cmd_docbook=1
        ;;

    phpbb)
        cmd_phpbb=1
        ;;

    *)
        echo -e "[1mError: unknown command: $1[0m"
        usage
        ;;
    esac
    shift
done

[ ! -z $cmd_mysql   ] && inst_mysql
[ ! -z $cmd_apache  ] && inst_apache
[ ! -z $cmd_php     ] && inst_php
[ ! -z $cmd_svn     ] && inst_svn
[ ! -z $cmd_mailman ] && inst_mailman
[ ! -z $cmd_mantis  ] && inst_mantis
[ ! -z $cmd_mwiki   ] && inst_mwiki
[ ! -z $cmd_phpbb   ] && inst_phpbb
[ ! -z $cmd_docbook ] && inst_docbook
[ ! -z $cmd_gosa    ] && inst_gosa

