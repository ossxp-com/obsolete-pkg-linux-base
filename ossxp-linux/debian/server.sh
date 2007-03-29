#!/bin/sh -e

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
        for pkg in \
            ossxp-apache2-mpm-prefork ossxp-apache2-doc \
            ossxp-apache2 \
        ; do
            echo -e "[1minstall $pkg :[0m"
            apt-get install --force-yes -y $pkg || echo -e "[1m[44minstall $pkg failed! [0m"
        done
    else
        for pkg in \
            ossxp-apache2-mpm-worker ossxp-apache2-doc \
            ossxp-apache2 \
        ; do
            echo -e "[1minstall $pkg :[0m"
            apt-get install --force-yes -y $pkg || echo -e "[1m[44minstall $pkg failed! [0m"
        done
    fi
}

function inst_php
{
    if [ "$TYPE" = "--prefork" ]; then
        for pkg in \
            ossxp-php5-common ossxp-libapache2-mod-php5 \
            ossxp-php5-cgi ossxp-php5-cli ossxp-php5 \
            ossxp-php5-gd ossxp-php5-mysql \
        ; do
            echo -e "[1minstall $pkg :[0m"
            apt-get install --force-yes -y $pkg || echo -e "[1m[44minstall $pkg failed! [0m"
        done
    else
        for pkg in \
            ossxp-php5-common-mt ossxp-libapache2-mod-php5-mt \
            ossxp-php5-cgi-mt ossxp-php5-cli-mt ossxp-php5-mt \
            ossxp-php5-gd-mt ossxp-php5-mysql-mt \
        ; do
            echo -e "[1minstall $pkg :[0m"
            apt-get install --force-yes -y $pkg || echo -e "[1m[44minstall $pkg failed! [0m"
        done
    fi
}

function inst_svn
{
    if [ "$TYPE" = "--prefork" ]; then
        for pkg in \
            ossxp-libsvn1 ossxp-libapache2-svn ossxp-libsvn-doc \
            ossxp-subversion ossxp-subversion-tools ossxp-python-subversion \
        ; do
            echo -e "[1minstall $pkg :[0m"
            apt-get install --force-yes -y $pkg || echo -e "[1m[44minstall $pkg failed! [0m"
        done
    else
        for pkg in \
            ossxp-libsvn1 ossxp-libapache2-svn ossxp-libsvn-doc \
            ossxp-subversion ossxp-subversion-tools ossxp-python-subversion \
        ; do
            echo -e "[1minstall $pkg :[0m"
            apt-get install --force-yes -y $pkg || echo -e "[1m[44minstall $pkg failed! [0m"
        done
    fi
}

function inst_mailman
{
    for pkg in \
        ossxp-mailman \
    ; do
            echo -e "[1minstall $pkg :[0m"
            apt-get install --force-yes -y $pkg || echo -e "[1m[44minstall $pkg failed! [0m"
    done
}

function inst_mantis
{
    for pkg in \
        ossxp-mantis \
    ; do
            echo -e "[1minstall $pkg :[0m"
            apt-get install --force-yes -y $pkg || echo -e "[1m[44minstall $pkg failed! [0m"
    done
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

