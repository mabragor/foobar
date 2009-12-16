APP_DIR=../..
TOP_DIR=$(APP_DIR)/..

include $(APP_DIR)/config.mk
include $(TOP_DIR)/config.mk

CURRENT_INSTALL_DIR=$(INSTALL_DJANGO_DIR)/$(PROJECTNAME)/$(APPNAME)/management/commands
SUBDIRS=
FILES=$(wildcard *.py)

all: subdirs

install: create_dir install_files

clean: clean_subdirs
	rm -f $(wildcard *.pyc) *~

include $(TOP_DIR)/targets.mk
