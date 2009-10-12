include config.mk

CURRENT_INSTALL_DIR=$(INSTALL_DJANGO_DIR)/$(PROJECTNAME)
FILES=$(wildcard *.py) $(wildcard *.wsgi)
SUBDIRS=js css media lib locale \
	client manager rfid storage templates

all: subdirs

help:
	echo "all        - compile objecs"; \
	echo "install    - install objects"; \
	echo "clean      - clean project"; \
	echo "dump       - make database dump"; \
	echo "translate  - prepare i18n"; \
	echo "postscript - create PS of code"; \
	echo "dbcreate   - create project's database"; \
	echo "dbdrop     - drop project's database"; 

install: create_dir install_files install_subdirs chown_all

clean: clean_subdirs
	rm -f $(wildcard *.pyc) *~; \
	find . -name '*.ps' -delete;

translate:
	mkdir -p ./locale
	for i in ru; do \
		django-admin.py makemessages --locale $$i; \
	done

postscript:
	for i in `find . -name '*.py' -size +0 | grep -v pyxslt`; do \
		in=$$i; out=`dirname $$i`/`basename $$i .py`.ps; \
		echo "$$in ===> $$out"; \
		cedilla -s 8 -fs cyrillic-courier -w \
			-h "foobar",,$$in" \
			-f "Page %p" $$in $$out; \
	done; \
	psmerge -o- `find . -name '*.ps' -size +0 | sort` | ps2pdf - code-dirty.pdf ; \
	pdfopt code-dirty.pdf code.pdf; \
	rm code-dirty.pdf

dbcreate:
	echo "CREATE USER $(PROJECTNAME)@localhost IDENTIFIED BY 'q1';" >> ./mysql.tmp; \
	echo "CREATE DATABASE $(PROJECTNAME);" >> ./mysql.tmp; \
	echo "GRANT ALL ON $(PROJECTNAME).* TO $(PROJECTNAME)@localhost;" >> ./mysql.tmp; \
	echo "\. ./mysql.tmp"; \
	mysql -u root -p; \
	rm -f ./mysql.tmp

dbdrop:
	echo "REVOKE ALL ON $(PROJECTNAME).* FROM $(PROJECTNAME)@localhost;" >> ./mysql.tmp
	echo "DROP DATABASE $(PROJECTNAME);" >> ./mysql.tmp
	echo "DROP USER $(PROJECTNAME)@localhost;" >> ./mysql.tmp
	echo "\. ./mysql.tmp"; \
	mysql -u root -p; \
	rm -f ./mysql.tmp

include targets.mk
