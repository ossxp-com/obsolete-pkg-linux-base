#!/bin/sh
#
# Port CA.sh from Tim Hudson, tjh@cryptsoft.com
# Using certtool form gnutls.
# Copyright Jiang Xin, 2011

CATOP=/etc/certtool
SERIAL_FILE=${CATOP}/sn/sn.txt
CAKEY=${CATOP}/private/cakey.pem
CAREQ=${CATOP}/ca/careq.pem
CACRT=${CATOP}/ca/cacert.pem
CERTTOOL=certtool
PROG=$(basename $0)

DAYS=3650

######################################
# functions
######################################

die()
{
	echo "Error: $*"
	exit 1
}

get_serial()
{
	[ -w ${SERIAL_FILE} ] || die "serial file not exist or can not modified. (${SERIAL_FILE})"
	SERIAL=$(tail -1 ${SERIAL_FILE})
	if [ "x${SERIAL}" = "x" ]; then
		SERIAL=1000
	fi
}

update_serial()
{
	SERIAL=$((${SERIAL}+1))
	echo $SERIAL > ${SERIAL_FILE}
}

dump_template()
{

	if [ $# -gt 0 ]; then
		DOMAIN_NAME="$1"
	else
		DOMAIN_NAME="YOUR.DOM.AIN"
	fi

	cat <<EOF
# X.509 Certificate options
#
# DN options

# The organization of the subject.
organization = "<Your_Organization_name>"

# The organizational unit of the subject.
unit = "R&D Dept."

# The locality of the subject.
locality = "Beijing"

# The state of the certificate owner.
state = "Beijing"

# The country of the subject. Two letter code.
country = CN

# The common name of the certificate owner.
cn = "${DOMAIN_NAME}"

# A user id of the certificate owner.
#uid = "clauper"

# If the supported DN OIDs are not adequate you can set
# any OID here.
# For example set the X.520 Title and the X.520 Pseudonym
# by using OID and string pairs.
#dn_oid = "2.5.4.12" "Dr." "2.5.4.65" "jackal"

# The serial number of the certificate
serial = ${SERIAL}

# In how many days, counting from today, this certificate will expire.
expiration_days = ${DAYS}

# X.509 v3 extensions

# A dnsname in case of a WWW server.
dns_name = "www.${DOMAIN_NAME}"
dns_name = "*.${DOMAIN_NAME}"

# An IP address in case of a server.
#ip_address = "192.168.1.1"

# An email in case of a person
email = "<Your_Email_Here>"

# An URL that has CRLs (certificate revocation lists)
# available. Needed in CA certificates.
#crl_dist_points = "http://www.getcrl.crl/getcrl/"

# Whether this is a CA certificate or not
#ca

# Whether this certificate will be used for a TLS client
tls_www_client

# Whether this certificate will be used for a TLS server
tls_www_server

# Whether this certificate will be used to sign data (needed
# in TLS DHE ciphersuites).
signing_key

# Whether this certificate will be used to encrypt data (needed
# in TLS RSA ciphersuites). Note that it is preferred to use different
# keys for encryption and signing.
encryption_key

# Whether this key will be used to sign other certificates.
#cert_signing_key

# Whether this key will be used to sign CRLs.
#crl_signing_key

# Whether this key will be used to sign code.
#code_signing_key

# Whether this key will be used to sign OCSP data.
#ocsp_signing_key

# Whether this key will be used for time stamping.
#time_stamping_key
EOF
}

usage()
{
		cat >&2 << EOF
Usage:
    $PROG --init
                      If CA not setup yet.

    $PROG --newkey
                      Step 1 to generate a new key/cert pair.

    $PROG --newreq <domain.name>
                      Step 2 to generate a new key/cert pair.

    $PROG --sign
                      Step 3 to generate a new key/cert pair.

    $PROG --verify
                      Show certs.
EOF
    exit 0
}

# Get initial serial number from SERIAL_FILE

TEMPLATE=new.txt
NEWKEY=new.key
NEWREQ=new.req
NEWCRT=new.crt

if [ $# -eq 0 ]; then usage ; fi

get_serial

while [ $# -gt 0 ]; do
case $1 in
-\?|-h|--help)
    usage
    exit 0
    ;;
-newreq|--newreq) 
    # create a req template file, go edit it.
    shift
    [ ! -f $NEWKEY ] && die "Key file ($NEWKEY) does not exit, run $PROG -newkey first."
    if [ ! -f $TEMPLATE ]; then
			dump_template $1 > $TEMPLATE
		fi

		echo "Now a EDITEMPLATEOR will startup to edit file $TEMPLATE..."
		echo "Press any key..."
		read
		vi $TEMPLATE
    [ -f $TEMPLATE ] && echo "Now execute: $PROG --sign to create cert file."
    exit 0
    ;;
-newkey|--newkey) 
    # create a private key
    [ -f $NEWKEY ] && die "Key file ($NEWKEY) already exists."
		$CERTTOOL --generate-privkey --outfile $NEWKEY
    echo "Private key is in $NEWKEY."
    exit 0
    ;;
-sign|--sign) 
    # sign a cert.
    [ -f $NEWCRT ] && die "Cert file ($NEWCRT) already exists."
		# $CERTTOOL --generate-certificate --load-privkey $NEWKEY  \
    #           --outfile $NEWCRT --load-ca-certificate $CACRT \
    #           --load-ca-privkey $CAKEY
    if [ -f $TEMPLATE ]; then
      $CERTTOOL --generate-certificate --load-privkey $NEWKEY  \
                --template $TEMPLATE --outfile $NEWCRT \
                --load-ca-certificate $CACRT --load-ca-privkey $CAKEY
      if [ $? == 0 ]; then
        update_serial
      fi
    else
      die "Generate a template file using: $PROG --newreq"
    fi
    echo "Cert is in $NEWCRT, private key is $NEWKEY"
    ;;
--verify) 
    echo "not implement yet."
   ;;
*)
    usage "Unknown arg $i";
    ;;
esac
shift
done



exit $RET

# vim: et ts=2 sw=2
