TOP_DIR=..

include $(TOP_DIR)/config.mk

CURRENT_INSTALL_DIR=$(DESTDIR)/$(PROJECTNAME)/static
SUBDIRS=farbtastic
TEMPLATES=$(wildcard *.html)

all: subdirs

install: create_dir install_dirs

clean: clean_subdirs
	rm -f *~

include $(TOP_DIR)/targets.mk
