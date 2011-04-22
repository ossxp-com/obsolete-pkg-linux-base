
all:
	@echo "clean - remove *.deb and other temporary files."
	@echo "build - generate config files for current dists and run dpkg-buildpackage"

build:
	make -f debian/rules debian/control
	dpkg-buildpackage -b -rfakeroot

clean:
	-rm -f ../*changes ../*.deb 
	-rm -rf debian/build
	-sudo setfacl -Rb  ../debian

branch=master
name=ossxp-linux
version=5

rpm:tar
	rpmbuild --sign -ta $(name)-$(version).tar.gz

tar:
	git archive --prefix=$(name)-$(version)/ $(branch) | gzip > $(name)-$(version).tar.gz

dir: clean

.PHONY: all clean dir
# vim: noet

