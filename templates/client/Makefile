TOP_DIR=../..

include $(TOP_DIR)/config.mk

CURRENT_INSTALL_DIR=$(INSTALL_DJANGO_DIR)/$(PROJECTNAME)/templates/client
TEMPLATES=$(wildcard *.html)
SUBDIRS=

all:

install: create_dir install_templates install_subdirs

clean:
	rm -f *.mo *~

include $(TOP_DIR)/targets.mk
