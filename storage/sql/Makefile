TOP_DIR=../..
APP_DIR=..

include $(TOP_DIR)/config.mk
include $(APP_DIR)/config.mk

CURRENT_INSTALL_DIR=$(INSTALL_DJANGO_DIR)/$(PROJECTNAME)/$(APPNAME)/sql
SUBDIRS=
FILES=$(wildcard *.sql)

all: subdirs

install: create_dir install_files install_subdirs

fixtures:
	python $(TOP_DIR)/manage.py loaddata fixtures/initial_data.json

clean: clean_subdirs
	rm -f $(wildcard *.pyc) *~

include $(TOP_DIR)/targets.mk
