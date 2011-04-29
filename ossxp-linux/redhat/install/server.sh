#!/bin/sh -e
# include apt maintainance functions
. /opt/ossxp/install/myyum.inc

[ "$(echo -e)" = "-e" ] && ECHO="echo" || ECHO="echo -e"

is_prefork_mode()
{
    VER=$(LC_ALL=C apt-cache policy ossxp-apache2-mpm-prefork 2>/dev/null | grep Installed  -n | cut -d":" -f3 | sed -e 's/ //g')
    if [ -n "$VER" ] && [ "$VER" != "(none)" ]; then
        return 0
    fi

    VER=$(LC_ALL=C apt-cache policy ossxp-php5-common-prefork 2>/dev/null | grep Installed  -n | cut -d":" -f3 | sed -e 's/ //g')
    if [ -n "$VER" ] && [ "$VER" != "(none)" ]; then
        return 0
    fi

    return 1
}


usage()
{
    $ECHO "Usage:"
    $ECHO "    $SCRIPTNAME [--prefork|--worker] [--install|--uninstall] <server> ..."
    $ECHO "Available Servers:"
    $ECHO "    lamp --- mysql & apache & php"
    $ECHO "    apache"
    $ECHO "    php"
    $ECHO "    svn"
    $ECHO "    mailman"
    $ECHO "    mantis"
    $ECHO "    moin"
    $ECHO "    mwiki"
    $ECHO "    gosa"
    $ECHO "    docbook"
    $ECHO "    phpbb"
    $ECHO "Current PoW state: $PoW_MODE"
    exit 1
}


real_actions()
{
    PACKAGES=

    if [ "$PoW_MODE" = "--prefork" ]; then
	MAIN_PACKAGES=$($ECHO $MAIN_PACKAGES | sed -e 's/@@PoW@@/-prefork/g')
	UNINST_PACKAGES=$($ECHO $UNINST_PACKAGES | sed -e 's/@@PoW@@/-prefork/g')
	INST_PACKAGES=$($ECHO $INST_PACKAGES | sed -e 's/@@PoW@@/-prefork/g')
    else
	MAIN_PACKAGES=$($ECHO $MAIN_PACKAGES | sed -e 's/@@PoW@@/-worker/g')
	UNINST_PACKAGES=$($ECHO $UNINST_PACKAGES | sed -e 's/@@PoW@@/-worker/g')
	INST_PACKAGES=$($ECHO $INST_PACKAGES | sed -e 's/@@PoW@@/-worker/g')
    fi

    if [ "$UNINSTALL" = "yes" ]; then
        PACKAGES="$MAIN_PACKAGES $UNINST_PACKAGES"
    else
        PACKAGES="$MAIN_PACKAGES $INST_PACKAGES"
    fi
    $INSTALLCMD $PACKAGES
}


inst_apache()
{
    if [ "$PoW_MODE" = "--prefork" ]; then
	MAIN_PACKAGES="ossxp-apache2-mpm-prefork ossxp-apache2.2-common 
	               ossxp-apache2-doc
                       ossxp-apache2-utils ossxp-apache2"
       	UNINST_PACKAGES="ossxp-apache2-prefork-dev"
	INST_PACKAGES=
    else
	MAIN_PACKAGES="ossxp-apache2-mpm-worker ossxp-apache2.2-common 
	               ossxp-apache2-doc
                       ossxp-apache2-utils ossxp-apache2"
       	UNINST_PACKAGES="ossxp-apache2-threaded-dev"
	INST_PACKAGES=
    fi
    real_actions
}


inst_gosa()
{
    MAIN_PACKAGES="ossxp-gosa ossxp-gosa-schema ossxp-ldap"
    INST_PACKAGES="
            ossxp-php5-imap@@PoW@@ ossxp-php5-imap
	    ossxp-php5-ldap@@PoW@@ ossxp-php5-ldap
            ossxp-php5-mhash@@PoW@@ ossxp-php5-mhash
            ossxp-php5-recode@@PoW@@ ossxp-php5-recode
	    "
    UNINST_PACKAGES=""
    real_actions
}


inst_docbook()
{
    MAIN_PACKAGES="ossxp-docbook"
    INST_PACKAGES=
    UNINST_PACKAGES=
    real_actions
}


inst_php()
{
    MAIN_PACKAGES="
	    ossxp-php5-common@@PoW@@ ossxp-php5-common 
	    ossxp-libapache2-mod-php5@@PoW@@ ossxp-libapache2-mod-php5 
	    ossxp-php5-cgi@@PoW@@ ossxp-php5-cgi 
	    ossxp-php5-cli@@PoW@@ ossxp-php5-cli 
	    ossxp-php5@@PoW@@ ossxp-php5 
	    ossxp-php5-gd@@PoW@@ ossxp-php5-gd 
	    ossxp-php5-mysql@@PoW@@ ossxp-php5-mysql 
	    ossxp-php-pear"
    UNINST_PACKAGES="
	    ossxp-libphp-jpgraph ossxp-jpgraph
	    ossxp-smarty ossxp-smarty-gettext
	    ossxp-php-auth ossxp-php-auth-sasl
	    ossxp-php-db ossxp-php-http ossxp-php-log
            ossxp-php-mail ossxp-php-mail-mime 
	    ossxp-php-net-smtp ossxp-php-net-socket 
	    ossxp-php-xml-parser
	    ossxp-php-versioncontrol-svn
            ossxp-php5@@PoW@@-dev ossxp-php5-dev
            ossxp-php5-curl@@PoW@@ ossxp-php5-curl
	    ossxp-php5-gmp@@PoW@@ ossxp-php5-gmp
            ossxp-php5-imap@@PoW@@ ossxp-php5-imap
	    ossxp-php5-interbase@@PoW@@ ossxp-php5-interbase
	    ossxp-php5-ldap@@PoW@@ ossxp-php5-ldap
	    ossxp-php5-mcrypt@@PoW@@ ossxp-php5-mcrypt
            ossxp-php5-mhash@@PoW@@ ossxp-php5-mhash
            ossxp-php5-odbc@@PoW@@ ossxp-php5-odbc
            ossxp-php5-pgsql@@PoW@@ ossxp-php5-pgsql
            ossxp-php5-pspell@@PoW@@ ossxp-php5-pspell
            ossxp-php5-recode@@PoW@@ ossxp-php5-recode
            ossxp-php5-snmp@@PoW@@ ossxp-php5-snmp
            ossxp-php5-sqlite@@PoW@@ ossxp-php5-sqlite
            ossxp-php5-sybase@@PoW@@ ossxp-php5-sybase
            ossxp-php5-tidy@@PoW@@ ossxp-php5-tidy
            ossxp-php5-xmlrpc@@PoW@@ ossxp-php5-xmlrpc
            ossxp-php5-xsl@@PoW@@ ossxp-php5-xsl
	    "
    INST_PACKAGES=

    real_actions
}


inst_svn()
{
    MAIN_PACKAGES="ossxp-libsvn1 ossxp-libapache2-svn ossxp-libsvn-doc 
            ossxp-subversion ossxp-subversion-tools 
            ossxp-libsvn-perl ossxp-python-subversion 
            ossxp-svn-client ossxp-svn-server"
    INST_PACKAGES=
    UNINST_PACKAGES=
    real_actions
}


inst_mailman()
{
    MAIN_PACKAGES="ossxp-mailman"
    INST_PACKAGES=
    UNINST_PACKAGES=
    real_actions
}


inst_mysql()
{
    MAIN_PACKAGES="mysql-server"
    INST_PACKAGES=
    UNINST_PACKAGES=
    real_actions
}


inst_mwiki()
{
    MAIN_PACKAGES="ossxp-mediawiki ossxp-mediawiki-math"
    INST_PACKAGES=
    UNINST_PACKAGES=ossxp-mediawiki-style-worldhello
    real_actions
}


inst_mantis()
{
    MAIN_PACKAGES="ossxp-mantis"
    INST_PACKAGES=ossxp-linux-fonts
    UNINST_PACKAGES=ossxp-mantis-theme-worldhello
    real_actions
}


inst_moin()
{
    MAIN_PACKAGES="ossxp-libapache2-mod-fastcgi 
        ossxp-libapache2-mod-python 
	ossxp-moinmoin"
    INST_PACKAGES=
    UNINST_PACKAGES=
    real_actions
}


inst_phpbb()
{
    MAIN_PACKAGES="ossxp-phpbb 
	ossxp-phpbb-avatars 
        ossxp-phpbb-language-zh 
        ossxp-phpbb-smiles"
    INST_PACKAGES=
    UNINST_PACKAGES=ossxp-phpbb-style-worldhello
    real_actions
}

########################################
# main function here:
########################################

if [ `id -u` -ne 0 ]; then
  $ECHO "you must be root to run this script!"
  exit 1
fi

SCRIPTNAME=`basename $0`
if is_prefork_mode ; then
    PoW_MODE="--prefork"
else
    PoW_MODE="--worker"
fi
INSTALLCMD="install_packages -i"
UNINSTALL=
PURGE=


[ $# -eq 0 ] && usage
while [ $# -gt 0 ]; do
    case $1 in
    --prefork)
        PoW_MODE=$1
        ;;

    --install)
        UNINSTALL=
        ;;

    --uninstall)
        UNINSTALL="yes"
        ;;

    --purge)
        UNINSTALL="yes"
        PURGE="yes"
        ;;

    --thread|--worker)
        PoW_MODE=$1
        ;;

    -*)
        $ECHO "[1mError: unknown option: $1[0m"
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

    moin|moinmoin)
    	cmd_moin=1
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
        $ECHO "[1mError: unknown command: $1[0m"
        usage
        ;;
    esac
    shift
done

if [ "$UNINSTALL" != "yes" ]; then
	INSTALLCMD="install_packages -i"
	[ ! -z $cmd_mysql   ] && inst_mysql
	[ ! -z $cmd_apache  ] && inst_apache
	[ ! -z $cmd_php     ] && inst_php
	[ ! -z $cmd_svn     ] && inst_svn
	[ ! -z $cmd_mailman ] && inst_mailman
	[ ! -z $cmd_mantis  ] && inst_mantis
	[ ! -z $cmd_mwiki   ] && inst_mwiki
	[ ! -z $cmd_moin    ] && inst_moin
	[ ! -z $cmd_phpbb   ] && inst_phpbb
	[ ! -z $cmd_docbook ] && inst_docbook
	[ ! -z $cmd_gosa    ] && inst_gosa
elif [ "$UNINSTALL" = "yes" ]; then
	if [ "$PURGE" = "yes" ]; then
		INSTALLCMD="uninstall_packages --purge"
	else
		INSTALLCMD="uninstall_packages"
	fi

	if [ ! -z $cmd_apache ]; then
		cmd_php=1
		cmd_svn=1
		cmd_mailman=1
		cmd_moin=1
	fi
	if [ ! -z $cmd_php ]; then
		cmd_mantis=1
		cmd_mwiki=1
		cmd_phpbb=1
		cmd_gosa=1
	fi

	[ ! -z $cmd_docbook ] && inst_docbook
	[ ! -z $cmd_gosa    ] && inst_gosa
	[ ! -z $cmd_mantis  ] && inst_mantis
	[ ! -z $cmd_mwiki   ] && inst_mwiki
	[ ! -z $cmd_phpbb   ] && inst_phpbb
	[ ! -z $cmd_svn     ] && inst_svn
	[ ! -z $cmd_mailman ] && inst_mailman
	[ ! -z $cmd_php     ] && inst_php
	[ ! -z $cmd_moin    ] && inst_moin
	[ ! -z $cmd_apache  ] && inst_apache
	[ ! -z $cmd_mysql   ] && inst_mysql
fi
