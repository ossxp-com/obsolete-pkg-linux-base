<Directory /mnt.iso/>
	Options Indexes FollowSymLinks MultiViews
	AllowOverride None
	Order allow,deny
	allow from all
</Directory>

Alias         /debian-iso         "/mnt.iso/debian/"

<VirtualHost *:80>
    ServerAdmin noreply@moon.ossxp.com
    ServerName mirror.moon.ossxp.com
    ServerAlias mirrors.moon.ossxp.com
    ServerAlias mirrors.jx.bj.ossxp.com
    ServerAlias mirror.jx.bj.ossxp.com
    ServerAlias apt-source
    
		Include /etc/apache2/include/mirrors/apt-mirrors.inc
</VirtualHost>
