TOP_DIR=..

include $(TOP_DIR)/config.mk

CURRENT_INSTALL_DIR=$(DESTDIR)/$(PROJECTNAME)/css
FILES=$(wildcard *.css)

all:

install: create_dir install_files

clean:
	rm -f *~

include $(TOP_DIR)/targets.mk
