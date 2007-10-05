#!/bin/sh -e

# include apt maintainance functions
. ./apt.inc

[ -x /bin/echo ] && alias echo=/bin/echo

if [ `id -u` -ne 0 ]; then
  echo "you must be root to run this script!"
  exit 1
fi

SCRIPTNAME=`basename $0`
TYPE="--prefork"

function usage()
{
    echo "Usage:"
    echo "    $SCRIPTNAME [--prefork|--thread] <server> ..."
    echo "Available Servers:"
    echo "    apache"
    echo "    php"
    echo "    subversion|svn"
    echo "    mailman"
    echo "    mantis"
    exit 1
}

function inst_apache
{
    if [ "$TYPE" = "--prefork" ]; then
        install_packages \
            ossxp-apache2-mpm-prefork ossxp-apache2-doc \
            ossxp-apache2 
    else
        install_packages \
            ossxp-apache2-mpm-worker ossxp-apache2-doc \
            ossxp-apache2 
    fi
}

function inst_php
{
    if [ "$TYPE" = "--prefork" ]; then
        install_packages \
            ossxp-php5-common ossxp-libapache2-mod-php5 \
            ossxp-php5-cgi ossxp-php5-cli ossxp-php5 \
            ossxp-php5-gd ossxp-php5-mysql 
    else
        install_packages \
            ossxp-php5-common-mt ossxp-libapache2-mod-php5-mt \
            ossxp-php5-cgi-mt ossxp-php5-cli-mt ossxp-php5-mt \
            ossxp-php5-gd-mt ossxp-php5-mysql-mt 
    fi
}

function inst_svn
{
    if [ "$TYPE" = "--prefork" ]; then
        install_packages \
            ossxp-libsvn1 ossxp-libapache2-svn ossxp-libsvn-doc \
            ossxp-subversion ossxp-subversion-tools ossxp-python-subversion 
    else
        install_packages \
            ossxp-libsvn1 ossxp-libapache2-svn ossxp-libsvn-doc \
            ossxp-subversion ossxp-subversion-tools ossxp-python-subversion 
    fi
}

function inst_mailman
{
    install_packages \
        ossxp-mailman 
}

function inst_mantis
{
    install_packages \
        ossxp-mantis 
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
        usage
        ;;
    *)
        SERVERS="$SERVERS $1"
    esac
    shift
done

for srv in $SERVERS; do
    case $srv in
    apache)
        inst_apache
        ;;

    php)
        sh $0 $TYPE apache
        inst_php
        ;;

    subversion|svn)
        sh $0 $TYPE apache
        inst_svn
        ;;

    mailman)
        sh $0 $TYPE apache
        inst_mailman
        ;;

    mantis)
        sh $0 $TYPE php
        inst_mantis
        ;;

    *)
        usage
        ;;
    esac
done

