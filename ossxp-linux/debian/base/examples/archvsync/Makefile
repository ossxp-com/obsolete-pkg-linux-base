HOME=/home/debian
BIN=$(HOME)/bin
ETC=$(HOME)/etc

TARGETS=debian debian-security ubuntu debian-backports debian-multimedia debian-volatile

help:
	@echo "Targets: $(TARGETS)"
all: debian

$(TARGETS):
	$(BIN)/ftpsync sync:archive:$@ sync:stage1 || true
	$(BIN)/ftpsync sync:archive:$@ sync:stage2 || true

# vim: noet ts=4 sw=4
