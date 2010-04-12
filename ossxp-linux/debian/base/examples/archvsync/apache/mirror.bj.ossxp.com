<Directory /mnt.iso/>
	Options Indexes FollowSymLinks MultiViews
	AllowOverride None
	Order allow,deny
	allow from all
</Directory>

Alias         /debian-iso         "/mnt.iso/debian/"

<VirtualHost *:80>
    ServerAdmin noreply@bj.ossxp.com
    ServerName mirror.bj.ossxp.com
    ServerAlias mirrors.bj.ossxp.com
    ServerAlias apt-source

    ###################################################################
    DocumentRoot /data/_mirrors_/

    RedirectMatch ^/debian/(.*\.deb)$               http://ftp.us.debian.org/debian/$1
    RedirectMatch ^/debian-volatile/(.*\.deb)$      http://volatile.debian.org/debian-volatile/$1
    RedirectMatch ^/debian-security/(.*\.deb)$      http://security.debian.org/$1
    RedirectMatch ^/debian-multimedia/(.*\.deb)$    http://www.debian-multimedia.org/$1
    RedirectMatch ^/debian-backports/(.*\.deb)$     http://www.backports.org/debian/$1
    RedirectMatch ^/ubuntu/(.*\.deb)$               http://mirror.cs.umn.edu/ubuntu/$1

    ###################################################################
   	<Directory /data/_mirrors_>
		Options Indexes FollowSymLinks MultiViews
        IndexOptions NameWidth=* +SuppressDescription

		AllowOverride None
		Order allow,deny
        allow from all
	</Directory>
 
</VirtualHost>
