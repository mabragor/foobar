TOP_DIR=..

include $(TOP_DIR)/config.mk

CURRENT_INSTALL_DIR=$(DESTDIR)/$(PROJECTNAME)/media
SUBDIRS=
TEMPLATES=$(wildcard *.html)

all: subdirs

install: create_dir #install_templates install_subdirs
	cp -r extjs $(CURRENT_INSTALL_DIR)

clean: clean_subdirs
	rm -f *~

include $(TOP_DIR)/targets.mk
