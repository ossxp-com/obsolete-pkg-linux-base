
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

dir: clean

.PHONY: all clean dir
# vim: noet

