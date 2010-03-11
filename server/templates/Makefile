TOP_DIR=..

include $(TOP_DIR)/config.mk

CURRENT_INSTALL_DIR=$(DESTDIR)/$(PROJECTNAME)/templates
SUBDIRS=manager
TEMPLATES=$(wildcard *.html)

all: subdirs

install: create_dir install_templates install_subdirs

clean: clean_subdirs
	rm -f *~

include $(TOP_DIR)/targets.mk
