TOP_DIR=../..

include $(TOP_DIR)/config.mk

CURRENT_INSTALL_DIR=$(DESTDIR)/$(PROJECTNAME)/templates/manager
TEMPLATES=$(wildcard *.html)
SUBDIRS=

all:

install: create_dir install_templates install_subdirs

clean:
	rm -f *.mo *~

include $(TOP_DIR)/targets.mk
